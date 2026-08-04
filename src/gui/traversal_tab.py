"""
traversal_tab.py
Pestaña del Módulo 2: recorridos BFS y DFS desde un nodo origen.
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

from src.bfs_dfs import bfs, dfs
from src.gui.common import (
    COLOR_UNREACHABLE,
    COLOR_SOURCE,
    ROW_BG_SOURCE,
    error,
    make_table,
    next_run_color,
    node_item,
    populate_node_combo,
    tint_row,
    warn,
)


class TraversalTab(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.bfs_result = None
        self.dfs_result = None
        self.start = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Nodo origen:"))
        self.combo_start = QComboBox()
        controls.addWidget(self.combo_start, 1)
        btn_run = QPushButton("Ejecutar BFS y DFS")
        btn_run.clicked.connect(self.on_run)
        controls.addWidget(btn_run)
        root.addLayout(controls)

        highlight_row = QHBoxLayout()
        self.btn_show_bfs = QPushButton("Resaltar BFS en el grafo")
        self.btn_show_bfs.clicked.connect(self.on_show_bfs)
        self.btn_show_bfs.setEnabled(False)
        self.btn_show_dfs = QPushButton("Resaltar DFS en el grafo")
        self.btn_show_dfs.clicked.connect(self.on_show_dfs)
        self.btn_show_dfs.setEnabled(False)
        highlight_row.addWidget(self.btn_show_bfs)
        highlight_row.addWidget(self.btn_show_dfs)
        highlight_row.addStretch(1)
        root.addLayout(highlight_row)

        table_box = QGroupBox("Orden de visita")
        table_layout = QVBoxLayout(table_box)
        self.table = make_table(["BFS", "DFS"])
        table_layout.addWidget(self.table)
        root.addWidget(table_box, 1)

        self.lbl_unreachable = QLabel("Nodos no alcanzables: —")
        self.lbl_unreachable.setWordWrap(True)
        root.addWidget(self.lbl_unreachable)

    def refresh(self):
        populate_node_combo(self.combo_start, self.window.graph)
        self.bfs_result = None
        self.dfs_result = None
        self.table.setRowCount(0)
        self.lbl_unreachable.setText("Nodos no alcanzables: —")
        self.btn_show_bfs.setEnabled(False)
        self.btn_show_dfs.setEnabled(False)

    def on_run(self):
        grafo = self.window.require_graph()
        if grafo is None:
            return
        inicio = self.combo_start.currentData()
        if inicio is None:
            warn(self, "Seleccione un nodo de origen.")
            return
        try:
            self.bfs_result = bfs(grafo, inicio)
            self.dfs_result = dfs(grafo, inicio)
        except ValueError as exc:
            error(self, str(exc))
            return
        self.start = inicio

        filas = max(len(self.bfs_result["orden"]), len(self.dfs_result["orden"]))
        self.table.setRowCount(filas)
        for i in range(filas):
            if i < len(self.bfs_result["orden"]):
                self.table.setItem(i, 0, node_item(grafo, self.bfs_result["orden"][i]))
            if i < len(self.dfs_result["orden"]):
                self.table.setItem(i, 1, node_item(grafo, self.dfs_result["orden"][i]))
        tint_row(self.table, 0, ROW_BG_SOURCE)

        no_alcanzables = self.bfs_result["no_alcanzables"]
        self.lbl_unreachable.setText(
            "Nodos no alcanzables: " + (", ".join(no_alcanzables) if no_alcanzables else "(ninguno)")
        )
        self.btn_show_bfs.setEnabled(True)
        self.btn_show_dfs.setEnabled(True)
        self.on_show_bfs()

    def _highlight(self, resultado, nombre_algoritmo):
        run_color = next_run_color()
        node_colors = {}
        node_extra = {}
        for idx, nodo in enumerate(resultado["orden"]):
            node_colors[nodo] = COLOR_SOURCE if nodo == self.start else run_color
            node_extra[nodo] = f"#{idx}"
        for nodo in resultado["no_alcanzables"]:
            node_colors[nodo] = COLOR_UNREACHABLE

        edge_colors = {}
        for hijo, padre in resultado["arbol"].items():
            if padre is not None:
                edge_colors[(padre, hijo)] = run_color

        self.window.canvas.render_scene(
            node_colors=node_colors, edge_colors=edge_colors, node_labels_extra=node_extra
        )
        self.window.set_canvas_caption(
            f"{nombre_algoritmo} desde {self.start}: orden de visita resaltado "
            f"(número = orden), origen en morado, no alcanzables en gris."
        )

    def on_show_bfs(self):
        if self.bfs_result:
            self._highlight(self.bfs_result, "BFS")

    def on_show_dfs(self):
        if self.dfs_result:
            self._highlight(self.dfs_result, "DFS")
