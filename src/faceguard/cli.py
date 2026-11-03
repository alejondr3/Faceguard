from __future__ import annotations

import argparse
import glob
import time
from pathlib import Path

import cv2

from .config import Settings
from .database import FaceDatabase
from .models import FaceEngine, crop_face
from .quality import enhance_frame, face_quality
from .temporal import TemporalVote


def camera_source(value: str):
    return int(value) if value.isdigit() else value


def open_camera(source):
    camera = cv2.VideoCapture(source)
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    if not camera.isOpened():
        raise RuntimeError(f"No se pudo abrir la cámara o stream: {source}")
    return camera


def enroll(args, settings: Settings) -> None:
    database = FaceDatabase(args.database or settings.database)
    engine = FaceEngine(settings.models_dir, settings.detector_score_threshold)
    collected = 0

    def accept(frame) -> bool:
        nonlocal collected
        prepared = enhance_frame(frame)
        faces = engine.detect(prepared)
        if len(faces) != 1:
            return False
        face = faces[0]
        if min(face[2], face[3]) < settings.min_face_size:
            return False
        quality = face_quality(crop_face(prepared, face))
        if quality < args.min_quality:
            return False
        vector = engine.embedding(prepared, face)
        database.add_embedding(args.name, vector, quality)
        collected += 1
        return True

    if args.images:
        paths = []
        for pattern in args.images:
            paths.extend(Path(path) for path in glob.glob(pattern))
        for path in paths:
            image = cv2.imread(str(path))
            if image is not None:
                accept(image)
        print(f"Registradas {collected} muestras válidas para {args.name}.")
        database.close()
        return

    camera = open_camera(camera_source(args.camera))
    last_capture = 0.0
    print("Mira al frente y gira lentamente. Pulsa Q para cancelar.")
    while collected < args.samples:
        ok, frame = camera.read()
        if not ok:
            continue
        prepared = enhance_frame(frame)
        faces = engine.detect(prepared)
        status = "Debe verse exactamente una cara"
        if len(faces) == 1:
            face = faces[0]
            quality = face_quality(crop_face(prepared, face))
            status = f"calidad {quality:.2f} | muestras {collected}/{args.samples}"
            now = time.monotonic()
            if quality >= args.min_quality and now - last_capture >= 0.35:
                database.add_embedding(args.name, engine.embedding(prepared, face), quality)
                collected += 1
                last_capture = now
        cv2.putText(prepared, status, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        cv2.imshow("Registro - Q para salir", prepared)
        if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
            break
    camera.release()
    cv2.destroyAllWindows()
    database.close()
    print(f"Registradas {collected} muestras válidas para {args.name}.")


def recognize(args, settings: Settings) -> None:
    database = FaceDatabase(args.database or settings.database)
    if not database.all_embeddings():
        raise RuntimeError("La base está vacía. Primero ejecuta: faceguard enroll --name NOMBRE")
    engine = FaceEngine(settings.models_dir, settings.detector_score_threshold)
    camera = open_camera(camera_source(args.camera))
    vote = TemporalVote(settings.vote_window, settings.votes_required)
    frame_number = 0
    cached = (None, 0.0)

    while True:
        ok, frame = camera.read()
        if not ok:
            continue
        prepared = enhance_frame(frame)
        faces = engine.detect(prepared)
        # En equipos lentos se puede calcular el embedding cada N cuadros.
        if faces and frame_number % args.process_every == 0:
            main_face = faces[0]
            if min(main_face[2], main_face[3]) >= settings.min_face_size:
                cached = database.best_match(
                    engine.embedding(prepared, main_face), args.threshold
                )
        stable_name = vote.update(cached[0] if faces else None)
        for index, face in enumerate(faces):
            x, y, width, height = map(int, face[:4])
            if index == 0 and stable_name:
                label, color = f"{stable_name} ({cached[1]:.2f})", (40, 220, 40)
            else:
                label, color = f"Desconocido ({cached[1]:.2f})", (0, 80, 255)
            cv2.rectangle(prepared, (x, y), (x + width, y + height), color, 2)
            cv2.putText(prepared, label, (x, max(25, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.imshow("Reconocimiento - Q para salir", prepared)
        frame_number += 1
        if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
            break
    camera.release()
    cv2.destroyAllWindows()
    database.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="faceguard", description="Reconocimiento facial local")
    sub = parser.add_subparsers(dest="command", required=True)

    download = sub.add_parser("download-models", help="Descargar modelos ONNX")

    enroll_parser = sub.add_parser("enroll", help="Registrar una persona")
    enroll_parser.add_argument("--name", required=True)
    enroll_parser.add_argument("--camera", default="0", help="Índice, archivo o URL RTSP")
    enroll_parser.add_argument("--images", nargs="+", help="Patrones de imágenes, ej. fotos/ana/*.jpg")
    enroll_parser.add_argument("--samples", type=int, default=20)
    enroll_parser.add_argument("--min-quality", type=float, default=0.35)
    enroll_parser.add_argument("--database", type=Path)

    recognize_parser = sub.add_parser("recognize", help="Reconocer en tiempo real")
    recognize_parser.add_argument("--camera", default="0", help="Índice, archivo o URL RTSP")
    recognize_parser.add_argument("--threshold", type=float, default=0.40)
    recognize_parser.add_argument("--process-every", type=int, default=2)
    recognize_parser.add_argument("--database", type=Path)

    list_parser = sub.add_parser("list", help="Listar personas registradas")
    list_parser.add_argument("--database", type=Path)
    delete_parser = sub.add_parser("delete", help="Eliminar una persona y sus embeddings")
    delete_parser.add_argument("--name", required=True)
    delete_parser.add_argument("--database", type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings()
    if args.command == "download-models":
        from .models import download_models
        download_models(settings.models_dir)
    elif args.command == "enroll":
        enroll(args, settings)
    elif args.command == "recognize":
        recognize(args, settings)
    elif args.command == "list":
        database = FaceDatabase(args.database or settings.database)
        for name, count in database.summary():
            print(f"{name}: {count} muestras")
        database.close()
    elif args.command == "delete":
        database = FaceDatabase(args.database or settings.database)
        print("Eliminado." if database.delete_person(args.name) else "No encontrado.")
        database.close()


if __name__ == "__main__":
    main()


