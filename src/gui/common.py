"""
common.py
Utilidades compartidas por las pestañas de la interfaz gráfica: paleta de
colores para resaltar resultados, formato de nodos en los combos, tablas de
resultados con estilo consistente (filas alternadas, celdas numéricas
alineadas, resaltado de filas relevantes) y diálogos de error/información
reutilizables.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QHeaderView,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
)

INF = float("inf")

# Fuente monoespaciada para columnas numéricas: alinea dígitos entre filas y
# distingue visualmente los valores de las etiquetas de nodo.
MONO_FONT = QFont("Cascadia Mono")
MONO_FONT.setStyleHint(QFont.StyleHint.Monospace)
MONO_FONT.setPointSize(10)

# Tonos de fondo para resaltar filas completas de una tabla (además del
# resaltado que ya reciben nodos/aristas en el lienzo del grafo).
ROW_BG_SOURCE = QColor("#3b0764")     # fila del nodo origen (violeta oscuro)
ROW_BG_TARGET = QColor("#4c0519")     # fila del nodo destino (rojo oscuro)
ROW_BG_SATURATED = QColor("#4a044e")  # fila de arista saturada / crítica
COLOR_TEXT_MUTED = QColor("#64748b")  # texto atenuado (INF, no alcanzable)

# Paleta de colores para el resultado resaltado en el mapa (camino, árbol,
# flujo, recorrido). Cada vez que se ejecuta un algoritmo se toma el
# siguiente color de la lista, para distinguir visualmente una ejecución de
# la anterior aunque sea del mismo tipo de resultado.
RUN_COLOR_PALETTE = [
    QColor("#38bdf8"),  # celeste
    QColor("#f59e0b"),  # ámbar
    QColor("#22c55e"),  # verde
    QColor("#f472b6"),  # rosa
    QColor("#a78bfa"),  # lavanda
    QColor("#fb7185"),  # coral
    QColor("#2dd4bf"),  # turquesa
    QColor("#facc15"),  # amarillo
]
_run_color_state = {"index": 0}


def next_run_color():
    """Devuelve un color distinto cada vez que se llama (recorriendo
    RUN_COLOR_PALETTE de forma cíclica), para que cada ejecución de un
    algoritmo quede resaltada en el mapa con un color propio."""
    color = RUN_COLOR_PALETTE[_run_color_state["index"] % len(RUN_COLOR_PALETTE)]
    _run_color_state["index"] += 1
    return color


# Colores fijos que identifican un rol dentro del grafo (se mantienen
# constantes entre ejecuciones para que sirvan de referencia/leyenda); el
# color del resultado en sí (camino, árbol, flujo) varía en cada ejecución
# mediante next_run_color().
COLOR_SOURCE = QColor("#a855f7")      # nodo origen
COLOR_SINK = QColor("#ef4444")        # nodo sumidero / destino
COLOR_UNREACHABLE = QColor("#475569")  # nodo no alcanzable



def node_label(graph, node):
    """Devuelve 'id — Nombre' si el grafo tiene un nombre legible para el
    nodo (cargado desde JSON con esquema enriquecido); si no, solo el id."""
    if graph and graph.etiquetas and node in graph.etiquetas:
        return f"{node} — {graph.etiquetas[node]}"
    return str(node)


def populate_node_combo(combo: QComboBox, graph, include_empty=False, empty_text="(ninguno)"):
    combo.blockSignals(True)
    combo.clear()
    if include_empty:
        combo.addItem(empty_text, None)
    if graph is not None:
        for node in graph.obtener_nodos():
            combo.addItem(node_label(graph, node), node)
    combo.blockSignals(False)


def selected_node(combo: QComboBox):
    return combo.currentData()


def fmt(value):
    if value == INF:
        return "INF"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def warn(parent, text, title="Aviso"):
    QMessageBox.warning(parent, title, text)


def error(parent, text, title="Error"):
    QMessageBox.critical(parent, title, text)


def info(parent, text, title="OptiRed"):
    QMessageBox.information(parent, title, text)


def make_table(headers, sortable=False):
    """Crea una QTableWidget con estilo consistente para toda la aplicación:
    filas alternadas, selección de fila completa, sin edición directa y,
    opcionalmente, ordenable al hacer clic en el encabezado."""
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.verticalHeader().setVisible(False)
    table.setSortingEnabled(sortable)
    return table


def node_item(graph, node):
    """Celda de tabla para un nodo: muestra 'id — Nombre' cuando el grafo
    trae nombres legibles (igual que en los combos)."""
    return QTableWidgetItem(node_label(graph, node))


def numeric_item(value, muted=None):
    """Celda numérica alineada a la derecha con fuente monoespaciada. Los
    valores INF (no alcanzable) se muestran atenuados salvo que se indique
    lo contrario con muted=False."""
    item = QTableWidgetItem(fmt(value))
    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    item.setFont(MONO_FONT)
    is_muted = (value == INF) if muted is None else muted
    if is_muted:
        item.setForeground(COLOR_TEXT_MUTED)
    return item


def tint_row(table: QTableWidget, row: int, color: QColor):
    """Tiñe el fondo de todas las celdas de una fila ya llenada (para
    resaltar, por ejemplo, la fila del nodo origen o destino)."""
    if row < 0 or row >= table.rowCount():
        return
    for col in range(table.columnCount()):
        item = table.item(row, col)
        if item is not None:
            item.setBackground(color)
