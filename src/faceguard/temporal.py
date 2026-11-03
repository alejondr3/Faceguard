from __future__ import annotations

from collections import Counter, deque


class TemporalVote:
    def __init__(self, window: int = 7, required: int = 4):
        if required > window:
            raise ValueError("required no puede ser mayor que window")
        self.values: deque[str | None] = deque(maxlen=window)
        self.required = required

    def update(self, identity: str | None) -> str | None:
        self.values.append(identity)
        known = [value for value in self.values if value is not None]
        if not known:
            return None
        identity, count = Counter(known).most_common(1)[0]
        return identity if count >= self.required else None


