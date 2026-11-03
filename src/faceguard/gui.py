from __future__ import annotations

import threading
import time
import tkinter as tk
import zipfile
from tempfile import TemporaryDirectory
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import cv2
from PIL import Image, ImageTk

from .cli import camera_source, save_face_photo
from .config import Settings
from .database import FaceDatabase
from .models import FaceEngine, crop_face
from .quality import enhance_frame, face_quality


class FaceGuardApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.settings = Settings()
        self.database = FaceDatabase(self.settings.database)
        self.engine: FaceEngine | None = None
        self.camera: cv2.VideoCapture | None = None
        self.mode: str | None = None
        self.running = False
        self.loop_id = 0
        self.frame_number = 0
        self.collected = 0
        self.last_capture = 0.0
        self.cached_labels: list[tuple[str | None, float]] = []
        self.video_writer: cv2.VideoWriter | None = None
        self.recording_path: Path | None = None
        self.photo_image = None

        self.root.title("Reconocedor de caras")
        self.root.geometry("1120x720")
        self.root.minsize(900, 620)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self._build_interface()

    def _build_interface(self) -> None:
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
        style.configure("Action.TButton", font=("Segoe UI", 12, "bold"), padding=10)
        style.configure("TLabel", font=("Segoe UI", 10))

        header = ttk.Frame(self.root, padding=(20, 14))
        header.pack(fill="x")
        ttk.Label(header, text="Reconocedor de caras", style="Title.TLabel").pack(side="left")
        self.status = tk.StringVar(value="Listo. Elige una acción.")
        ttk.Label(header, textvariable=self.status).pack(side="right", padx=10)

        body = ttk.Frame(self.root, padding=(20, 0, 20, 20))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        video_frame = ttk.Frame(body, relief="solid", borderwidth=1)
        video_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        self.video = ttk.Label(
            video_frame,
            text="La vista de la cámara aparecerá aquí",
            anchor="center",
            font=("Segoe UI", 15),
        )
        self.video.pack(fill="both", expand=True)

        controls = ttk.Frame(body, width=280)
        controls.grid(row=0, column=1, sticky="ns")

        ttk.Label(controls, text="Registrar una persona", font=("Segoe UI", 14, "bold")).pack(
            anchor="w", pady=(0, 10)
        )
        ttk.Label(controls, text="Nombre completo").pack(anchor="w")
        self.name = tk.StringVar()
        ttk.Entry(controls, textvariable=self.name, width=32, font=("Segoe UI", 11)).pack(
            fill="x", pady=(4, 12)
        )

        row = ttk.Frame(controls)
        row.pack(fill="x", pady=(0, 14))
        ttk.Label(row, text="Cámara (0 o URL RTSP)").grid(row=0, column=0, columnspan=2, sticky="w")
        self.camera_number = tk.StringVar(value="0")
        self.samples = tk.IntVar(value=30)
        ttk.Entry(row, textvariable=self.camera_number, width=32).grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(4, 10)
        )
        ttk.Label(row, text="Cantidad de fotos").grid(row=2, column=0, sticky="w")
        ttk.Spinbox(row, from_=10, to=100, textvariable=self.samples, width=7).grid(
            row=3, column=0, sticky="w", pady=4
        )
        ttk.Label(
            controls,
            text="Usa 0 para webcam o pega una URL RTSP para una cámara de seguridad.",
            wraplength=270,
        ).pack(anchor="w", pady=(0, 10))
        self.record_video = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            controls,
            text="Grabar reconocimiento en video",
            variable=self.record_video,
        ).pack(anchor="w", pady=(0, 12))

        self.enroll_button = ttk.Button(
            controls, text="📷  Registrar persona", style="Action.TButton", command=self.start_enrollment
        )
        self.enroll_button.pack(fill="x", pady=5)
        self.recognize_button = ttk.Button(
            controls, text="▶  Iniciar reconocimiento", style="Action.TButton", command=self.start_recognition
        )
        self.recognize_button.pack(fill="x", pady=5)
        self.stop_button = ttk.Button(
            controls, text="■  Detener cámara", style="Action.TButton", command=self.stop_camera
        )
        self.stop_button.pack(fill="x", pady=5)

        ttk.Separator(controls).pack(fill="x", pady=20)
        ttk.Label(controls, text="Personas registradas", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", pady=(0, 7)
        )
        self.people = tk.StringVar(value="Todavía no hay registros")
        ttk.Label(controls, textvariable=self.people, wraplength=260, justify="left").pack(anchor="w")
        ttk.Button(controls, text="Actualizar lista", command=self.refresh_people).pack(
            fill="x", pady=(10, 0)
        )
        ttk.Button(controls, text="💾  Crear respaldo", command=self.create_backup).pack(
            fill="x", pady=(8, 0)
        )
        ttk.Button(controls, text="🗑  Eliminar base de datos", command=self.delete_database).pack(
            fill="x", pady=(8, 0)
        )
        self.refresh_people()

    def _set_buttons(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.enroll_button.configure(state=state)
        self.recognize_button.configure(state=state)

    def _load_engine(self, callback) -> None:
        if self.engine is not None:
            callback()
            return
        self.status.set("Preparando modelos por primera vez…")
        self._set_buttons(False)

        def worker():
            try:
                engine = FaceEngine(self.settings.models_dir, self.settings.detector_score_threshold)
                self.root.after(0, lambda: self._engine_ready(engine, callback))
            except Exception as error:
                self.root.after(0, lambda: self._show_error("No se pudieron preparar los modelos", error))

        threading.Thread(target=worker, daemon=True).start()

    def _engine_ready(self, engine: FaceEngine, callback) -> None:
        self.engine = engine
        self._set_buttons(True)
        callback()

    def _show_error(self, title: str, error: Exception) -> None:
        self._set_buttons(True)
        self.status.set("Ocurrió un error.")
        messagebox.showerror(title, str(error))

    def _open_camera(self) -> bool:
        self.stop_camera(clear_status=False)
        source = camera_source(self.camera_number.get().strip() or "0")
        self.camera = cv2.VideoCapture(source)
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        if not self.camera.isOpened():
            self.camera.release()
            self.camera = None
            messagebox.showerror("Cámara", f"No se pudo abrir la cámara {source}.")
            return False
        self.running = True
        self.loop_id += 1
        loop_id = self.loop_id
        self.frame_number = 0
        self.cached_labels = []
        self.root.after(1, lambda: self._tick(loop_id))
        return True

    def start_enrollment(self) -> None:
        person = self.name.get().strip()
        if not person:
            messagebox.showwarning("Falta el nombre", "Escribe el nombre de la persona.")
            return
        self._load_engine(self._begin_enrollment)

    def _begin_enrollment(self) -> None:
        if self._open_camera():
            self.mode = "enroll"
            self.collected = 0
            self.last_capture = 0.0
            self.status.set("Mira al frente y gira lentamente la cabeza.")

    def start_recognition(self) -> None:
        if not self.database.all_embeddings():
            messagebox.showinfo("Sin personas", "Primero registra al menos una persona.")
            return
        self._load_engine(self._begin_recognition)

    def _begin_recognition(self) -> None:
        if self._open_camera():
            self.mode = "recognize"
            self.status.set("Reconocimiento activo")

    def _tick(self, loop_id: int) -> None:
        if loop_id != self.loop_id or not self.running or self.camera is None or self.engine is None:
            return
        ok, frame = self.camera.read()
        if not ok:
            self.root.after(30, lambda: self._tick(loop_id))
            return
        prepared = enhance_frame(frame)
        faces = self.engine.detect(prepared)

        if self.mode == "enroll":
            self._process_enrollment(prepared, faces)
        elif self.mode == "recognize":
            self._process_recognition(prepared, faces)

        rgb = cv2.cvtColor(prepared, cv2.COLOR_BGR2RGB)
        if self.mode == "recognize" and self.record_video.get():
            self._write_recording(prepared)
        image = Image.fromarray(rgb)
        image.thumbnail((780, 600), Image.Resampling.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(image=image)
        self.video.configure(image=self.photo_image, text="")
        self.frame_number += 1
        self.root.after(15, lambda: self._tick(loop_id))

    def _process_enrollment(self, frame, faces) -> None:
        target = self.samples.get()
        message = "Debe verse exactamente una cara"
        if len(faces) == 1:
            face = faces[0]
            quality = face_quality(crop_face(frame, face))
            message = f"Calidad {quality:.2f} · Fotos {self.collected}/{target}"
            now = time.monotonic()
            if quality >= 0.35 and now - self.last_capture >= 0.35:
                self.database.add_embedding(
                    self.name.get().strip(), self.engine.embedding(frame, face), quality
                )
                save_face_photo(
                    frame, face, self.name.get().strip(), self.settings.photos_dir
                )
                self.collected += 1
                self.last_capture = now
            x, y, width, height = map(int, face[:4])
            cv2.rectangle(frame, (x, y), (x + width, y + height), (40, 220, 40), 2)
        cv2.putText(frame, message, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (40, 220, 40), 2)
        self.status.set(message)
        if self.collected >= target:
            person = self.name.get().strip()
            self.stop_camera(clear_status=False)
            self.status.set(f"Registro terminado: {person}")
            self.refresh_people()
            messagebox.showinfo("Registro terminado", f"Se guardaron {target} fotos de {person}.")

    def _process_recognition(self, frame, faces) -> None:
        if self.frame_number % 3 == 0:
            self.cached_labels = []
            for face in faces:
                if min(face[2], face[3]) >= self.settings.min_face_size:
                    self.cached_labels.append(
                        self.database.best_match(
                            self.engine.embedding(frame, face), self.settings.match_threshold
                        )
                    )
                else:
                    self.cached_labels.append((None, 0.0))

        for index, face in enumerate(faces):
            name, score = (
                self.cached_labels[index] if index < len(self.cached_labels) else (None, 0.0)
            )
            x, y, width, height = map(int, face[:4])
            color = (40, 220, 40) if name else (0, 80, 255)
            label = f"{name} ({score:.2f})" if name else "Desconocido"
            cv2.rectangle(frame, (x, y), (x + width, y + height), color, 2)
            cv2.putText(frame, label, (x, max(25, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    def _write_recording(self, frame) -> None:
        if self.video_writer is None:
            self.settings.recordings_dir.mkdir(parents=True, exist_ok=True)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            self.recording_path = self.settings.recordings_dir / f"reconocimiento-{timestamp}.mp4"
            height, width = frame.shape[:2]
            fps = self.camera.get(cv2.CAP_PROP_FPS) if self.camera is not None else 0
            if not fps or fps < 1 or fps > 120:
                fps = 20.0
            self.video_writer = cv2.VideoWriter(
                str(self.recording_path),
                cv2.VideoWriter_fourcc(*"mp4v"),
                fps,
                (width, height),
            )
            if not self.video_writer.isOpened():
                self.video_writer.release()
                self.video_writer = None
                self.record_video.set(False)
                messagebox.showerror("Grabación", "No se pudo crear el archivo de video.")
                return
        self.video_writer.write(frame)

    def stop_camera(self, clear_status: bool = True) -> None:
        saved_recording = None
        self.running = False
        self.loop_id += 1
        self.mode = None
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
            if self.recording_path is not None:
                saved_recording = self.recording_path.name
            self.recording_path = None
        if clear_status:
            self.status.set(
                f"Video guardado: {saved_recording}" if saved_recording else "Cámara detenida"
            )

    def refresh_people(self) -> None:
        records = self.database.summary()
        self.people.set(
            "\n".join(f"• {name}: {count} fotos" for name, count in records)
            if records
            else "Todavía no hay registros"
        )

    def create_backup(self) -> None:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        selected = filedialog.asksaveasfilename(
            title="Guardar respaldo completo",
            defaultextension=".zip",
            initialfile=f"respaldo-caras-{timestamp}.zip",
            filetypes=[("Archivo ZIP", "*.zip")],
        )
        if not selected:
            return
        destination = Path(selected)
        try:
            with TemporaryDirectory() as temporary:
                database_copy = self.database.backup(Path(temporary) / "faces.db")
                with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
                    archive.write(database_copy, "data/faces.db")
                    if self.settings.photos_dir.exists():
                        for photo in self.settings.photos_dir.rglob("*"):
                            if photo.is_file() and photo.resolve() != destination.resolve():
                                relative = photo.relative_to(self.settings.photos_dir)
                                archive.write(photo, Path("data/photos") / relative)
            self.status.set(f"Respaldo creado: {destination.name}")
            messagebox.showinfo(
                "Respaldo terminado",
                f"Se guardaron la base SQLite y las fotografías en:\n{destination}",
            )
        except Exception as error:
            self._show_error("No se pudo crear el respaldo", error)

    def delete_database(self) -> None:
        if not self.database.summary():
            messagebox.showinfo("Base vacía", "La base de datos ya está vacía.")
            return
        confirmed = messagebox.askyesno(
            "Eliminar base de datos",
            "Se eliminarán permanentemente todas las personas y embeddings.\n\n"
            "Las fotografías se conservarán en data/photos.\n"
            "Se recomienda crear un respaldo antes.\n\n"
            "¿Quieres continuar?",
            icon="warning",
        )
        if not confirmed:
            return
        final_confirmation = messagebox.askyesno(
            "Última confirmación",
            "Esta acción no se puede deshacer sin un respaldo.\n\n"
            "¿Eliminar toda la base SQLite?",
            icon="warning",
        )
        if not final_confirmation:
            return
        try:
            self.stop_camera(clear_status=False)
            database_path = self.database.path
            self.database.close()
            for path in (
                database_path,
                database_path.with_name(database_path.name + "-wal"),
                database_path.with_name(database_path.name + "-shm"),
            ):
                path.unlink(missing_ok=True)
            self.database = FaceDatabase(database_path)
            self.refresh_people()
            self.status.set("Base de datos eliminada; se creó una base vacía")
            messagebox.showinfo(
                "Base eliminada",
                "Se eliminaron las identidades y se creó una base SQLite vacía.\n"
                "Las fotografías no fueron eliminadas.",
            )
        except Exception as error:
            # Intenta dejar la aplicación utilizable incluso si falló el borrado.
            self.database = FaceDatabase(self.settings.database)
            self._show_error("No se pudo eliminar la base de datos", error)

    def close(self) -> None:
        self.stop_camera(clear_status=False)
        self.database.close()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    FaceGuardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()


