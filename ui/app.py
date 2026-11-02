from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Static, Button, DataTable, Input, Select,
    Label, TextArea, Rule
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


class InventoryApp(App):
    TITLE = "Lab Inventory"
    SUB_TITLE = "Manajemen Inventaris Laboratorium Komputer"
    CSS = """
    Screen { background: #0b1220; }
    #top-summary { height: auto; padding: 1 2; background: #17243a; border: round #263b59; margin: 1 2; }
    #summary-line { color: #bfdbfe; }
    #toolbar { height: 3; margin: 0 2 1 2; }
    #search { width: 1fr; }
    #table-wrap { height: 1fr; margin: 0 2; border: round #263b59; }
    DataTable { height: 1fr; }
    #action-bar { height: 3; margin: 1 2; align-horizontal: left; }
    #status { height: 2; padding: 0 2; color: #93c5fd; }
    Button { margin-right: 1; }
    """
    BINDINGS = [
        ("a", "add_item", "Tambah"),
        ("e", "edit_item", "Ubah"),
        ("d", "delete_item", "Hapus"),
        ("r", "refresh", "Muat ulang"),
        ("q", "quit", "Keluar"),
    ]

    def __init__(self, storage):
        super().__init__()
        self.storage = storage
        self.items: list[dict] = []
        self.filtered_items: list[dict] = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("LAB INVENTORY  |  SISTEM MANAJEMEN INVENTARIS", id="summary-line"),
            Static("Memuat data...", id="summary-details"),
            id="top-summary"
        )
        yield Horizontal(
            Input(placeholder="Cari kode, nama, kategori, kondisi, atau lokasi...", id="search"),
            Button("Bersihkan", id="clear-search"),
            id="toolbar"
        )
        yield Container(DataTable(id="inventory-table", cursor_type="row", zebra_stripes=True), id="table-wrap")
        yield Horizontal(
            Button("＋ Tambah", variant="primary", id="add"),
            Button("✎ Ubah", id="edit"),
            Button("⌫ Hapus", variant="error", id="delete"),
            Button("↻ Muat ulang", id="refresh"),
            id="action-bar"
        )
        yield Static("Pilih baris pada tabel untuk mengubah atau menghapus data. Shortcut: A tambah • E ubah • D hapus • Q keluar", id="status")
        yield Footer()

    def on_mount(self):
        table = self.query_one("#inventory-table", DataTable)
        table.add_columns("Kode", "Nama Barang", "Kategori", "Jumlah", "Kondisi", "Lokasi", "Catatan")
        self.refresh_items()

    def refresh_items(self):
        try:
            self.items = self.storage.list_items()
            self.apply_search()
            self.query_one("#status", Static).update(f"Data dimuat: {len(self.items)} barang.")
        except Exception as exc:
            self.query_one("#status", Static).update(f"Kesalahan membaca data: {exc}")

    def apply_search(self):
        term = self.query_one("#search", Input).value.strip().casefold()
        self.filtered_items = [
            item for item in self.items
            if not term or any(term in str(item.get(key, "")).casefold()
                               for key in ("code", "name", "category", "condition", "location", "notes"))
        ]
        table = self.query_one("#inventory-table", DataTable)
        table.clear()
        for item in self.filtered_items:
            table.add_row(
                str(item["code"]), item["name"], item["category"],
                str(item["quantity"]), item["condition"], item["location"], item["notes"],
                key=str(item["id"])
            )
        total_units = sum(int(item["quantity"]) for item in self.items)
        good = sum(int(item["quantity"]) for item in self.items if item["condition"] == "Baik")
        self.query_one("#summary-details", Static).update(
            f"Jenis barang: {len(self.items)}    •    Total unit: {total_units}    •    Unit berkondisi baik: {good}    •    Hasil pencarian: {len(self.filtered_items)}"
        )

    @on(Input.Changed, "#search")
    def search_changed(self, event):
        self.apply_search()

    @on(Button.Pressed, "#clear-search")
    def clear_search(self, event):
        self.query_one("#search", Input).value = ""

    def selected_item(self):
        table = self.query_one("#inventory-table", DataTable)
        if table.row_count == 0 or table.cursor_row is None:
            self.query_one("#status", Static).update("Belum ada barang yang dipilih.")
            return None
        try:
            row_key = table.get_row_at(table.cursor_row)
            item_id = int(row_key[0])
            return next((x for x in self.filtered_items if int(x["id"]) == item_id), None)
        except (IndexError, TypeError, ValueError):
            return None

    def action_add_item(self):
        self.push_screen(ItemForm(), self.on_add_result)

    @on(Button.Pressed, "#add")
    def add_button(self, event):
        self.action_add_item()

    def on_add_result(self, result):
        if result is None:
            return
        try:
            if any(x["code"].casefold() == result["code"].casefold() for x in self.items):
                self.query_one("#status", Static).update("Kode barang sudah digunakan. Gunakan kode yang unik.")
                return
            self.storage.add_item(result)
            self.refresh_items()
            self.query_one("#status", Static).update("Barang berhasil ditambahkan.")
        except Exception as exc:
            self.query_one("#status", Static).update(f"Gagal menambahkan barang: {exc}")

    def action_edit_item(self):
        item = self.selected_item()
        if item:
            self.push_screen(ItemForm(item), lambda result: self.on_edit_result(item, result))

    @on(Button.Pressed, "#edit")
    def edit_button(self, event):
        self.action_edit_item()

    def on_edit_result(self, old_item, result):
        if result is None:
            return
        try:
            if any(int(x["id"]) != int(old_item["id"]) and x["code"].casefold() == result["code"].casefold() for x in self.items):
                self.query_one("#status", Static).update("Kode barang sudah digunakan oleh barang lain.")
                return
            self.storage.update_item(int(old_item["id"]), result)
            self.refresh_items()
            self.query_one("#status", Static).update("Data barang berhasil diperbarui.")
        except Exception as exc:
            self.query_one("#status", Static).update(f"Gagal mengubah barang: {exc}")

    def action_delete_item(self):
        item = self.selected_item()
        if item:
            self.push_screen(ConfirmDelete(item), lambda confirmed: self.on_delete_result(item, confirmed))

    @on(Button.Pressed, "#delete")
    def delete_button(self, event):
        self.action_delete_item()

    def on_delete_result(self, item, confirmed):
        if not confirmed:
            return
        try:
            self.storage.delete_item(int(item["id"]))
            self.refresh_items()
            self.query_one("#status", Static).update("Barang berhasil dihapus.")
        except Exception as exc:
            self.query_one("#status", Static).update(f"Gagal menghapus barang: {exc}")

    @on(Button.Pressed, "#refresh")
    def refresh_button(self, event):
        self.refresh_items()

    def action_refresh(self):
        self.refresh_items()

    def on_unmount(self):
        try:
            self.storage.close()
        except Exception:
            pass
