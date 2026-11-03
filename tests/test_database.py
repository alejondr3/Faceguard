import numpy as np

from faceguard.database import FaceDatabase


def test_add_and_match(tmp_path):
    database = FaceDatabase(tmp_path / "faces.db")
    database.add_embedding("Ana", np.array([1.0, 0.0, 0.0]), 0.8)
    database.add_embedding("Luis", np.array([0.0, 1.0, 0.0]), 0.7)

    name, score = database.best_match(np.array([0.99, 0.01, 0.0]), 0.4)

    assert name == "Ana"
    assert score > 0.99
    database.close()


def test_unknown_below_threshold(tmp_path):
    database = FaceDatabase(tmp_path / "faces.db")
    database.add_embedding("Ana", np.array([1.0, 0.0]), 0.8)
    assert database.best_match(np.array([0.0, 1.0]), 0.4)[0] is None


def test_backup_is_readable(tmp_path):
    database = FaceDatabase(tmp_path / "faces.db")
    database.add_embedding("Ana", np.array([1.0, 0.0]), 0.8)
    backup_path = database.backup(tmp_path / "backup.db")

    backup = FaceDatabase(backup_path)
    assert backup.summary() == [("Ana", 1)]
    backup.close()
    database.close()


