from abc import ABC, abstractmethod
import json
import os
import time


CURRENT_SCHEMA_VERSION = 1


class Saver(ABC):
    @abstractmethod
    def save(self, data: dict) -> None:
        ...

    @abstractmethod
    def load(self) -> dict | None:
        ...

    @abstractmethod
    def delete(self) -> None:
        ...


def new_save_data() -> dict:
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "created_at": now,
        "updated_at": now,
        "player": {"name": "", "xp": 0, "hp": 3, "max_hp": 5, "currency": {}},
        "progression": {"unlocked_levels": [1], "completed_levels": {}, "stars": {}},
        "settings": {"theme": "default", "font_size": 12},
    }


def migrate(data: dict) -> dict:
    version = data.get("schema_version", 0)
    while version < CURRENT_SCHEMA_VERSION:
        version += 1
        migrate_fn = _MIGRATIONS.get(version)
        if migrate_fn:
            data = migrate_fn(data)
        data["schema_version"] = version
    return data


_MIGRATIONS: dict[int, callable] = {}


class JsonSaver(Saver):
    def __init__(self, path: str):
        self.path = path

    def save(self, data: dict) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, self.path)

    def load(self) -> dict | None:
        if not os.path.exists(self.path):
            return None
        try:
            with open(self.path) as f:
                data = json.load(f)
            if data.get("schema_version", 0) < CURRENT_SCHEMA_VERSION:
                data = migrate(data)
            return data
        except (OSError, json.JSONDecodeError):
            return None

    def delete(self) -> None:
        if os.path.exists(self.path):
            os.remove(self.path)
