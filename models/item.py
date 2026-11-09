from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class InventoryItem:
    id: int
    code: str
    name: str
    category: str
    quantity: int
    condition: str
    location: str
    notes: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=int(data["id"]),
            code=str(data["code"]),
            name=str(data["name"]),
            category=str(data["category"]),
            quantity=int(data["quantity"]),
            condition=str(data["condition"]),
            location=str(data["location"]),
            notes=str(data.get("notes", "")),
            updated_at=str(data.get("updated_at", "")),
        )


def timestamp_now() -> str:
    return datetime.now().isoformat(timespec="seconds")
