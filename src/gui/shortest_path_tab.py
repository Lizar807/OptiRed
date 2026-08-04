"""
shortest_path_tab.py
Pestaña del Módulo 4: rutas más cortas desde un nodo origen mediante
Dijkstra (pesos no negativos) y Bellman-Ford (admite pesos negativos y
detecta ciclos negativos).
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

from src.shortest_paths import bellman_ford, dijkstra, reconstruir_camino
from src.gui.common import (
    COLOR_SINK,
    COLOR_SOURCE,
    ROW_BG_SOURCE,
    ROW_BG_TARGET,
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


class ShortestPathTab(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.source = None
        self.dijkstra_result = None
        self.bf_result = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Origen:"))
        self.combo_source = QComboBox()
        controls.addWidget(self.combo_source, 1)
        controls.addWidget(QLabel("Destino (opcional):"))
        self.combo_target = QComboBox()
        controls.addWidget(self.combo_target, 1)
        root.addLayout(controls)

        run_row = QHBoxLayout()
        btn_dijkstra = QPushButton("Ejecutar Dijkstra")
        btn_dijkstra.clicked.connect(self.on_run_dijkstra)
        btn_bf = QPushButton("Ejecutar Bellman-Ford")
        btn_bf.clicked.connect(self.on_run_bellman_ford)
        run_row.addWidget(btn_dijkstra)
        run_row.addWidget(btn_bf)
        run_row.addStretch(1)
        root.addLayout(run_row)

        boxes = QHBoxLayout()

        self.box_dijkstra = QGroupBox("Dijkstra")
        d_layout = QVBoxLayout(self.box_dijkstra)
        self.table_dijkstra = self._make_table()
        d_layout.addWidget(self.table_dijkstra)
        self.lbl_dijkstra_path = QLabel("Camino: —")
        self.lbl_dijkstra_path.setWordWrap(True)
        d_layout.addWidget(self.lbl_dijkstra_path)
        self.btn_show_dijkstra = QPushButton("Resaltar en el grafo")
        self.btn_show_dijkstra.setEnabled(False)
        self.btn_show_dijkstra.clicked.connect(
            lambda: self.show_result(self.dijkstra_result, "Dijkstra")
        )
        d_layout.addWidget(self.btn_show_dijkstra)
        boxes.addWidget(self.box_dijkstra)

        self.box_bf = QGroupBox("Bellman-Ford")
        bf_layout = QVBoxLayout(self.box_bf)
        self.table_bf = self._make_table()
        bf_layout.addWidget(self.table_bf)
        self.lbl_bf_path = QLabel("Camino: —")
        self.lbl_bf_path.setWordWrap(True)
        bf_layout.addWidget(self.lbl_bf_path)
        self.btn_show_bf = QPushButton("Resaltar en el grafo")
        self.btn_show_bf.setEnabled(False)
        self.btn_show_bf.clicked.connect(
            lambda: self.show_result(self.bf_result, "Bellman-Ford")
        )
        bf_layout.addWidget(self.btn_show_bf)
        boxes.addWidget(self.box_bf)

        root.addLayout(boxes, 1)

    @staticmethod
    def _make_table():
        return make_table(["Nodo", "Distancia"], sortable=True)

    def refresh(self):
        populate_node_combo(self.combo_source, self.window.graph)
        populate_node_combo(self.combo_target, self.window.graph, include_empty=True)
        self.dijkstra_result = None
        self.bf_result = None
        self.table_dijkstra.setRowCount(0)
        self.table_bf.setRowCount(0)
        self.lbl_dijkstra_path.setText("Camino: —")
        self.lbl_bf_path.setText("Camino: —")
        self.btn_show_dijkstra.setEnabled(False)
        self.btn_show_bf.setEnabled(False)

    def _fill_table(self, table, distancias, origen=None, destino=None):
        grafo = self.window.graph
        table.setSortingEnabled(False)
        table.setRowCount(len(distancias))
        for row, (nodo, d) in enumerate(distancias.items()):
            table.setItem(row, 0, node_item(grafo, nodo))
            table.setItem(row, 1, numeric_item(d))
            if nodo == origen:
                tint_row(table, row, ROW_BG_SOURCE)
            elif nodo == destino:
                tint_row(table, row, ROW_BG_TARGET)
        table.setSortingEnabled(True)

    def _path_text(self, camino, costo):
        if camino is None:
            return "No existe camino entre el origen y el destino seleccionados."
        return f"{' -> '.join(camino)}  (costo: {fmt(costo)})"

    def on_run_dijkstra(self):
        grafo = self.window.require_graph()
        if grafo is None:
            return
        origen = self.combo_source.currentData()
        if origen is None:
            warn(self, "Seleccione un nodo de origen.")
            return
        try:
            self.dijkstra_result = dijkstra(grafo, origen)
        except ValueError as exc:
            error(self, str(exc))
            return
        self.source = origen
        destino = self.combo_target.currentData()
        self._fill_table(self.table_dijkstra, self.dijkstra_result["distancias"], origen, destino)

        if destino:
            camino = reconstruir_camino(self.dijkstra_result["anteriores"], origen, destino)
            costo = self.dijkstra_result["distancias"].get(destino)
            self.lbl_dijkstra_path.setText(self._path_text(camino, costo))
        else:
            self.lbl_dijkstra_path.setText("Camino: seleccione un destino para reconstruirlo.")

        self.btn_show_dijkstra.setEnabled(True)
        self.show_result(self.dijkstra_result, "Dijkstra")

    def on_run_bellman_ford(self):
        grafo = self.window.require_graph()
        if grafo is None:
            return
        origen = self.combo_source.currentData()
        if origen is None:
            warn(self, "Seleccione un nodo de origen.")
            return
        try:
            self.bf_result = bellman_ford(grafo, origen)
        except ValueError as exc:
            error(self, str(exc))
            return
        self.source = origen

        if self.bf_result["tiene_ciclo_negativo"]:
            self.table_bf.setRowCount(0)
            self.lbl_bf_path.setText(
                "Se detectó un ciclo negativo alcanzable desde el origen. "
                "No es posible calcular rutas mínimas bien definidas."
            )
            self.btn_show_bf.setEnabled(False)
            return

        destino = self.combo_target.currentData()
        self._fill_table(self.table_bf, self.bf_result["distancias"], origen, destino)
        if destino:
            camino = reconstruir_camino(self.bf_result["anteriores"], origen, destino)
            costo = self.bf_result["distancias"].get(destino)
            self.lbl_bf_path.setText(self._path_text(camino, costo))
        else:
            self.lbl_bf_path.setText("Camino: seleccione un destino para reconstruirlo.")

        self.btn_show_bf.setEnabled(True)
        self.show_result(self.bf_result, "Bellman-Ford")

    def show_result(self, resultado, nombre_algoritmo):
        if resultado is None or resultado.get("tiene_ciclo_negativo"):
            return
        destino = self.combo_target.currentData()
        node_colors = {self.source: COLOR_SOURCE}
        edge_colors = {}
        if destino:
            camino = reconstruir_camino(resultado["anteriores"], self.source, destino)
            if camino:
                run_color = next_run_color()
                node_colors[destino] = COLOR_SINK
                for n in camino:
                    node_colors.setdefault(n, run_color)
                for u, v in zip(camino, camino[1:]):
                    edge_colors[(u, v)] = run_color
        self.window.canvas.render_scene(node_colors=node_colors, edge_colors=edge_colors)
        self.window.set_canvas_caption(
            f"{nombre_algoritmo} desde {self.source}: origen en morado"
            + (", destino en rojo y camino resaltado." if destino else ".")
        )
