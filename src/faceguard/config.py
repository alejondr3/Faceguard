from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    database: Path = ROOT / "data" / "faces.db"
    photos_dir: Path = ROOT / "data" / "photos"
    recordings_dir: Path = ROOT / "data" / "recordings"
    models_dir: Path = ROOT / "models"
    match_threshold: float = 0.36
    detector_score_threshold: float = 0.75
    min_face_size: int = 55
    vote_window: int = 7
    votes_required: int = 4


