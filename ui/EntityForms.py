from textual.app import ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.widgets import Static, Button, Input, Select, Label, TextArea
from textual.screen import ModalScreen
from textual import on


CONDITIONS = ["Baik", "Perlu Perbaikan", "Rusak"]


class LabForm(ModalScreen):
    CSS = """
    LabForm { align: center middle; }
    #lab-dialog { width: 70; max-width: 92%; height: auto; border: round #4f8cff; background: #111827; padding: 2; }
    .field-label { margin-top: 1; color: #bfdbfe; }
    Input { width: 100%; margin-bottom: 1; }
    #lab-buttons { height: 3; align-horizontal: right; }
    #lab-error { height: 2; color: #fca5a5; }
    """

    def __init__(self, lab=None):
        super().__init__()
        self.lab = lab or {}

    def compose(self) -> ComposeResult:
        editing = bool(self.lab)
        yield Container(
            Static("UBAH LAB" if editing else "TAMBAH LAB", id="lab-title"),
            Label("Nama lab *", classes="field-label"),
            Input(value=str(self.lab.get("nama_lab", "")), placeholder="Contoh: Lab Komputer 1", id="nama_lab"),
            Static("", id="lab-error"),
            Horizontal(Button("Simpan", variant="primary", id="save"), Button("Batal", id="cancel"), id="lab-buttons"),
            id="lab-dialog",
        )

    @on(Button.Pressed, "#cancel")
    def cancel(self, event):
        self.dismiss(None)

    @on(Button.Pressed, "#save")
    def save(self, event):
        nama_lab = self.query_one("#nama_lab", Input).value.strip()
        if not nama_lab:
            self.query_one("#lab-error", Static).update("Nama lab wajib diisi.")
            return
        self.dismiss({"nama_lab": nama_lab})


class ComputerForm(ModalScreen):
    CSS = """
    ComputerForm { align: center middle; }
    #computer-dialog { width: 82; max-width: 96%; height: 92%; border: round #22c55e; background: #111827; padding: 1 2; }
    #computer-content { height: 1fr; width: 100%; }
    .field-label { margin-top: 1; color: #bfdbfe; }
    Input, Select { width: 100%; margin-bottom: 1; }
    TextArea { width: 100%; height: 7; margin-bottom: 1; }
    #computer-buttons { height: 3; align-horizontal: right; }
    #computer-error { height: 2; color: #fca5a5; }
    """

    def __init__(self, labs, computer=None):
        super().__init__()
        self.labs = labs
        self.computer = computer or {}

    def compose(self) -> ComposeResult:
        lab_options = [(lab["nama_lab"], lab["id"]) for lab in self.labs]
        editing = bool(self.computer)
        selected_lab = self.computer.get("id_lab", lab_options[0][1] if lab_options else Select.BLANK)
        yield Container(
            Static("UBAH KOMPUTER" if editing else "TAMBAH KOMPUTER"),
            ScrollableContainer(
                Label("Lab *", classes="field-label"),
                Select(lab_options, value=selected_lab, id="id_lab"),
                Label("Kode PC *", classes="field-label"),
                Input(value=str(self.computer.get("kode_pc", "")), placeholder="Contoh: PC-LAB1-01", id="kode_pc"),
                Label("Monitor *", classes="field-label"),
                Select([(x, x) for x in CONDITIONS], value=self.computer.get("monitor", "Baik"), id="monitor"),
                Label("CPU *", classes="field-label"),
                Select([(x, x) for x in CONDITIONS], value=self.computer.get("cpu", "Baik"), id="cpu"),
                Label("Keyboard *", classes="field-label"),
                Select([(x, x) for x in CONDITIONS], value=self.computer.get("keyboard", "Baik"), id="keyboard"),
                Label("Mouse *", classes="field-label"),
                Select([(x, x) for x in CONDITIONS], value=self.computer.get("mouse", "Baik"), id="mouse"),
                Label("Kondisi komputer *", classes="field-label"),
                Select([(x, x) for x in CONDITIONS], value=self.computer.get("kondisi", "Baik"), id="kondisi"),
                Label("Catatan", classes="field-label"),
                TextArea(str(self.computer.get("catatan", "")), id="catatan"),
                id="computer-content",
            ),
            Static("", id="computer-error"),
            Horizontal(Button("Simpan", variant="primary", id="save"), Button("Batal", id="cancel"), id="computer-buttons"),
            id="computer-dialog",
        )

    @on(Button.Pressed, "#cancel")
    def cancel(self, event):
        self.dismiss(None)

    @on(Button.Pressed, "#save")
    def save(self, event):
        kode_pc = self.query_one("#kode_pc", Input).value.strip()
        lab_id = self.query_one("#id_lab", Select).value
        if not kode_pc:
            self.query_one("#computer-error", Static).update("Kode PC wajib diisi.")
            return
        if lab_id is Select.BLANK:
            self.query_one("#computer-error", Static).update("Pilih lab terlebih dahulu.")
            return
        values = {}
        for field in ("monitor", "cpu", "keyboard", "mouse", "kondisi"):
            value = self.query_one(f"#{field}", Select).value
            if value is Select.BLANK:
                self.query_one("#computer-error", Static).update("Semua pilihan kondisi wajib dipilih.")
                return
            values[field] = str(value)
        self.dismiss({
            "id_lab": int(lab_id), "kode_pc": kode_pc, **values,
            "catatan": self.query_one("#catatan", TextArea).text.strip(),
        })


