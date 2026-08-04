"""
main.py
Punto de entrada del sistema OptiRed: Sistema de Análisis y Optimización de
Redes. Levanta la interfaz gráfica de escritorio (PyQt6) que integra los 6
módulos del sistema: gestión del grafo, recorridos BFS/DFS, árbol de
expansión mínima (Prim/Kruskal), rutas más cortas desde un origen
(Dijkstra/Bellman-Ford), caminos entre todos los pares (Floyd-Warshall/
Johnson) y flujo máximo (Ford-Fulkerson).

Ejecución:
    python main.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication

from src.gui.main_window import MainWindow

DARK_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #0f172a;
    color: #e2e8f0;
    font-family: "Segoe UI", "Ubuntu", "Cantarell", sans-serif;
    font-size: 13px;
}
QGroupBox {
    background-color: #131c31;
    border: 1px solid #334155;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: #93c5fd;
    letter-spacing: 0.3px;
}
QLabel {
    color: #e2e8f0;
}
QTabWidget::pane {
    border: 1px solid #334155;
    border-radius: 6px;
}
QTabBar::tab {
    background: #1e293b;
    padding: 8px 14px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #2563eb;
    color: white;
    font-weight: 600;
}
QPushButton {
    background-color: #2563eb;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #3b82f6;
}
QPushButton:pressed {
    background-color: #1d4ed8;
}
QPushButton:disabled {
    background-color: #334155;
    color: #94a3b8;
}
QLineEdit, QComboBox, QListWidget {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 5px;
    padding: 4px;
    selection-background-color: #2563eb;
}
QComboBox:hover, QLineEdit:hover {
    border: 1px solid #475569;
}
QComboBox::drop-down {
    border: none;
    width: 22px;
}
QComboBox QAbstractItemView {
    background-color: #1e293b;
    border: 1px solid #334155;
    selection-background-color: #2563eb;
    outline: none;
}
QHeaderView::section {
    background-color: #16213a;
    color: #93c5fd;
    font-weight: 600;
    padding: 6px;
    border: none;
    border-right: 1px solid #0f172a;
    border-bottom: 2px solid #2563eb;
}
QTableWidget {
    background-color: #18233b;
    alternate-background-color: #15203a;
    gridline-color: #263449;
    border: 1px solid #334155;
    border-radius: 6px;
    outline: none;
}
QTableWidget::item {
    padding: 5px 8px;
    border: none;
}
QTableWidget::item:selected {
    background-color: #2563eb;
    color: white;
}
QScrollBar:vertical, QScrollBar:horizontal {
    background: #0f172a;
    width: 12px;
    height: 12px;
}
QScrollBar::handle {
    background: #334155;
    border-radius: 5px;
}
QStatusBar {
    background: #1e293b;
    color: #cbd5e1;
}
"""


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
