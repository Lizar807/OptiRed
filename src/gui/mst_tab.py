"""
mst_tab.py
Pestaña del Módulo 3: árbol de expansión mínima mediante Prim y Kruskal.
"""

from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.mst import kruskal, prim
from src.gui.common import error, make_table, next_run_color, node_item, numeric_item


class MstTab(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.prim_result = None
        self.kruskal_result = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)

        controls = QHBoxLayout()
        btn_prim = QPushButton("Ejecutar Prim")
        btn_prim.clicked.connect(self.on_run_prim)
        btn_kruskal = QPushButton("Ejecutar Kruskal")
        btn_kruskal.clicked.connect(self.on_run_kruskal)
        controls.addWidget(btn_prim)
        controls.addWidget(btn_kruskal)
        controls.addStretch(1)
        root.addLayout(controls)

        boxes = QHBoxLayout()

        self.box_prim = QGroupBox("Prim")
        prim_layout = QVBoxLayout(self.box_prim)
        self.table_prim = self._make_table()
        prim_layout.addWidget(self.table_prim)
        self.lbl_prim_cost = QLabel("Costo total: —")
        prim_layout.addWidget(self.lbl_prim_cost)
        self.btn_show_prim = QPushButton("Resaltar en el grafo")
        self.btn_show_prim.setEnabled(False)
        self.btn_show_prim.clicked.connect(lambda: self.show_result(self.prim_result, "Prim"))
        prim_layout.addWidget(self.btn_show_prim)
        boxes.addWidget(self.box_prim)

        self.box_kruskal = QGroupBox("Kruskal")
        kruskal_layout = QVBoxLayout(self.box_kruskal)
        self.table_kruskal = self._make_table()
        kruskal_layout.addWidget(self.table_kruskal)
        self.lbl_kruskal_cost = QLabel("Costo total: —")
        kruskal_layout.addWidget(self.lbl_kruskal_cost)
        self.btn_show_kruskal = QPushButton("Resaltar en el grafo")
        self.btn_show_kruskal.setEnabled(False)
        self.btn_show_kruskal.clicked.connect(
            lambda: self.show_result(self.kruskal_result, "Kruskal")
        )
        kruskal_layout.addWidget(self.btn_show_kruskal)
        boxes.addWidget(self.box_kruskal)

        root.addLayout(boxes, 1)

    @staticmethod
    def _make_table():
        return make_table(["Origen", "Destino", "Peso"], sortable=True)

    def refresh(self):
        self.prim_result = None
        self.kruskal_result = None
        self.table_prim.setRowCount(0)
        self.table_kruskal.setRowCount(0)
        self.lbl_prim_cost.setText("Costo total: —")
        self.lbl_kruskal_cost.setText("Costo total: —")
        self.btn_show_prim.setEnabled(False)
        self.btn_show_kruskal.setEnabled(False)

    def _fill_table(self, table, resultado):
        grafo = self.window.graph
        table.setSortingEnabled(False)
        table.setRowCount(len(resultado["aristas"]))
        for row, (u, v, w) in enumerate(resultado["aristas"]):
            table.setItem(row, 0, node_item(grafo, u))
            table.setItem(row, 1, node_item(grafo, v))
            table.setItem(row, 2, numeric_item(w, muted=False))
        table.setSortingEnabled(True)

    def on_run_prim(self):
        grafo = self.window.require_graph()
        if grafo is None:
            return
        try:
            self.prim_result = prim(grafo)
        except ValueError as exc:
            error(self, str(exc))
            return
        self._fill_table(self.table_prim, self.prim_result)
        nota_bosque = " (bosque: el grafo no es conexo)" if self.prim_result["es_bosque"] else ""
        self.lbl_prim_cost.setText(f"Costo total: {self.prim_result['costo']}{nota_bosque}")
        self.btn_show_prim.setEnabled(True)
        self.show_result(self.prim_result, "Prim")

    def on_run_kruskal(self):
        grafo = self.window.require_graph()
        if grafo is None:
            return
        try:
            self.kruskal_result = kruskal(grafo)
        except ValueError as exc:
            error(self, str(exc))
            return
        self._fill_table(self.table_kruskal, self.kruskal_result)
        nota_bosque = " (bosque: el grafo no es conexo)" if self.kruskal_result["es_bosque"] else ""
        self.lbl_kruskal_cost.setText(f"Costo total: {self.kruskal_result['costo']}{nota_bosque}")
        self.btn_show_kruskal.setEnabled(True)

    def show_result(self, resultado, nombre_algoritmo):
        if resultado is None:
            return
        run_color = next_run_color()
        edge_colors = {(u, v): run_color for u, v, _ in resultado["aristas"]}
        self.window.canvas.render_scene(edge_colors=edge_colors)
        self.window.set_canvas_caption(
            f"Árbol de expansión mínima ({nombre_algoritmo}) resaltado. "
            f"Costo total: {resultado['costo']}."
        )
