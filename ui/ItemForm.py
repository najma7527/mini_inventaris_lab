from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.widgets import (
    Static, Button, Input, Select,
    Label, TextArea
)
from textual.screen import ModalScreen
from textual import on
from models.item import InventoryItem, timestamp_now

CATEGORIES = [
    "Perangkat Keras", "Perangkat Lunak",
    "Jaringan", "Lainnya"
]
CONDITIONS = ["Baik", "Perlu Perbaikan", "Rusak"]

class ItemForm(ModalScreen):
    CSS = """
    ItemForm {
        align: center middle;
    }

    #dialog {
        width: 76;
        max-width: 95%;
        height: 90%;
        max-height: 95%;
        border: round #4f8cff;
        background: #111827;
        padding: 1 2;
    }

    #form-content {
        height: 1fr;
        width: 100%;
        overflow-y: auto;
        scrollbar-gutter: stable;
    }

    .field-label {
        margin-top: 1;
        color: #bfdbfe;
    }

    Input, Select {
        width: 100%;
        margin-bottom: 1;
    }

    TextArea {
        width: 100%;
        height: 8;
        margin-bottom: 1;
    }

    #form-buttons {
        height: 3;
        align-horizontal: right;
    }

    #form-error {
        color: #fca5a5;
        height: auto;
    }
    """

    BINDINGS = [("escape", "dismiss(None)", "Batal")]

    def __init__(self, item: dict | None = None):
        super().__init__()
        self.item = item or {}

    def compose(self) -> ComposeResult:
        editing = bool(self.item)

        yield Container(
            Static(
                "UBAH DATA BARANG" if editing else "TAMBAH BARANG",
                id="form-title"
            ),

            ScrollableContainer(
                Label("Kode barang *", classes="field-label"),
                Input(
                    value=str(self.item.get("code", "")),
                    placeholder="Contoh: PC-001",
                    id="code"
                ),

                Label("Nama barang *", classes="field-label"),
                Input(
                    value=str(self.item.get("name", "")),
                    placeholder="Contoh: Komputer Lab 1",
                    id="name"
                ),

                Label("Kategori *", classes="field-label"),
                Select(
                    [(x, x) for x in CATEGORIES],
                    value=self.item.get("category", CATEGORIES[0]),
                    id="category"
                ),

                Label("Jumlah *", classes="field-label"),
                Input(
                    value=str(self.item.get("quantity", 1)),
                    placeholder="Jumlah unit",
                    id="quantity"
                ),

                Label("Kondisi *", classes="field-label"),
                Select(
                    [(x, x) for x in CONDITIONS],
                    value=self.item.get("condition", CONDITIONS[0]),
                    id="condition"
                ),

                Label("Lokasi *", classes="field-label"),
                Input(
                    value=str(self.item.get("location", "")),
                    placeholder="Contoh: Lab A / Rak 2",
                    id="location"
                ),

                Label("Catatan", classes="field-label"),
                TextArea(
                    self.item.get("notes", ""),
                    id="notes"
                ),

                id="form-content"
            ),

            Static("", id="form-error"),

            Horizontal(
                Button("Simpan", variant="primary", id="save"),
                Button("Batal", variant="default", id="cancel"),
                id="form-buttons"
            ),

            id="dialog"
        )

    @on(Button.Pressed, "#cancel")
    def cancel(self, event):
        self.dismiss(None)

    @on(Button.Pressed, "#save")
    def save(self, event):
        code = self.query_one("#code", Input).value.strip()
        name = self.query_one("#name", Input).value.strip()
        category = self.query_one("#category", Select).value
        quantity_text = self.query_one("#quantity", Input).value.strip()
        condition = self.query_one("#condition", Select).value
        location = self.query_one("#location", Input).value.strip()
        notes = self.query_one("#notes", TextArea).text.strip()

        error = ""

        if not code or not name or not location:
            error = "Kode, nama, dan lokasi wajib diisi."

        elif category is Select.BLANK or condition is Select.BLANK:
            error = "Pilih kategori dan kondisi barang."

        else:
            try:
                quantity = int(quantity_text)

                if quantity < 0:
                    error = "Jumlah tidak boleh negatif."

            except ValueError:
                error = "Jumlah harus berupa bilangan bulat."

        if error:
            self.query_one("#form-error", Static).update(error)
            return

        self.dismiss({
            "code": code,
            "name": name,
            "category": str(category),
            "quantity": quantity,
            "condition": str(condition),
            "location": location,
            "notes": notes,
            "updated_at": timestamp_now()
        })


