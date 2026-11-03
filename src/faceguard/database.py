from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS persons (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS embeddings (
    id INTEGER PRIMARY KEY,
    person_id INTEGER NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    vector BLOB NOT NULL,
    quality REAL NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_embeddings_person ON embeddings(person_id);
"""


class FaceDatabase:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript(SCHEMA)

    def close(self) -> None:
        self.connection.close()

    def backup(self, destination: str | Path) -> Path:
        """Crea una copia SQLite consistente incluso si la aplicación está abierta."""
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        target = sqlite3.connect(destination)
        try:
            self.connection.backup(target)
        finally:
            target.close()
        return destination

    def import_database(self, source_path: str | Path) -> tuple[int, int, int]:
        """Combina otra base FaceGuard y devuelve personas, embeddings y omitidos."""
        source_path = Path(source_path).resolve()
        if source_path == self.path.resolve():
            raise ValueError("La base seleccionada ya es la base activa")
        if not source_path.is_file():
            raise ValueError("El archivo SQLite seleccionado no existe")

        source = sqlite3.connect(f"file:{source_path.as_posix()}?mode=ro", uri=True)
        try:
            tables = {
                row[0]
                for row in source.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
            if not {"persons", "embeddings"}.issubset(tables):
                raise ValueError(
                    "La base no es compatible: faltan las tablas persons o embeddings"
                )
            person_columns = {
                row[1] for row in source.execute("PRAGMA table_info(persons)").fetchall()
            }
            embedding_columns = {
                row[1] for row in source.execute("PRAGMA table_info(embeddings)").fetchall()
            }
            if not {"id", "name"}.issubset(person_columns) or not {
                "person_id",
                "vector",
                "quality",
            }.issubset(embedding_columns):
                raise ValueError("La estructura de la base SQLite no es compatible")
            rows = source.execute(
                """SELECT p.name, e.vector, e.quality
                   FROM embeddings e JOIN persons p ON p.id = e.person_id"""
            ).fetchall()
        finally:
            source.close()

        current = self.all_embeddings()
        # SFace produce vectores float32 de 128 dimensiones (512 bytes).
        expected_size = current[0][1].nbytes if current else 128 * 4
        existing = {(name, vector.tobytes()) for name, vector, _quality in current}
        existing_people = {name for name, _count in self.summary()}
        people_added = 0
        embeddings_added = 0
        skipped = 0
        now = datetime.now(timezone.utc).isoformat()

        try:
            for name, blob, quality in rows:
                if not isinstance(name, str) or not name.strip():
                    skipped += 1
                    continue
                if not isinstance(blob, bytes) or not blob or len(blob) % 4:
                    raise ValueError(f"Embedding inválido para {name}")
                if len(blob) != expected_size:
                    raise ValueError(
                        f"Los embeddings de {name} no usan SFace o tienen otra dimensión"
                    )
                name = name.strip()
                key = (name, blob)
                if key in existing:
                    skipped += 1
                    continue
                if name not in existing_people:
                    self.connection.execute(
                        "INSERT INTO persons(name, created_at) VALUES (?, ?)", (name, now)
                    )
                    existing_people.add(name)
                    people_added += 1
                person_id = self.connection.execute(
                    "SELECT id FROM persons WHERE name = ?", (name,)
                ).fetchone()[0]
                self.connection.execute(
                    "INSERT INTO embeddings(person_id, vector, quality, created_at) VALUES (?, ?, ?, ?)",
                    (person_id, blob, float(quality), now),
                )
                existing.add(key)
                embeddings_added += 1
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        return people_added, embeddings_added, skipped

    def add_embedding(self, name: str, vector: np.ndarray, quality: float) -> None:
        name = name.strip()
        if not name:
            raise ValueError("El nombre no puede estar vacío")
        now = datetime.now(timezone.utc).isoformat()
        self.connection.execute(
            "INSERT OR IGNORE INTO persons(name, created_at) VALUES (?, ?)", (name, now)
        )
        person_id = self.connection.execute(
            "SELECT id FROM persons WHERE name = ?", (name,)
        ).fetchone()[0]
        normalized = normalize(vector).astype(np.float32)
        self.connection.execute(
            "INSERT INTO embeddings(person_id, vector, quality, created_at) VALUES (?, ?, ?, ?)",
            (person_id, normalized.tobytes(), float(quality), now),
        )
        self.connection.commit()

    def all_embeddings(self) -> list[tuple[str, np.ndarray, float]]:
        rows = self.connection.execute(
            """SELECT p.name, e.vector, e.quality
               FROM embeddings e JOIN persons p ON p.id = e.person_id"""
        ).fetchall()
        return [
            (name, np.frombuffer(blob, dtype=np.float32).copy(), float(quality))
            for name, blob, quality in rows
        ]

    def summary(self) -> list[tuple[str, int]]:
        return self.connection.execute(
            """SELECT p.name, COUNT(e.id) FROM persons p
               LEFT JOIN embeddings e ON e.person_id = p.id
               GROUP BY p.id ORDER BY p.name"""
        ).fetchall()

    def delete_person(self, name: str) -> bool:
        cursor = self.connection.execute("DELETE FROM persons WHERE name = ?", (name,))
        self.connection.commit()
        return cursor.rowcount > 0

    def best_match(self, query: np.ndarray, threshold: float) -> tuple[str | None, float]:
        query = normalize(query)
        by_person: dict[str, list[float]] = {}
        for name, vector, _quality in self.all_embeddings():
            by_person.setdefault(name, []).append(float(np.dot(query, normalize(vector))))
        if not by_person:
            return None, 0.0

        # El promedio de los 3 mejores ejemplos tolera cambios de luz sin dejar que
        # una única captura accidental decida la identidad.
        scores = {
            name: float(np.mean(sorted(values, reverse=True)[:3]))
            for name, values in by_person.items()
        }
        name, score = max(scores.items(), key=lambda item: item[1])
        return (name, score) if score >= threshold else (None, score)


def normalize(vector: np.ndarray) -> np.ndarray:
    flat = np.asarray(vector, dtype=np.float32).reshape(-1)
    norm = float(np.linalg.norm(flat))
    return flat / max(norm, 1e-12)


