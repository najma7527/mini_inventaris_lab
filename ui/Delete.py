from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, Button
from textual.screen import ModalScreen
from textual import on


class ConfirmDelete(ModalScreen):
    CSS = """
    ConfirmDelete { align: center middle; }
    #confirm-box { width: 64; max-width: 92%; height: auto; border: round #ef4444; background: #111827; padding: 2; }
    #confirm-buttons { height: 3; align-horizontal: right; }
    """

    def __init__(self, title: str, description: str):
        super().__init__()
        self.title = title
        self.description = description

    def compose(self) -> ComposeResult:
        yield Container(
            Static(self.title, classes="title"),
            Static(self.description),
            Static("Tindakan ini tidak dapat dibatalkan.", id="warning"),
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

