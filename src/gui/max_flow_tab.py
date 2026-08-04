"""
max_flow_tab.py
Pestaña del Módulo 6: flujo máximo entre una fuente y un sumidero mediante
Ford-Fulkerson (búsqueda de caminos aumentantes por BFS / Edmonds-Karp).
"""

from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.max_flow import ford_fulkerson
from src.gui.common import (
    COLOR_SINK,
    COLOR_SOURCE,
    ROW_BG_SATURATED,
    error,
    fmt,
    make_table,
    next_run_color,
    node_item,
    numeric_item,
    populate_node_combo,
    tint_row,
    warn,
)


class MaxFlowTab(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.result = None
        self.source = None
        self.sink = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Fuente:"))
        self.combo_source = QComboBox()
        controls.addWidget(self.combo_source, 1)
        controls.addWidget(QLabel("Sumidero:"))
        self.combo_sink = QComboBox()
        controls.addWidget(self.combo_sink, 1)
        btn_run = QPushButton("Calcular flujo máximo")
        btn_run.clicked.connect(self.on_run)
        controls.addWidget(btn_run)
        root.addLayout(controls)

        self.lbl_result = QLabel("Flujo máximo: —")
        self.lbl_result.setStyleSheet("font-weight: 600;")
        root.addWidget(self.lbl_result)

        box = QGroupBox("Flujo por arista")
        box_layout = QVBoxLayout(box)
        self.table = make_table(
            ["Origen", "Destino", "Flujo / Capacidad", "Uso"], sortable=True
        )
        box_layout.addWidget(self.table)
        self.lbl_saturated_hint = QLabel(
            "Las aristas saturadas (flujo = capacidad) se resaltan: suelen formar el corte mínimo."
        )
        self.lbl_saturated_hint.setWordWrap(True)
        self.lbl_saturated_hint.setStyleSheet("color: #94a3b8;")
        box_layout.addWidget(self.lbl_saturated_hint)
        root.addWidget(box, 1)

        self.btn_show = QPushButton("Resaltar en el grafo")
        self.btn_show.setEnabled(False)
        self.btn_show.clicked.connect(self.on_show)
        root.addWidget(self.btn_show)

    def refresh(self):
        grafo = self.window.graph
        populate_node_combo(self.combo_source, grafo)
        populate_node_combo(self.combo_sink, grafo)
        self.result = None
        self.table.setRowCount(0)
        self.lbl_result.setText("Flujo máximo: —")
        self.btn_show.setEnabled(False)

        # Si el archivo cargado (JSON con esquema enriquecido) declara fuente
        # y sumidero en sus metadatos, se preseleccionan por comodidad.
        if grafo is not None and grafo.metadatos:
            fuente = grafo.metadatos.get("fuente")
            sumidero = grafo.metadatos.get("sumidero")
            if fuente:
                idx = self.combo_source.findData(fuente)
                if idx >= 0:
                    self.combo_source.setCurrentIndex(idx)
            if sumidero:
                idx = self.combo_sink.findData(sumidero)
                if idx >= 0:
                    self.combo_sink.setCurrentIndex(idx)

    def on_run(self):
        grafo = self.window.require_graph()
        if grafo is None:
            return
        fuente = self.combo_source.currentData()
        sumidero = self.combo_sink.currentData()
        if fuente is None or sumidero is None:
            warn(self, "Seleccione el nodo fuente y el nodo sumidero.")
            return
        try:
            self.result = ford_fulkerson(grafo, fuente, sumidero)
        except ValueError as exc:
            error(self, str(exc))
            return
        self.source, self.sink = fuente, sumidero

        if not self.result["tiene_camino"]:
            self.table.setRowCount(0)
            self.lbl_result.setText(f"No existe camino desde {fuente} hasta {sumidero}.")
            self.btn_show.setEnabled(False)
            return

        self.lbl_result.setText(f"Flujo máximo encontrado: {fmt(self.result['flujo_maximo'])}")
        aristas = list(self.result["flujo_por_arista"].items())
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(aristas))
        for row, ((u, v), (usado, cap)) in enumerate(aristas):
            self.table.setItem(row, 0, node_item(grafo, u))
            self.table.setItem(row, 1, node_item(grafo, v))
            self.table.setItem(row, 2, numeric_item(f"{fmt(usado)} / {fmt(cap)}", muted=False))
            pct = (usado / cap * 100) if cap else 0
            self.table.setItem(row, 3, numeric_item(f"{pct:.0f}%", muted=False))
            if cap and usado >= cap:
                tint_row(self.table, row, ROW_BG_SATURATED)
        self.table.setSortingEnabled(True)

        self.btn_show.setEnabled(True)
        self.on_show()

    def on_show(self):
        if self.result is None or not self.result["tiene_camino"]:
            return
        run_color = next_run_color()
        node_colors = {self.source: COLOR_SOURCE, self.sink: COLOR_SINK}
        edge_colors = {}
        edge_extra = {}
        for (u, v), (usado, cap) in self.result["flujo_por_arista"].items():
            edge_colors[(u, v)] = run_color
            edge_extra[(u, v)] = f"flujo {fmt(usado)}/{fmt(cap)}"
        self.window.canvas.render_scene(
            node_colors=node_colors, edge_colors=edge_colors, edge_extra=edge_extra
        )
        self.window.set_canvas_caption(
            f"Flujo máximo {self.source} -> {self.sink}: {fmt(self.result['flujo_maximo'])}. "
            f"Aristas con flujo enviado resaltadas."
        )
