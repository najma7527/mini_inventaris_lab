from abc import ABC, abstractmethod


class InventoryStorage(ABC):
    @abstractmethod
    def list_items(self) -> list[dict]: ...

    @abstractmethod
    def add_item(self, item: dict) -> dict: ...

    @abstractmethod
    def update_item(self, item_id: int, item: dict) -> bool: ...

    @abstractmethod
    def delete_item(self, item_id: int) -> bool: ...

    @abstractmethod
    def close(self) -> None: ...
