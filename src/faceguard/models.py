from __future__ import annotations

import urllib.request
from pathlib import Path

import cv2
import numpy as np


MODEL_URLS = {
    "face_detection_yunet_2023mar.onnx": (
        "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/"
        "face_detection_yunet_2023mar.onnx"
    ),
    "face_recognition_sface_2021dec.onnx": (
        "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/"
        "face_recognition_sface_2021dec.onnx"
    ),
}


def download_models(models_dir: Path) -> None:
    models_dir.mkdir(parents=True, exist_ok=True)
    for filename, url in MODEL_URLS.items():
        destination = models_dir / filename
        if destination.exists() and destination.stat().st_size > 100_000:
            continue
        temporary = destination.with_suffix(".part")
        print(f"Descargando {filename}...")
        urllib.request.urlretrieve(url, temporary)
        temporary.replace(destination)


class FaceEngine:
    def __init__(self, models_dir: Path, score_threshold: float = 0.75):
        download_models(models_dir)
        self.detector = cv2.FaceDetectorYN.create(
            str(models_dir / "face_detection_yunet_2023mar.onnx"),
            "",
            (320, 320),
            score_threshold,
            0.3,
            5000,
        )
        self.recognizer = cv2.FaceRecognizerSF.create(
            str(models_dir / "face_recognition_sface_2021dec.onnx"), ""
        )

    def detect(self, frame: np.ndarray) -> list[np.ndarray]:
        height, width = frame.shape[:2]
        self.detector.setInputSize((width, height))
        _result, faces = self.detector.detect(frame)
        if faces is None:
            return []
        return sorted(faces, key=lambda face: float(face[2] * face[3]), reverse=True)

    def embedding(self, frame: np.ndarray, face: np.ndarray) -> np.ndarray:
        aligned = self.recognizer.alignCrop(frame, face)
        return self.recognizer.feature(aligned).reshape(-1).astype(np.float32)


def crop_face(frame: np.ndarray, face: np.ndarray, margin: float = 0.12) -> np.ndarray:
    x, y, width, height = face[:4]
    pad_x, pad_y = width * margin, height * margin
    x1, y1 = max(0, int(x - pad_x)), max(0, int(y - pad_y))
    x2 = min(frame.shape[1], int(x + width + pad_x))
    y2 = min(frame.shape[0], int(y + height + pad_y))
    return frame[y1:y2, x1:x2]


