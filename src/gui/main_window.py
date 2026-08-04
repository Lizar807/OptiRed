"""
main_window.py
Ventana principal de OptiRed. Integra el lienzo de visualización del grafo
(siempre visible) con seis pestañas, una por cada módulo funcional del
sistema: gestión del grafo, BFS/DFS, MST, rutas desde un origen, caminos
entre todos los pares y flujo máximo.
"""

import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.gui.all_pairs_tab import AllPairsTab
from src.gui.canvas import GraphCanvas
from src.gui.graph_tab import GraphTab
from src.gui.max_flow_tab import MaxFlowTab
from src.gui.mst_tab import MstTab
from src.gui.shortest_path_tab import ShortestPathTab
from src.gui.traversal_tab import TraversalTab

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OptiRed — Sistema de Análisis y Optimización de Redes")
        self.resize(1360, 860)

        self.data_dir = DATA_DIR if os.path.isdir(DATA_DIR) else os.getcwd()
        self.graph = None

        self._build_ui()

    # ------------------------------------------------------------------ #
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        outer.addWidget(splitter)

        # --- Pestañas de los 6 módulos ---
        self.tabs = QTabWidget()
        self.graph_tab = GraphTab(self)
        self.traversal_tab = TraversalTab(self)
        self.mst_tab = MstTab(self)
        self.shortest_path_tab = ShortestPathTab(self)
        self.all_pairs_tab = AllPairsTab(self)
        self.max_flow_tab = MaxFlowTab(self)

        self.tabs.addTab(self.graph_tab, "1 · Grafo")
        self.tabs.addTab(self.traversal_tab, "2 · BFS / DFS")
        self.tabs.addTab(self.mst_tab, "3 · MST")
        self.tabs.addTab(self.shortest_path_tab, "4 · Rutas desde origen")
        self.tabs.addTab(self.all_pairs_tab, "5 · Todos los pares")
        self.tabs.addTab(self.max_flow_tab, "6 · Flujo máximo")
        splitter.addWidget(self.tabs)

        self._tabs_list = [
            self.graph_tab,
            self.traversal_tab,
            self.mst_tab,
            self.shortest_path_tab,
            self.all_pairs_tab,
            self.max_flow_tab,
        ]

        # --- Panel derecho: visualización permanente del grafo ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        title_row = QHBoxLayout()
        title = QLabel("Visualización del grafo")
        title.setStyleSheet("font-size: 14px; font-weight: 700; padding: 4px 0;")
        title_row.addWidget(title)
        title_row.addStretch(1)

        btn_fit = QPushButton("Ajustar a la vista")
        btn_fit.clicked.connect(lambda: self.canvas.fit_view())

        btn_export = QPushButton("Exportar imagen…")
        btn_export.clicked.connect(self.on_export_image)

        for btn in (btn_fit, btn_export):
            title_row.addWidget(btn)
        right_layout.addLayout(title_row)

        self.canvas = GraphCanvas()
        right_layout.addWidget(self.canvas, 1)

        self.lbl_caption = QLabel(
            "Cargue un grafo desde la pestaña «1 · Grafo» para comenzar. "
            "La vista se ajusta sola; use la rueda del mouse para hacer zoom "
            "y arrastre para desplazarse."
        )
        self.lbl_caption.setWordWrap(True)
        self.lbl_caption.setStyleSheet("color: #cbd5e1; padding: 4px 2px;")
        right_layout.addWidget(self.lbl_caption)

        splitter.addWidget(right_panel)
        splitter.setSizes([560, 780])

        self.statusBar().showMessage("Listo.")

    # ------------------------------------------------------------------ #
    def set_graph(self, graph):
        """Reemplaza el grafo actual (nuevo/cargado) y refresca toda la UI."""
        self.graph = graph
        self.canvas.set_graph(graph)
        self.set_canvas_caption(
            "Grafo cargado. Ejecute un algoritmo desde cualquier pestaña para "
            "resaltar su resultado aquí."
        )
        self.refresh_all_tabs()
        self._update_status()

    def on_graph_mutated(self):
        """Se llama tras agregar/eliminar nodos o aristas: conserva la misma
        referencia de grafo pero recalcula la disposición y refresca la UI."""
        self.canvas.set_graph(self.graph)
        self.refresh_all_tabs()
        self._update_status()

    def refresh_all_tabs(self):
        for tab in self._tabs_list:
            tab.refresh()

    def require_graph(self):
        """Devuelve el grafo actual, o muestra un aviso y devuelve None si
        todavía no se ha cargado/creado ninguno."""
        if self.graph is None:
            QMessageBox.warning(
                self, "Aviso", "Primero debe crear o cargar un grafo en la pestaña «1 · Grafo»."
            )
            return None
        return self.graph

    def set_canvas_caption(self, text):
        self.lbl_caption.setText(text)

    def on_export_image(self):
        if self.graph is None or not self.graph.obtener_nodos():
            QMessageBox.warning(self, "Aviso", "Primero cargue o cree un grafo para exportarlo.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar imagen del grafo", os.path.join(self.data_dir, "grafo.png"),
            "Imagen PNG (*.png);;Imagen JPEG (*.jpg)",
        )
        if not path:
            return
        if self.canvas.export_image(path):
            self.statusBar().showMessage(f"Imagen exportada: {path}", 6000)
        else:
            QMessageBox.critical(self, "Error", "No se pudo exportar la imagen.")

    def _update_status(self):
        if self.graph is None:
            self.statusBar().showMessage("Listo.")
            return
        self.statusBar().showMessage(
            f"Grafo actual: {self.graph.describir_tipo()} · "
            f"{self.graph.num_nodos()} nodos · {self.graph.num_aristas()} aristas"
        )
