from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import (
     Static, Button
)
from textual.screen import ModalScreen
from textual import on
from models.item import timestamp_now

class ConfirmDelete(ModalScreen):
    CSS = """
    ConfirmDelete { align: center middle; }
    #confirm-box { width: 60; max-width: 90%; height: auto; border: round #ef4444; background: #111827; padding: 2; }
    #confirm-buttons { height: 3; align-horizontal: right; }
    """
    def __init__(self, item: dict):
        super().__init__()
        self.item = item

    def compose(self) -> ComposeResult:
        yield Container(
            Static("HAPUS DATA BARANG", classes="title"),
            Static(f"Yakin menghapus '{self.item['name']}' ({self.item['code']})?"),
            Static("Tindakan ini tidak dapat dibatalkan."),
            Horizontal(
                Button("Ya, hapus", variant="error", id="yes"),
                Button("Batal", id="no"),
                id="confirm-buttons"
            ),
            id="confirm-box"
        )

    @on(Button.Pressed, "#yes")
    def yes(self, event):
        self.dismiss(True)

    @on(Button.Pressed, "#no")
    def no(self, event):
        self.dismiss(False)

