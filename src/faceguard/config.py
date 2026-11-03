from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    database: Path = ROOT / "data" / "faces.db"
    models_dir: Path = ROOT / "models"
    match_threshold: float = 0.40
    detector_score_threshold: float = 0.75
    min_face_size: int = 55
    vote_window: int = 7
    votes_required: int = 4


