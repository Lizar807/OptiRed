"""
graph_tab.py
Pestaña del Módulo 1: gestión del grafo (crear, cargar, guardar, agregar y
eliminar nodos/aristas, mostrar nodos y aristas, indicar tipo de grafo).
"""

import os

from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt

from src.graph import Grafo
from src.gui.common import (
    error,
    info,
    make_table,
    node_item,
    node_label,
    numeric_item,
    populate_node_combo,
    warn,
)
from src.gui.dialogs import DialogoOpcionesGrafo


class GraphTab(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self._build_ui()

    # ------------------------------------------------------------------ #
    def _build_ui(self):
        root = QVBoxLayout(self)

        # --- Fila de acciones principales sobre el archivo del grafo ---
        actions = QHBoxLayout()
        btn_new = QPushButton("Nuevo grafo vacío")
        btn_new.clicked.connect(self.on_new_graph)
        btn_load = QPushButton("Cargar desde archivo…")
        btn_load.clicked.connect(self.on_load_graph)
        btn_save = QPushButton("Guardar en archivo…")
        btn_save.clicked.connect(self.on_save_graph)
        actions.addWidget(btn_new)
        actions.addWidget(btn_load)
        actions.addWidget(btn_save)
        actions.addStretch(1)
        root.addLayout(actions)

        # --- Resumen del grafo cargado ---
        self.lbl_summary = QLabel("Ningún grafo cargado todavía.")
        self.lbl_summary.setWordWrap(True)
        self.lbl_summary.setStyleSheet("font-weight: 600; padding: 6px 0;")
        root.addWidget(self.lbl_summary)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter, 1)

        # --- Columna izquierda: edición (agregar/eliminar) ---
        edit_box = QGroupBox("Agregar / eliminar")
        edit_layout = QVBoxLayout(edit_box)

        add_node_row = QHBoxLayout()
        self.txt_new_node = QLineEdit()
        self.txt_new_node.setPlaceholderText("Id del nuevo nodo, p.ej. F")
        btn_add_node = QPushButton("Agregar nodo")
        btn_add_node.clicked.connect(self.on_add_node)
        add_node_row.addWidget(self.txt_new_node)
        add_node_row.addWidget(btn_add_node)
        edit_layout.addWidget(QLabel("Agregar nodo:"))
        edit_layout.addLayout(add_node_row)

        add_edge_row = QHBoxLayout()
        self.txt_edge_u = QLineEdit()
        self.txt_edge_u.setPlaceholderText("Origen")
        self.txt_edge_v = QLineEdit()
        self.txt_edge_v.setPlaceholderText("Destino")
        self.txt_edge_w = QLineEdit()
        self.txt_edge_w.setPlaceholderText("Peso")
        btn_add_edge = QPushButton("Agregar arista")
        btn_add_edge.clicked.connect(self.on_add_edge)
        add_edge_row.addWidget(self.txt_edge_u)
        add_edge_row.addWidget(self.txt_edge_v)
        add_edge_row.addWidget(self.txt_edge_w)
        edit_layout.addWidget(QLabel("Agregar arista (origen, destino, peso):"))
        edit_layout.addLayout(add_edge_row)
        edit_layout.addWidget(btn_add_edge)

        edit_layout.addSpacing(10)

        remove_node_row = QHBoxLayout()
        self.combo_remove_node = QComboBox()
        btn_remove_node = QPushButton("Eliminar nodo")
        btn_remove_node.clicked.connect(self.on_remove_node)
        remove_node_row.addWidget(self.combo_remove_node, 1)
        remove_node_row.addWidget(btn_remove_node)
        edit_layout.addWidget(QLabel("Eliminar nodo:"))
        edit_layout.addLayout(remove_node_row)

        remove_edge_row = QHBoxLayout()
        self.combo_remove_edge_u = QComboBox()
        self.combo_remove_edge_v = QComboBox()
        btn_remove_edge = QPushButton("Eliminar arista")
        btn_remove_edge.clicked.connect(self.on_remove_edge)
        remove_edge_row.addWidget(self.combo_remove_edge_u)
        remove_edge_row.addWidget(self.combo_remove_edge_v)
        remove_edge_row.addWidget(btn_remove_edge)
        edit_layout.addWidget(QLabel("Eliminar arista:"))
        edit_layout.addLayout(remove_edge_row)

        edit_layout.addStretch(1)
        splitter.addWidget(edit_box)

        # --- Columna derecha: listas de nodos y aristas ---
        lists_box = QGroupBox("Nodos y aristas")
        lists_layout = QHBoxLayout(lists_box)

        node_col = QVBoxLayout()
        node_col.addWidget(QLabel("Nodos"))
        self.list_nodes = QListWidget()
        node_col.addWidget(self.list_nodes)
        lists_layout.addLayout(node_col)

        edge_col = QVBoxLayout()
        edge_col.addWidget(QLabel("Aristas"))
        self.table_edges = make_table(["Origen", "Destino", "Peso"], sortable=True)
        edge_col.addWidget(self.table_edges)
        lists_layout.addLayout(edge_col)

        splitter.addWidget(lists_box)
        splitter.setSizes([380, 520])

    # ------------------------------------------------------------------ #
    def data_dir(self):
        return self.window.data_dir

    def on_new_graph(self):
        dlg = DialogoOpcionesGrafo(
            self, title="Nuevo grafo vacío",
            note="Defina las propiedades del grafo vacío que se creará."
        )
        if dlg.exec():
            dirigido, ponderado, con_capacidad = dlg.valores()
            grafo = Grafo(dirigido=dirigido, ponderado=ponderado, con_capacidad=con_capacidad)
            self.window.set_graph(grafo)
            info(self, "Grafo vacío creado correctamente.")

    def on_load_graph(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Cargar grafo", self.data_dir(),
            "Archivos de grafo (*.csv *.txt *.json);;Todos los archivos (*)"
        )
        if not path:
            return

        ext = os.path.splitext(path)[1].lower()
        dirigido, ponderado, con_capacidad = False, True, False
        if ext in (".csv", ".txt"):
            dlg = DialogoOpcionesGrafo(
                self, title="Propiedades del archivo",
                note=(f"El formato '{ext}' no declara si el grafo es dirigido, "
                      f"ponderado o si tiene capacidades. Indíquelo:")
            )
            if not dlg.exec():
                return
            dirigido, ponderado, con_capacidad = dlg.valores()

        try:
            grafo = Grafo.cargar_desde_archivo(
                path, dirigido=dirigido, ponderado=ponderado, con_capacidad=con_capacidad
            )
        except (FileNotFoundError, ValueError) as exc:
            error(self, f"No se pudo cargar el grafo:\n{exc}")
            return

        self.window.set_graph(grafo)
        info(self, f"Grafo cargado correctamente desde:\n{path}")

    def on_save_graph(self):
        grafo = self.window.require_graph()
        if grafo is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar grafo", self.data_dir(),
            "CSV (*.csv);;JSON (*.json)"
        )
        if not path:
            return
        try:
            grafo.guardar_en_archivo(path)
        except ValueError as exc:
            error(self, f"No se pudo guardar el grafo:\n{exc}")
            return
        info(self, f"Grafo guardado correctamente en:\n{path}")

    def on_add_node(self):
        grafo = self.window.require_graph()
        if grafo is None:
            return
        nodo = self.txt_new_node.text().strip()
        if not nodo:
            warn(self, "Escriba el id del nodo a agregar.")
            return
        grafo.agregar_nodo(nodo)
        self.txt_new_node.clear()
        self.window.on_graph_mutated()

    def on_add_edge(self):
        grafo = self.window.require_graph()
        if grafo is None:
            return
        u = self.txt_edge_u.text().strip()
        v = self.txt_edge_v.text().strip()
        texto_peso = self.txt_edge_w.text().strip() or "1"
        if not u or not v:
            warn(self, "Indique el nodo de origen y de destino de la arista.")
            return
        try:
            peso = float(texto_peso)
        except ValueError:
            error(self, "El peso de la arista debe ser numérico.")
            return
        try:
            grafo.agregar_arista(u, v, peso)
        except ValueError as exc:
            error(self, str(exc))
            return
        self.txt_edge_u.clear()
        self.txt_edge_v.clear()
        self.txt_edge_w.clear()
        self.window.on_graph_mutated()

    def on_remove_node(self):
        grafo = self.window.require_graph()
        if grafo is None:
            return
        nodo = self.combo_remove_node.currentData()
        if nodo is None:
            warn(self, "Seleccione un nodo para eliminar.")
            return
        try:
            grafo.eliminar_nodo(nodo)
        except ValueError as exc:
            error(self, str(exc))
            return
        self.window.on_graph_mutated()

    def on_remove_edge(self):
        grafo = self.window.require_graph()
        if grafo is None:
            return
        u = self.combo_remove_edge_u.currentData()
        v = self.combo_remove_edge_v.currentData()
        if u is None or v is None:
            warn(self, "Seleccione el origen y el destino de la arista a eliminar.")
            return
        try:
            grafo.eliminar_arista(u, v)
        except ValueError as exc:
            error(self, str(exc))
            return
        self.window.on_graph_mutated()

    # ------------------------------------------------------------------ #
    def refresh(self):
        """Actualiza combos, listas y el resumen a partir del grafo actual."""
        grafo = self.window.graph
        populate_node_combo(self.combo_remove_node, grafo)
        populate_node_combo(self.combo_remove_edge_u, grafo)
        populate_node_combo(self.combo_remove_edge_v, grafo)

        self.list_nodes.clear()
        self.table_edges.setRowCount(0)

        if grafo is None:
            self.lbl_summary.setText("Ningún grafo cargado todavía.")
            return

        for nodo in grafo.obtener_nodos():
            self.list_nodes.addItem(node_label(grafo, nodo))

        aristas = grafo.obtener_aristas()
        self.table_edges.setSortingEnabled(False)
        self.table_edges.setRowCount(len(aristas))
        for row, (u, v, w) in enumerate(aristas):
            self.table_edges.setItem(row, 0, node_item(grafo, u))
            self.table_edges.setItem(row, 1, node_item(grafo, v))
            self.table_edges.setItem(row, 2, numeric_item(w, muted=False))
        self.table_edges.setSortingEnabled(True)

        conexidad = "conexo" if grafo.es_conexo() else "NO conexo"
        desc = f"\n{grafo.descripcion}" if grafo.descripcion else ""
        self.lbl_summary.setText(
            f"Tipo de grafo: {grafo.describir_tipo()}  |  Nodos: {grafo.num_nodos()}  |  "
            f"Aristas: {grafo.num_aristas()}  |  {conexidad}{desc}"
        )
