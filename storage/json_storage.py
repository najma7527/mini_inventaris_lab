import json
from pathlib import Path
from threading import RLock
from storage.base import InventoryStorage


class JsonInventoryStorage(InventoryStorage):
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        if not self.file_path.exists():
            self._write({"next_id": 1, "items": []})
        self._read()  # validasi awal

    def _read(self) -> dict:
        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict) or not isinstance(data.get("items"), list):
                raise ValueError("Format file JSON tidak sesuai.")
            data.setdefault("next_id", 1)
            return data
        except json.JSONDecodeError as exc:
            raise ValueError(f"File JSON rusak: {exc}") from exc

    def _write(self, data: dict) -> None:
        temp = self.file_path.with_suffix(self.file_path.suffix + ".tmp")
        with temp.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        temp.replace(self.file_path)

    def list_items(self) -> list[dict]:
        with self._lock:
            return sorted(self._read()["items"], key=lambda x: x["id"])

    def add_item(self, item: dict) -> dict:
        with self._lock:
            data = self._read()
            item = dict(item)
            item["id"] = int(data["next_id"])
            data["next_id"] = item["id"] + 1
            data["items"].append(item)
            self._write(data)
            return item

    def update_item(self, item_id: int, item: dict) -> bool:
        with self._lock:
            data = self._read()
            for index, existing in enumerate(data["items"]):
                if int(existing["id"]) == int(item_id):
                    updated = dict(item)
                    updated["id"] = int(item_id)
                    data["items"][index] = updated
                    self._write(data)
                    return True
            return False

    def delete_item(self, item_id: int) -> bool:
        with self._lock:
            data = self._read()
            old_length = len(data["items"])
            data["items"] = [x for x in data["items"] if int(x["id"]) != int(item_id)]
            if len(data["items"]) == old_length:
                return False
            self._write(data)
            return True

    def close(self) -> None:
        pass