class LabItemForm(ModalScreen):
    CSS = """
    LabItemForm { align: center middle; }
    #item-dialog { width: 78; max-width: 94%; height: 88%; border: round #f59e0b; background: #111827; padding: 1 2; }
    #item-content { height: 1fr; width: 100%; }
    .field-label { margin-top: 1; color: #bfdbfe; }
    Input, Select { width: 100%; margin-bottom: 1; }
    TextArea { width: 100%; height: 8; margin-bottom: 1; }
    #item-buttons { height: 3; align-horizontal: right; }
    #item-error { height: 2; color: #fca5a5; }
    """

    def __init__(self, labs, item=None):
        super().__init__()
        self.labs = labs
        self.item = item or {}

    def compose(self) -> ComposeResult:
        lab_options = [(lab["nama_lab"], lab["id"]) for lab in self.labs]
        selected_lab = self.item.get("id_lab", lab_options[0][1] if lab_options else Select.BLANK)
        yield Container(
            Static("UBAH ITEM LAB" if self.item else "TAMBAH ITEM LAB"),
            ScrollableContainer(
                Label("Lab *", classes="field-label"),
                Select(lab_options, value=selected_lab, id="id_lab"),
                Label("Kode item *", classes="field-label"),
                Input(value=str(self.item.get("kode_item", "")), placeholder="Contoh: PR-001", id="kode_item"),
                Label("Nama item *", classes="field-label"),
                Input(value=str(self.item.get("nama_item", "")), placeholder="Contoh: Proyektor", id="nama_item"),
                Label("Kondisi *", classes="field-label"),
                Select([(x, x) for x in CONDITIONS], value=self.item.get("kondisi", "Baik"), id="kondisi"),
                Label("Catatan", classes="field-label"),
                TextArea(str(self.item.get("catatan", "")), id="catatan"),
                id="item-content",
            ),
            Static("", id="item-error"),
            Horizontal(Button("Simpan", variant="primary", id="save"), Button("Batal", id="cancel"), id="item-buttons"),
            id="item-dialog",
        )

    @on(Button.Pressed, "#cancel")
    def cancel(self, event):
        self.dismiss(None)

    @on(Button.Pressed, "#save")
    def save(self, event):
        lab_id = self.query_one("#id_lab", Select).value
        kode_item = self.query_one("#kode_item", Input).value.strip()
        nama_item = self.query_one("#nama_item", Input).value.strip()
        kondisi = self.query_one("#kondisi", Select).value
        if lab_id is Select.BLANK:
            self.query_one("#item-error", Static).update("Pilih lab terlebih dahulu.")
            return
        if not kode_item or not nama_item:
            self.query_one("#item-error", Static).update("Kode dan nama item wajib diisi.")
            return
        if kondisi is Select.BLANK:
            self.query_one("#item-error", Static).update("Pilih kondisi item.")
            return
        self.dismiss({
            "id_lab": int(lab_id), "kode_item": kode_item, "nama_item": nama_item,
            "kondisi": str(kondisi), "catatan": self.query_one("#catatan", TextArea).text.strip(),
        })
