from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, DataTable, Footer, Header, Input, Static

from ui.delete_dialog import ConfirmDelete
from ui.entity_form import ENTITY_TITLES, EntityForm


ENTITY_STORAGE = {"lab": "lab", "computer": "computer", "item": "lab_item"}
LIST_METHODS = {
    "lab": "list_labs",
    "computer": "list_computers",
    "item": "list_lab_items",
}
TABLE_COLUMNS = {
    "lab": ("Nama Lab", "Jumlah Komputer", "Jumlah Item"),
    "computer": ("Lab", "Kode PC", "Monitor", "CPU", "Keyboard", "Mouse", "Kondisi", "Catatan"),
    "item": ("Lab", "Kode Item", "Nama Item", "Kondisi", "Catatan"),
}
TABLE_FIELDS = {
    "lab": ("nama_lab", "jumlah_komputer", "jumlah_item"),
    "computer": ("nama_lab", "kode_pc", "monitor", "cpu", "keyboard", "mouse", "kondisi", "catatan"),
    "item": ("nama_lab", "kode_item", "nama_item", "kondisi", "catatan"),
}


class InventoryApp(App):
    TITLE = "Inventaris Lab Komputer"
    SUB_TITLE = "Lab, Komputer, dan Item Laboratorium"
    CSS = """
    Screen { background: #0b1220; }
    #top-summary { height: 5; padding: 1 2; background: #17243a; border: round #263b59; margin: 1 2 0 2; }
    #summary-line { color: #dbeafe; text-style: bold; }
    #summary-details { color: #93c5fd; }
    #mode-bar, #toolbar { height: 3; margin: 1 2 0 2; }
    #search { width: 1fr; }
    #table-wrap { width: 100%; height: 1fr; margin: 1 2; }
    DataTable { width: 100%; height: 1fr; }
    #action-bar { height: 3; margin: 0 2; }
    #status { height: 2; padding: 0 2; color: #93c5fd; }
    Button { margin-right: 1; }
    """
    BINDINGS = [
        ("a", "add_record", "Tambah"),
        ("e", "edit_record", "Ubah"),
        ("d", "delete_record", "Hapus"),
        ("r", "refresh", "Muat ulang"),
        ("q", "quit", "Keluar"),
    ]

    def __init__(self, storage):
        super().__init__()
        self.storage = storage
        self.mode = "lab"
        self.labs = []
        self.records = []
        self.filtered_records = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("INVENTARIS LAB KOMPUTER", id="summary-line"),
            Static("Memuat data...", id="summary-details"),
            id="top-summary",
        )
        yield Horizontal(
            Button("Lab", variant="primary", id="mode-lab"),
            Button("Komputer", id="mode-computer"),
            Button("Item Lab", id="mode-item"),
            id="mode-bar",
        )
        yield Horizontal(
            Input(placeholder="Cari data pada tabel...", id="search"),
            Button("Bersihkan", id="clear-search"),
            id="toolbar",
        )
        yield Container(DataTable(id="inventory-table", cursor_type="row", zebra_stripes=True), id="table-wrap")
        yield Horizontal(
            Button("＋ Tambah", variant="primary", id="add"),
            Button("✎ Ubah", id="edit"),
            Button("⌫ Hapus", variant="error", id="delete"),
            Button("↻ Muat ulang", id="refresh"),
            id="action-bar",
        )
        yield Static("Pilih Lab, Komputer, atau Item Lab untuk mengelola data.", id="status")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_all()

    def refresh_all(self) -> None:
        try:
            self.labs = self.storage.list_labs()
            self.records = getattr(self.storage, LIST_METHODS[self.mode])()
            self.apply_search()
            self.query_one("#summary-details", Static).update(
                f"Lab: {len(self.labs)}  •  "
                f"Komputer: {sum(int(lab['jumlah_komputer'] or 0) for lab in self.labs)}  •  "
                f"Item lab: {sum(int(lab['jumlah_item'] or 0) for lab in self.labs)}"
            )
            self.query_one("#status", Static).update(f"Data berhasil dimuat: {len(self.records)} baris.")
        except Exception as exc:
            self.query_one("#status", Static).update(f"Kesalahan membaca data: {exc}")

    def apply_search(self) -> None:
        term = self.query_one("#search", Input).value.strip().casefold()
        self.filtered_records = [
            record for record in self.records
            if not term or any(term in str(value).casefold() for value in record.values())
        ]
        table = self.query_one("#inventory-table", DataTable)
        table.clear(columns=True)
        table.add_columns(*TABLE_COLUMNS[self.mode])
        for record in self.filtered_records:
            table.add_row(*(str(record[field]) for field in TABLE_FIELDS[self.mode]))

    @on(Input.Changed, "#search")
    def search_changed(self, _event: Input.Changed) -> None:
        self.apply_search()

    @on(Button.Pressed, "#clear-search")
    def clear_search(self, _event: Button.Pressed) -> None:
        self.query_one("#search", Input).value = ""

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        for name in ENTITY_TITLES:
            self.query_one(f"#mode-{name}", Button).variant = "primary" if name == mode else "default"
        self.refresh_all()

    @on(Button.Pressed, "#mode-lab")
    def mode_lab(self, _event: Button.Pressed) -> None:
        self.set_mode("lab")

    @on(Button.Pressed, "#mode-computer")
    def mode_computer(self, _event: Button.Pressed) -> None:
        self.set_mode("computer")

    @on(Button.Pressed, "#mode-item")
    def mode_item(self, _event: Button.Pressed) -> None:
        self.set_mode("item")

    def selected_record(self) -> dict | None:
        table = self.query_one("#inventory-table", DataTable)
        index = table.cursor_row
        if index is None or index < 0 or index >= len(self.filtered_records):
            return None
        return self.filtered_records[index]

    def action_add_record(self) -> None:
        self.open_form()

    @on(Button.Pressed, "#add")
    def add_button(self, _event: Button.Pressed) -> None:
        self.action_add_record()

    def action_edit_record(self) -> None:
        record = self.selected_record()
        if record is None:
            self.show_status("Belum ada baris yang dipilih.")
            return
        self.open_form(record)

    @on(Button.Pressed, "#edit")
    def edit_button(self, _event: Button.Pressed) -> None:
        self.action_edit_record()

    def open_form(self, record: dict | None = None) -> None:
        entity = self.mode
        if entity != "lab" and not self.labs:
            self.show_status("Tambahkan data Lab terlebih dahulu.")
            return
        record_id = record["id"] if record else None
        self.push_screen(
            EntityForm(entity, self.labs, record),
            lambda result: self.on_form_result(entity, result, record_id),
        )

    def on_form_result(self, entity: str, result: dict | None, record_id: int | None = None) -> None:
        if result is None:
            return
        action = "add" if record_id is None else "update"
        method = getattr(self.storage, f"{action}_{ENTITY_STORAGE[entity]}")
        try:
            if record_id is None:
                method(result)
            else:
                method(record_id, result)
            self.refresh_all()
        except Exception as exc:
            self.show_status(f"Gagal menyimpan {ENTITY_TITLES[entity].lower()}: {exc}")

    def action_delete_record(self) -> None:
        record = self.selected_record()
        if record is None:
            self.show_status("Belum ada baris yang dipilih.")
            return
        entity = self.mode
        if entity == "lab":
            label = record["nama_lab"]
        elif entity == "computer":
            label = f"{record['nama_lab']} ({record['kode_pc']})"
        else:
            label = f"{record['nama_item']} ({record['kode_item']})"
        title = f"HAPUS DATA {ENTITY_TITLES[entity].upper()}"
        self.push_screen(
            ConfirmDelete(title, f"Yakin menghapus '{label}'?"),
            lambda confirmed: self.on_delete_result(entity, record, confirmed),
        )

    @on(Button.Pressed, "#delete")
    def delete_button(self, _event: Button.Pressed) -> None:
        self.action_delete_record()

    def on_delete_result(self, entity: str, record: dict, confirmed: bool) -> None:
        if not confirmed:
            return
        try:
            getattr(self.storage, f"delete_{ENTITY_STORAGE[entity]}")(record["id"])
            self.refresh_all()
        except Exception as exc:
            self.show_status(f"Gagal menghapus data: {exc}")

    @on(Button.Pressed, "#refresh")
    def refresh_button(self, _event: Button.Pressed) -> None:
        self.refresh_all()

    def action_refresh(self) -> None:
        self.refresh_all()

    def show_status(self, message: str) -> None:
        self.query_one("#status", Static).update(message)
