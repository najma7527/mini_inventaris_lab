from dataclasses import dataclass

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static, TextArea


CONDITIONS = ("Baik", "Perlu Perbaikan", "Rusak")
ENTITY_TITLES = {"lab": "Lab", "computer": "Komputer", "item": "Item Lab"}


@dataclass(frozen=True)
class FormField:
    name: str
    label: str
    kind: str = "input"
    required: bool = True
    placeholder: str = ""
    options: tuple[tuple[str, object], ...] = ()
    default: object = ""


def fields_for_entity(entity: str, labs: list[dict]) -> tuple[FormField, ...]:
    lab_options = tuple((lab["nama_lab"], lab["id"]) for lab in labs)
    if entity == "lab":
        return (FormField("nama_lab", "Nama lab", placeholder="Contoh: Lab Komputer 1"),)
    if entity == "computer":
        return (
            FormField("id_lab", "Lab", "select", options=lab_options),
            FormField("kode_pc", "Kode PC", placeholder="Contoh: PC-LAB1-01"),
            *(FormField(name, label, "select", options=tuple((value, value) for value in CONDITIONS), default="Baik")
              for name, label in (
                  ("monitor", "Monitor"),
                  ("cpu", "CPU"),
                  ("keyboard", "Keyboard"),
                  ("mouse", "Mouse"),
                  ("kondisi", "Kondisi komputer"),
              )),
            FormField("catatan", "Catatan", "textarea", required=False),
        )
    if entity == "item":
        return (
            FormField("id_lab", "Lab", "select", options=lab_options),
            FormField("kode_item", "Kode item", placeholder="Contoh: PR-001"),
            FormField("nama_item", "Nama item", placeholder="Contoh: Proyektor"),
            FormField(
                "kondisi",
                "Kondisi",
                "select",
                options=tuple((value, value) for value in CONDITIONS),
                default="Baik",
            ),
            FormField("catatan", "Catatan", "textarea", required=False),
        )
    raise ValueError(f"Jenis data tidak dikenal: {entity}")


class EntityForm(ModalScreen):
    CSS = """
    EntityForm { align: center middle; }
    #dialog { width: 82; max-width: 95%; height: 90%; border: round #4f8cff; background: #111827; padding: 1 2; }
    #form-content { height: 1fr; width: 100%; }
    .field-label { margin-top: 1; color: #bfdbfe; }
    Input, Select { width: 100%; margin-bottom: 1; }
    TextArea { width: 100%; height: 8; margin-bottom: 1; }
    #form-buttons { height: 3; align-horizontal: right; }
    #form-error { height: 2; color: #fca5a5; }
    """
    BINDINGS = [("escape", "dismiss(None)", "Batal")]

    def __init__(self, entity: str, labs: list[dict], record: dict | None = None):
        super().__init__()
        self.entity = entity
        self.record = record or {}
        self.fields = fields_for_entity(entity, labs)

    def compose(self) -> ComposeResult:
        editing = bool(self.record)
        title = ENTITY_TITLES[self.entity]
        yield Container(
            Static(f"{'UBAH' if editing else 'TAMBAH'} {title.upper()}", id="form-title"),
            ScrollableContainer(
                *(widget for field in self.fields for widget in self._field_widgets(field)),
                id="form-content",
            ),
            Static("", id="form-error"),
            Horizontal(
                Button("Simpan", variant="primary", id="save"),
                Button("Batal", id="cancel"),
                id="form-buttons",
            ),
            id="dialog",
        )

    def _field_widgets(self, field: FormField) -> tuple[object, ...]:
        widgets: list[object] = [Label(f"{field.label}{' *' if field.required else ''}", classes="field-label")]
        value = self.record.get(field.name, field.default)
        if field.kind == "select":
            option_values = {option[1] for option in field.options}
            if value not in option_values:
                value = field.options[0][1] if field.options else Select.BLANK
            widgets.append(Select(field.options, value=value, id=field.name))
        elif field.kind == "textarea":
            widgets.append(TextArea(str(value), id=field.name))
        else:
            widgets.append(Input(value=str(value), placeholder=field.placeholder, id=field.name))
        return tuple(widgets)

    @on(Button.Pressed, "#cancel")
    def cancel(self, _event: Button.Pressed) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#save")
    def save(self, _event: Button.Pressed) -> None:
        values = {}
        for field in self.fields:
            if field.kind == "textarea":
                value = self.query_one(f"#{field.name}", TextArea).text.strip()
            elif field.kind == "select":
                value = self.query_one(f"#{field.name}", Select).value
                if value is Select.BLANK and field.required:
                    self._show_error(f"{field.label} wajib dipilih.")
                    return
                if value is not Select.BLANK and field.name == "id_lab":
                    value = int(value)
            else:
                value = self.query_one(f"#{field.name}", Input).value.strip()

            if field.required and not value:
                self._show_error(f"{field.label} wajib diisi.")
                return
            values[field.name] = value

        self.dismiss(values)

    def _show_error(self, message: str) -> None:
        self.query_one("#form-error", Static).update(message)
