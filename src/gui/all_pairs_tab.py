"""
all_pairs_tab.py
Pestaña del Módulo 5: caminos más cortos entre todos los pares de nodos
mediante Floyd-Warshall y Johnson.
"""

from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.all_pairs import (
    floyd_warshall,
    johnson,
    reconstruir_camino_floyd,
    reconstruir_camino_johnson,
)
from src.gui.common import (
    COLOR_SINK,
    COLOR_SOURCE,
    error,
    fmt,
    next_run_color,
    node_label,
    numeric_item,
    populate_node_combo,
)


class AllPairsTab(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.fw_result = None
        self.johnson_result = None
        self.nodes = []
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)

        run_row = QHBoxLayout()
        btn_fw = QPushButton("Ejecutar Floyd-Warshall")
        btn_fw.clicked.connect(self.on_run_fw)
        btn_johnson = QPushButton("Ejecutar Johnson")
        btn_johnson.clicked.connect(self.on_run_johnson)
        run_row.addWidget(btn_fw)
        run_row.addWidget(btn_johnson)
        run_row.addStretch(1)
        root.addLayout(run_row)

        path_row = QHBoxLayout()
        path_row.addWidget(QLabel("Ver camino de:"))
        self.combo_source = QComboBox()
        path_row.addWidget(self.combo_source, 1)
        path_row.addWidget(QLabel("a:"))
        self.combo_target = QComboBox()
        path_row.addWidget(self.combo_target, 1)
        self.btn_show_path_fw = QPushButton("Resaltar (Floyd-Warshall)")
        self.btn_show_path_fw.setEnabled(False)
        self.btn_show_path_fw.clicked.connect(self.on_show_fw_path)
        self.btn_show_path_johnson = QPushButton("Resaltar (Johnson)")
        self.btn_show_path_johnson.setEnabled(False)
        self.btn_show_path_johnson.clicked.connect(self.on_show_johnson_path)
        path_row.addWidget(self.btn_show_path_fw)
        path_row.addWidget(self.btn_show_path_johnson)
        root.addLayout(path_row)

        self.tabs = QTabWidget()
        self.table_fw = QTableWidget()
        self.table_fw.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_fw.setAlternatingRowColors(True)
        self.table_johnson = QTableWidget()
        self.table_johnson.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_johnson.setAlternatingRowColors(True)
        self.tabs.addTab(self.table_fw, "Matriz Floyd-Warshall")
        self.tabs.addTab(self.table_johnson, "Matriz Johnson")
        root.addWidget(self.tabs, 1)

        self.lbl_note = QLabel("")
        self.lbl_note.setWordWrap(True)
        root.addWidget(self.lbl_note)

    def refresh(self):
        grafo = self.window.graph
        self.nodes = grafo.obtener_nodos() if grafo else []
        populate_node_combo(self.combo_source, grafo)
        populate_node_combo(self.combo_target, grafo)
        self.fw_result = None
        self.johnson_result = None
        self.table_fw.clear()
        self.table_johnson.clear()
        self.table_fw.setRowCount(0)
        self.table_fw.setColumnCount(0)
        self.table_johnson.setRowCount(0)
        self.table_johnson.setColumnCount(0)
        self.btn_show_path_fw.setEnabled(False)
        self.btn_show_path_johnson.setEnabled(False)
        self.lbl_note.setText("")

    def _fill_matrix(self, table, resultado, nodos):
        grafo = self.window.graph
        table.setRowCount(len(nodos))
        table.setColumnCount(len(nodos))
        table.setHorizontalHeaderLabels(nodos)
        table.setVerticalHeaderLabels(nodos)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for j, v in enumerate(nodos):
            header_item = table.horizontalHeaderItem(j)
            if header_item is not None:
                header_item.setToolTip(node_label(grafo, v))
        for i, u in enumerate(nodos):
            table.verticalHeaderItem(i).setToolTip(node_label(grafo, u))
            for j, v in enumerate(nodos):
                valor = resultado["distancias"][u][v]
                item = numeric_item(valor)
                if u == v:
                    item.setForeground(COLOR_SOURCE)
                table.setItem(i, j, item)

    def on_run_fw(self):
        grafo = self.window.require_graph()
        if grafo is None:
            return
        self.fw_result = floyd_warshall(grafo)
        self.nodes = grafo.obtener_nodos()
        if self.fw_result["tiene_ciclo_negativo"]:
            self.lbl_note.setText(
                "Se detectó un ciclo negativo. No es posible calcular una matriz de "
                "distancias bien definida con Floyd-Warshall."
            )
            self.btn_show_path_fw.setEnabled(False)
            return
        self._fill_matrix(self.table_fw, self.fw_result, self.nodes)
        self.tabs.setCurrentWidget(self.table_fw)
        self.btn_show_path_fw.setEnabled(True)
        self.lbl_note.setText("Matriz de distancias mínimas calculada con Floyd-Warshall.")

    def on_run_johnson(self):
        grafo = self.window.require_graph()
        if grafo is None:
            return
        try:
            self.johnson_result = johnson(grafo)
        except ValueError as exc:
            error(self, str(exc))
            return
        self.nodes = grafo.obtener_nodos()
        if self.johnson_result["tiene_ciclo_negativo"]:
            self.lbl_note.setText(
                "Johnson detectó un ciclo negativo alcanzable desde el nodo auxiliar. "
                "El algoritmo se detiene y no calcula la matriz de distancias."
            )
            self.btn_show_path_johnson.setEnabled(False)
            return
        self._fill_matrix(self.table_johnson, self.johnson_result, self.nodes)
        self.tabs.setCurrentWidget(self.table_johnson)
        self.btn_show_path_johnson.setEnabled(True)
        self.lbl_note.setText("Matriz de distancias mínimas calculada con Johnson.")

    def _highlight_path(self, camino, costo, nombre_algoritmo, origen, destino):
        if camino is None:
            self.window.set_canvas_caption(
                f"No existe camino desde {origen} hasta {destino} ({nombre_algoritmo})."
            )
            return
        run_color = next_run_color()
        node_colors = {origen: COLOR_SOURCE, destino: COLOR_SINK}
        for n in camino:
            node_colors.setdefault(n, run_color)
        edge_colors = {(u, v): run_color for u, v in zip(camino, camino[1:])}
        self.window.canvas.render_scene(node_colors=node_colors, edge_colors=edge_colors)
        self.window.set_canvas_caption(
            f"Camino {origen} -> {destino} según {nombre_algoritmo}: "
            f"{' -> '.join(camino)} (costo: {fmt(costo)})."
        )

    def on_show_fw_path(self):
        origen = self.combo_source.currentData()
        destino = self.combo_target.currentData()
        if not origen or not destino or self.fw_result is None:
            return
        camino = reconstruir_camino_floyd(
            self.fw_result["siguiente"], self.fw_result["distancias"], origen, destino
        )
        costo = self.fw_result["distancias"][origen][destino]
        self._highlight_path(camino, costo, "Floyd-Warshall", origen, destino)

    def on_show_johnson_path(self):
        origen = self.combo_source.currentData()
        destino = self.combo_target.currentData()
        if not origen or not destino or self.johnson_result is None:
            return
        camino = reconstruir_camino_johnson(
            self.johnson_result["anteriores_por_origen"], origen, destino
        )
        costo = self.johnson_result["distancias"][origen][destino]
        self._highlight_path(camino, costo, "Johnson", origen, destino)
