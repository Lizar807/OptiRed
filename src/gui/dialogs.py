"""
dialogs.py
Diálogos auxiliares reutilizables por las distintas pestañas de la interfaz.
"""

from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
)


class DialogoOpcionesGrafo(QDialog):
    """Pide las propiedades básicas de un grafo: dirigido, ponderado y si
    contiene capacidades (para el módulo de flujo máximo). Se usa al crear un
    grafo vacío o al cargar un archivo .csv/.txt, ya que estos formatos no
    declaran esas propiedades explícitamente (a diferencia de .json)."""

    def __init__(self, parent=None, title="Propiedades del grafo",
                 dirigido=False, ponderado=True, con_capacidad=False,
                 note=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout(self)

        if note:
            label = QLabel(note)
            label.setWordWrap(True)
            layout.addWidget(label)

        form = QFormLayout()
        self.chk_dirigido = QCheckBox("El grafo es dirigido")
        self.chk_dirigido.setChecked(dirigido)
        self.chk_ponderado = QCheckBox("El grafo es ponderado")
        self.chk_ponderado.setChecked(ponderado)
        self.chk_capacidad = QCheckBox("Contiene capacidades (para flujo máximo)")
        self.chk_capacidad.setChecked(con_capacidad)

        form.addRow(self.chk_dirigido)
        form.addRow(self.chk_ponderado)
        form.addRow(self.chk_capacidad)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def valores(self):
        return (
            self.chk_dirigido.isChecked(),
            self.chk_ponderado.isChecked(),
            self.chk_capacidad.isChecked(),
        )
