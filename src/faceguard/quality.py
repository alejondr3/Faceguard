from __future__ import annotations

import cv2
import numpy as np


def enhance_frame(frame: np.ndarray, target_width: int = 960) -> np.ndarray:
    """Aumenta cuadros pequeños y mejora contraste local sin cambiar geometría."""
    height, width = frame.shape[:2]
    if width < target_width:
        scale = target_width / width
        frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)
    y = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(y)
    return cv2.cvtColor(cv2.merge((y, cr, cb)), cv2.COLOR_YCrCb2BGR)


def face_quality(face_crop: np.ndarray) -> float:
    """Puntaje 0..1 que combina tamaño, nitidez, luz y contraste."""
    if face_crop.size == 0:
        return 0.0
    gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    size_score = min(1.0, min(height, width) / 160.0)
    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    sharpness_score = min(1.0, blur / 180.0)
    mean = float(gray.mean())
    light_score = max(0.0, 1.0 - abs(mean - 130.0) / 130.0)
    contrast_score = min(1.0, float(gray.std()) / 55.0)
    return float(
        0.30 * size_score
        + 0.35 * sharpness_score
        + 0.20 * light_score
        + 0.15 * contrast_score
    )


