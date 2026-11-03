from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Static, Button, DataTable, Input
from textual import on

from ui.EntityForms import LabForm, ComputerForm, LabItemForm
from ui.Delete import ConfirmDelete


class InventoryApp(App):
    TITLE = "Inventaris Lab Komputer"
    SUB_TITLE = "Lab, Komputer, dan Item Laboratorium"
    CSS = """
    Screen { background: #0b1220; }
    #top-summary { height: 5; padding: 1 2; background: #17243a; border: round #263b59; margin: 1 2 0 2; }
    #summary-line { color: #dbeafe; text-style: bold; }
    #summary-details { color: #93c5fd; }
    #mode-bar { height: 3; margin: 1 2 0 2; }
    #toolbar { height: 3; margin: 1 2 0 2; }
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

    def on_mount(self):
        self.refresh_all()

    def refresh_all(self):
        try:
            self.labs = self.storage.list_labs()
            if self.mode == "lab":
                self.records = self.labs
            elif self.mode == "computer":
                self.records = self.storage.list_computers()
            else:
                self.records = self.storage.list_lab_items()
            self.apply_search()
            lab_count = len(self.labs)
            computer_count = sum(int(x["jumlah_komputer"] or 0) for x in self.labs)
            item_count = sum(int(x["jumlah_item"] or 0) for x in self.labs)
            self.query_one("#summary-details", Static).update(
                f"Lab: {lab_count}  •  Komputer: {computer_count}  •  Item lab: {item_count}"
            )
            self.query_one("#status", Static).update(f"Data berhasil dimuat: {len(self.records)} baris.")
        except Exception as exc:
            self.query_one("#status", Static).update(f"Kesalahan membaca data: {exc}")

    def refresh_table_columns(self):
        table = self.query_one("#inventory-table", DataTable)
        if self.mode == "lab":
            columns = ["ID", "Nama Lab", "Jumlah Komputer", "Jumlah Item"]
        elif self.mode == "computer":
            columns = ["ID", "Lab", "Kode PC", "Monitor", "CPU", "Keyboard", "Mouse", "Kondisi", "Catatan"]
        else:
            columns = ["ID", "Lab", "Kode Item", "Nama Item", "Kondisi", "Catatan"]
        table.clear(columns=True)
        table.add_columns(*columns)

    def apply_search(self):
        term = self.query_one("#search", Input).value.strip().casefold()
        if not term:
            self.filtered_records = list(self.records)
        else:
            self.filtered_records = [
                record for record in self.records
                if any(term in str(value).casefold() for value in record.values())
            ]
        self.refresh_table_columns()
        table = self.query_one("#inventory-table", DataTable)
        for record in self.filtered_records:
            if self.mode == "lab":
                row = [record["id"], record["nama_lab"], record["jumlah_komputer"], record["jumlah_item"]]
            elif self.mode == "computer":
                row = [record["id"], record["nama_lab"], record["kode_pc"], record["monitor"], record["cpu"],
                       record["keyboard"], record["mouse"], record["kondisi"], record["catatan"]]
            else:
                row = [record["id"], record["nama_lab"], record["kode_item"], record["nama_item"],
                       record["kondisi"], record["catatan"]]
            table.add_row(*(str(value) for value in row), key=str(record["id"]))

    @on(Input.Changed, "#search")
    def search_changed(self, event):
        self.apply_search()

    @on(Button.Pressed, "#clear-search")
    def clear_search(self, event):
        self.query_one("#search", Input).value = ""

    def set_mode(self, mode):
        self.mode = mode
        for mode_name in ("lab", "computer", "item"):
            button = self.query_one(f"#mode-{mode_name}", Button)
            button.variant = "primary" if mode_name == mode else "default"
        self.refresh_all()

    @on(Button.Pressed, "#mode-lab")
    def mode_lab(self, event):
        self.set_mode("lab")

    @on(Button.Pressed, "#mode-computer")
    def mode_computer(self, event):
        self.set_mode("computer")

    @on(Button.Pressed, "#mode-item")
    def mode_item(self, event):
        self.set_mode("item")

    def selected_record(self):
        table = self.query_one("#inventory-table", DataTable)
        if table.row_count == 0 or table.cursor_row is None:
            return None
        index = table.cursor_row
        if index < 0 or index >= len(self.filtered_records):
            return None
        return self.filtered_records[index]

    def action_add_record(self):
        if self.mode == "lab":
            self.push_screen(LabForm(), self.on_lab_result)
        elif self.mode == "computer":
            if not self.labs:
                self.query_one("#status", Static).update("Tambahkan data Lab terlebih dahulu.")
                return
            self.push_screen(ComputerForm(self.labs), self.on_computer_result)
        else:
            if not self.labs:
                self.query_one("#status", Static).update("Tambahkan data Lab terlebih dahulu.")
                return
            self.push_screen(LabItemForm(self.labs), self.on_item_result)

    @on(Button.Pressed, "#add")
    def add_button(self, event):
        self.action_add_record()

    def action_edit_record(self):
        record = self.selected_record()
        if not record:
            self.query_one("#status", Static).update("Belum ada baris yang dipilih.")
            return
        if self.mode == "lab":
            self.push_screen(LabForm(record), lambda result: self.on_lab_result(result, record["id"]))
        elif self.mode == "computer":
            self.push_screen(ComputerForm(self.labs, record), lambda result: self.on_computer_result(result, record["id"]))
        else:
            self.push_screen(LabItemForm(self.labs, record), lambda result: self.on_item_result(result, record["id"]))

    @on(Button.Pressed, "#edit")
    def edit_button(self, event):
        self.action_edit_record()

    def action_delete_record(self):
        record = self.selected_record()
        if not record:
            self.query_one("#status", Static).update("Belum ada baris yang dipilih.")
            return
        label = record["nama_lab"] if self.mode == "lab" else record.get("kode_pc", record.get("nama_item", "data"))
        title = "HAPUS DATA LAB" if self.mode == "lab" else "HAPUS DATA KOMPUTER" if self.mode == "computer" else "HAPUS ITEM LAB"
        self.push_screen(ConfirmDelete(title, f"Yakin menghapus '{label}'?"), lambda confirmed: self.on_delete_result(record, confirmed))

    @on(Button.Pressed, "#delete")
    def delete_button(self, event):
        self.action_delete_record()

    def on_lab_result(self, result, record_id=None):
        if result is None:
            return
        try:
            if record_id is None:
                self.storage.add_lab(result)
            else:
                self.storage.update_lab(record_id, result)
            self.refresh_all()
        except Exception as exc:
            self.query_one("#status", Static).update(f"Gagal menyimpan lab: {exc}")

    def on_computer_result(self, result, record_id=None):
        if result is None:
            return
        try:
            if record_id is None:
                self.storage.add_computer(result)
            else:
                self.storage.update_computer(record_id, result)
            self.refresh_all()
        except Exception as exc:
            self.query_one("#status", Static).update(f"Gagal menyimpan komputer: {exc}")

    def on_item_result(self, result, record_id=None):
        if result is None:
            return
        try:
            if record_id is None:
                self.storage.add_lab_item(result)
            else:
                self.storage.update_lab_item(record_id, result)
            self.refresh_all()
        except Exception as exc:
            self.query_one("#status", Static).update(f"Gagal menyimpan item lab: {exc}")

    def on_delete_result(self, record, confirmed):
        if not confirmed:
            return
        try:
            if self.mode == "lab":
                self.storage.delete_lab(record["id"])
            elif self.mode == "computer":
                self.storage.delete_computer(record["id"])
            else:
                self.storage.delete_lab_item(record["id"])
            self.refresh_all()
        except Exception as exc:
            self.query_one("#status", Static).update(f"Gagal menghapus data: {exc}")

    @on(Button.Pressed, "#refresh")
    def refresh_button(self, event):
        self.refresh_all()

    def action_refresh(self):
        self.refresh_all()

    def on_unmount(self):
        try:
            self.storage.close()
        except Exception:
            pass
