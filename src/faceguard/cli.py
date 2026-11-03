from __future__ import annotations

import argparse
import glob
import math
import re
import time
from datetime import datetime, timezone
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


def save_face_photo(frame, face, name: str, photos_dir: Path) -> Path:
    """Guarda un recorte facial válido como parte del dataset local."""
    safe_name = re.sub(r"[^\w.-]+", "_", name.strip(), flags=re.UNICODE).strip("._")
    if not safe_name:
        safe_name = "persona"
    person_dir = photos_dir / safe_name
    person_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    destination = person_dir / f"{timestamp}.jpg"
    crop = crop_face(frame, face, margin=0.25)
    if crop.size == 0:
        raise RuntimeError(f"No se pudo guardar la foto en {destination}")
    encoded, buffer = cv2.imencode(".jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 94])
    if not encoded:
        raise RuntimeError(f"No se pudo codificar la foto para {destination}")
    # imwrite puede fallar con rutas Unicode en algunas versiones de OpenCV/Windows.
    destination.write_bytes(buffer.tobytes())
    return destination


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
        if not args.no_save_photos:
            save_face_photo(prepared, face, args.name, args.photos_dir or settings.photos_dir)
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
                if not args.no_save_photos:
                    save_face_photo(
                        prepared, face, args.name, args.photos_dir or settings.photos_dir
                    )
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
    frame_number = 0
    next_track_id = 1
    tracks: dict[int, dict] = {}

    while True:
        ok, frame = camera.read()
        if not ok:
            continue
        prepared = enhance_frame(frame)
        faces = engine.detect(prepared)
        assigned_tracks: set[int] = set()
        for face in faces:
            x, y, width, height = map(int, face[:4])
            center = (x + width / 2, y + height / 2)
            candidates = [
                (math.dist(center, track["center"]), track_id)
                for track_id, track in tracks.items()
                if track_id not in assigned_tracks
            ]
            distance, track_id = min(candidates, default=(float("inf"), -1))
            if distance > max(width, height) * 0.8:
                track_id = next_track_id
                next_track_id += 1
                tracks[track_id] = {
                    "center": center,
                    "vote": TemporalVote(settings.vote_window, settings.votes_required),
                    "name": None,
                    "score": 0.0,
                    "seen": frame_number,
                }
            track = tracks[track_id]
            track["center"], track["seen"] = center, frame_number
            assigned_tracks.add(track_id)

            # En equipos lentos se puede calcular el embedding cada N cuadros.
            if frame_number % args.process_every == 0 and min(width, height) >= settings.min_face_size:
                candidate, score = database.best_match(
                    engine.embedding(prepared, face), args.threshold
                )
                track["name"] = track["vote"].update(candidate)
                track["score"] = score

            if track["name"]:
                label, color = f"{track['name']} ({track['score']:.2f})", (40, 220, 40)
            else:
                label, color = f"Desconocido ({track['score']:.2f})", (0, 80, 255)
            cv2.rectangle(prepared, (x, y), (x + width, y + height), color, 2)
            cv2.putText(prepared, label, (x, max(25, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        tracks = {
            track_id: track
            for track_id, track in tracks.items()
            if frame_number - track["seen"] <= 15
        }
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
    enroll_parser.add_argument("--photos-dir", type=Path)
    enroll_parser.add_argument(
        "--no-save-photos",
        action="store_true",
        help="Registrar embeddings sin conservar los recortes faciales",
    )

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


