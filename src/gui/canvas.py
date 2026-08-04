"""
canvas.py
Widget de visualización del grafo (QGraphicsView/QGraphicsScene). Calcula una
disposición ordenada de los nodos (semilla circular + ajuste por fuerzas,
similar a Fruchterman-Reingold, con una pasada final que garantiza una
separación mínima entre nodos) y permite resaltar nodos/aristas de distintos
colores según el resultado del algoritmo ejecutado (BFS/DFS, MST, rutas,
flujo, etc.).
"""

import math
import random
import re

from PyQt6.QtCore import QLineF, QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QImage, QPainter, QPainterPath, QPen, QPolygonF
from PyQt6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QGraphicsRectItem,
)

NODE_RADIUS = 20
MIN_NODE_SEPARATION = NODE_RADIUS * 2 + 46  # deja espacio para las etiquetas

COLOR_BG = QColor("#0f172a")
COLOR_NODE_DEFAULT = QColor("#2563eb")
COLOR_NODE_TEXT = QColor("#f8fafc")
COLOR_EDGE_DEFAULT = QColor("#64748b")
COLOR_EDGE_NEGATIVE = QColor("#ef4444")
COLOR_LABEL_BG = QColor(15, 23, 42, 210)
COLOR_LABEL_TEXT = QColor("#e2e8f0")


def _natural_key(node):
    """Clave de orden 'natural' para identificadores tipo N1, N2, ..., N10:
    ordena por el número que contienen en vez de por texto (evitaría que
    'N10' quede antes que 'N2')."""
    match = re.search(r"(\d+)", str(node))
    return (int(match.group(1)) if match else 0, str(node))


def spring_layout(nodes, edges, width=1200, height=800, iterations=250, seed=7):
    """Calcula posiciones (x, y) para cada nodo de manera ordenada:

    1. Semilla inicial: los nodos se ubican en un círculo, ordenados por su
       identificador, en vez de en posiciones aleatorias. Esto evita el
       aspecto "desordenado" de una semilla puramente al azar.
    2. Ajuste por fuerzas (repulsión entre todos los nodos, atracción entre
       nodos conectados) para agrupar visualmente a los nodos relacionados.
    3. Resolución final de superposiciones: una pasada adicional que separa
       a la fuerza cualquier par de nodos que haya quedado demasiado cerca,
       garantizando que ningún nodo ni su etiqueta se encimen con otro.

    El resultado es determinístico gracias a la semilla fija."""
    if not nodes:
        return {}

    cx, cy = width / 2, height / 2
    ordered = sorted(nodes, key=_natural_key)
    n = len(ordered)
    seed_radius = max(140, min(width, height) * 0.34)
    rnd = random.Random(seed)

    pos = {}
    for i, node in enumerate(ordered):
        angle = 2 * math.pi * i / n
        jitter = rnd.uniform(-0.03, 0.03) * seed_radius
        pos[node] = [
            cx + (seed_radius + jitter) * math.cos(angle),
            cy + (seed_radius + jitter) * math.sin(angle),
        ]

    if n == 1:
        pos[nodes[0]] = [cx, cy]
        return pos

    area = width * height
    k = math.sqrt(area / n) * 1.05

    for it in range(iterations):
        disp = {n_: [0.0, 0.0] for n_ in nodes}

        for i, u in enumerate(nodes):
            for v in nodes[i + 1:]:
                dx = pos[u][0] - pos[v][0]
                dy = pos[u][1] - pos[v][1]
                dist = math.hypot(dx, dy) or 0.01
                force = (k * k) / dist
                ux, uy = dx / dist, dy / dist
                disp[u][0] += ux * force
                disp[u][1] += uy * force
                disp[v][0] -= ux * force
                disp[v][1] -= uy * force

        for u, v, _ in edges:
            if u not in pos or v not in pos or u == v:
                continue
            dx = pos[u][0] - pos[v][0]
            dy = pos[u][1] - pos[v][1]
            dist = math.hypot(dx, dy) or 0.01
            force = (dist * dist) / k
            ux, uy = dx / dist, dy / dist
            disp[u][0] -= ux * force
            disp[u][1] -= uy * force
            disp[v][0] += ux * force
            disp[v][1] += uy * force

        temperature = max(0.02, 1.0 - it / iterations) * k
        for node in nodes:
            dx, dy = disp[node]
            dist = math.hypot(dx, dy) or 0.01
            limited = min(dist, temperature)
            pos[node][0] += dx / dist * limited
            pos[node][1] += dy / dist * limited
            pos[node][0] = min(max(pos[node][0], NODE_RADIUS + 30), width - NODE_RADIUS - 30)
            pos[node][1] = min(max(pos[node][1], NODE_RADIUS + 30), height - NODE_RADIUS - 30)

    # Pasada final: separa cualquier par de nodos que haya quedado más cerca
    # que la distancia mínima permitida, para que ningún nodo ni su etiqueta
    # se encimen con otro (esto es lo que hace que el mapa se vea ordenado
    # incluso en grafos densos).
    for _ in range(80):
        moved = False
        for i, u in enumerate(nodes):
            for v in nodes[i + 1:]:
                dx = pos[u][0] - pos[v][0]
                dy = pos[u][1] - pos[v][1]
                dist = math.hypot(dx, dy)
                if dist < MIN_NODE_SEPARATION:
                    if dist < 1e-6:
                        # Dos nodos coinciden exactamente: no hay una dirección
                        # de separación definida por la resta de posiciones, así
                        # que se usa un ángulo determinístico derivado de sus
                        # identificadores para poder separarlos igualmente.
                        angulo = (hash((u, v)) % 360) * math.pi / 180
                        ux, uy = math.cos(angulo), math.sin(angulo)
                        dist = 0.0
                    else:
                        ux, uy = dx / dist, dy / dist
                    push = (MIN_NODE_SEPARATION - dist) / 2 + 0.5
                    pos[u][0] += ux * push
                    pos[u][1] += uy * push
                    pos[v][0] -= ux * push
                    pos[v][1] -= uy * push
                    moved = True
        for node in nodes:
            pos[node][0] = min(max(pos[node][0], NODE_RADIUS + 30), width - NODE_RADIUS - 30)
            pos[node][1] = min(max(pos[node][1], NODE_RADIUS + 30), height - NODE_RADIUS - 30)
        if not moved:
            break

    return pos


class GraphCanvas(QGraphicsView):
    """Lienzo interactivo que dibuja el grafo cargado y resalta resultados de
    los algoritmos (colores de nodos/aristas y etiquetas adicionales)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene_ = QGraphicsScene(self)
        self.setScene(self.scene_)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setBackgroundBrush(QBrush(COLOR_BG))
        self.setMinimumHeight(360)

        self.graph = None
        self.positions = {}
        self.canvas_w = 1200
        self.canvas_h = 800

    # ------------------------------------------------------------------ #
    def set_graph(self, grafo):
        self.graph = grafo
        if grafo is None:
            self.positions = {}
            self.render_scene()
            return
        nodos = grafo.obtener_nodos()
        aristas = grafo.obtener_aristas()
        self.positions = spring_layout(nodos, aristas, self.canvas_w, self.canvas_h)
        self.render_scene()
        self.fit_view()

    def wheelEvent(self, event):
        # Zoom por defecto del lienzo (rueda del mouse); no hay botones de
        # zoom manual: al cargar un grafo la vista siempre se ajusta sola
        # mediante fit_view().
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    def fit_view(self):
        """Ajusta el zoom por defecto para que todo el grafo sea visible en
        el lienzo (se llama automáticamente al cargar un grafo)."""
        self.resetTransform()
        if self.scene_.itemsBoundingRect().isValid():
            self.fitInView(
                self.scene_.itemsBoundingRect().adjusted(-30, -30, 30, 30),
                Qt.AspectRatioMode.KeepAspectRatio,
            )

    def export_image(self, path):
        """Exporta el contenido actual del lienzo a un archivo PNG/JPG."""
        rect = self.scene_.itemsBoundingRect().adjusted(-20, -20, 20, 20)
        if not rect.isValid():
            rect = QRectF(0, 0, self.canvas_w, self.canvas_h)
        image = QImage(int(rect.width()), int(rect.height()), QImage.Format.Format_ARGB32)
        image.fill(COLOR_BG)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.scene_.render(painter, QRectF(image.rect()), rect)
        painter.end()
        return image.save(path)

    # ------------------------------------------------------------------ #
    def render_scene(self, node_colors=None, edge_colors=None, edge_extra=None,
                      node_labels_extra=None):
        """Vuelve a dibujar el grafo. node_colors: {nodo: QColor};
        edge_colors: {(u, v): QColor} (para no dirigidos alcanza un sentido);
        edge_extra: {(u, v): texto extra a mostrar tras el peso};
        node_labels_extra: {nodo: texto extra bajo la etiqueta, p.ej. orden BFS}."""
        self.scene_.clear()
        self.scene_.setSceneRect(QRectF(0, 0, self.canvas_w, self.canvas_h))

        if self.graph is None or not self.graph.obtener_nodos():
            msg = QGraphicsSimpleTextItem("Cargue o cree un grafo para visualizarlo aquí.")
            msg.setBrush(QBrush(QColor("#94a3b8")))
            msg.setFont(QFont("Segoe UI", 12))
            msg.setPos(30, 30)
            self.scene_.addItem(msg)
            return

        node_colors = node_colors or {}
        edge_colors = edge_colors or {}
        edge_extra = edge_extra or {}
        node_labels_extra = node_labels_extra or {}
        dirigido = self.graph.dirigido

        drawn_undirected = set()
        normal_edges = []
        highlighted_edges = []
        for u, v, w in self.graph.obtener_aristas():
            if u not in self.positions or v not in self.positions:
                continue
            if not dirigido:
                key = tuple(sorted((u, v)))
                if key in drawn_undirected:
                    continue
                drawn_undirected.add(key)

            color = edge_colors.get((u, v)) or edge_colors.get((v, u))
            is_highlighted = color is not None
            if color is None:
                color = COLOR_EDGE_NEGATIVE if w < 0 else COLOR_EDGE_DEFAULT
            extra = edge_extra.get((u, v)) or edge_extra.get((v, u))
            item = (u, v, w, color, extra)
            (highlighted_edges if is_highlighted else normal_edges).append(item)

        # Las aristas normales se dibujan primero para que las resaltadas
        # queden siempre visibles por encima, sin que otras líneas las tapen.
        for u, v, w, color, extra in normal_edges:
            self._draw_edge(u, v, w, color, 1.6, dirigido, extra, highlighted=False)
        for u, v, w, color, extra in highlighted_edges:
            self._draw_edge(u, v, w, color, 3.2, dirigido, extra, highlighted=True)

        for node in self.graph.obtener_nodos():
            if node not in self.positions:
                continue
            color = node_colors.get(node, COLOR_NODE_DEFAULT)
            label = self.graph.etiquetas.get(node) if self.graph.etiquetas else None
            extra = node_labels_extra.get(node)
            self._draw_node(node, color, label, extra)

    # ------------------------------------------------------------------ #
    def _draw_edge(self, u, v, w, color, width, is_directed, extra_text, highlighted=False):
        x1, y1 = self.positions[u]
        x2, y2 = self.positions[v]
        line = QLineF(x1, y1, x2, y2)
        length = line.length() or 1.0
        dx, dy = (x2 - x1) / length, (y2 - y1) / length

        start = QPointF(x1 + dx * NODE_RADIUS, y1 + dy * NODE_RADIUS)
        end = QPointF(x2 - dx * NODE_RADIUS, y2 - dy * NODE_RADIUS)

        z = 1.0 if highlighted else 0.0
        if highlighted:
            # Halo translúcido debajo de la línea principal para que el
            # camino/arista resaltada destaque incluso sobre un grafo denso.
            halo_color = QColor(color)
            halo_color.setAlpha(70)
            halo_pen = QPen(halo_color, width + 5)
            halo_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            halo = self.scene_.addLine(QLineF(start, end), halo_pen)
            halo.setZValue(z - 0.1)

        pen = QPen(color, width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        edge_item = self.scene_.addLine(QLineF(start, end), pen)
        edge_item.setZValue(z)

        if is_directed:
            arrow_size = 9
            back = QPointF(end.x() - dx * arrow_size, end.y() - dy * arrow_size)
            perp_x, perp_y = -dy, dx
            p1 = QPointF(back.x() + perp_x * (arrow_size * 0.55),
                         back.y() + perp_y * (arrow_size * 0.55))
            p2 = QPointF(back.x() - perp_x * (arrow_size * 0.55),
                         back.y() - perp_y * (arrow_size * 0.55))
            poly = QPolygonF([end, p1, p2])
            arrow_item = self.scene_.addPolygon(poly, QPen(color), QBrush(color))
            arrow_item.setZValue(z + 0.1)

        mid_x, mid_y = (start.x() + end.x()) / 2, (start.y() + end.y()) / 2
        label_text = f"{_fmt(w)}" + (f" ({extra_text})" if extra_text else "")
        self._add_label(mid_x, mid_y, label_text, small=True, z=z + 0.2)

    def _draw_node(self, node, color, label, extra):
        x, y = self.positions[node]
        is_highlighted = color != COLOR_NODE_DEFAULT
        ellipse = QGraphicsEllipseItem(x - NODE_RADIUS, y - NODE_RADIUS,
                                        NODE_RADIUS * 2, NODE_RADIUS * 2)
        ellipse.setBrush(QBrush(color))
        border = QColor("#fef9c3") if is_highlighted else QColor("#e2e8f0")
        ellipse.setPen(QPen(border, 2.4 if is_highlighted else 1.4))
        ellipse.setZValue(2)
        self.scene_.addItem(ellipse)

        text = QGraphicsSimpleTextItem(str(node))
        text.setBrush(QBrush(COLOR_NODE_TEXT))
        font = QFont("Segoe UI", 8, QFont.Weight.Bold)
        text.setFont(font)
        text.setZValue(3)
        rect = text.boundingRect()
        text.setPos(x - rect.width() / 2, y - rect.height() / 2)
        self.scene_.addItem(text)

        below = y + NODE_RADIUS + 4
        if label:
            self._add_label(x, below, label, small=True)
            below += 14
        if extra:
            self._add_label(x, below, str(extra), small=True, accent=True)

    def _add_label(self, x, y, text, small=False, accent=False, z=4):
        item = QGraphicsSimpleTextItem(text)
        item.setBrush(QBrush(QColor("#fbbf24") if accent else COLOR_LABEL_TEXT))
        item.setFont(QFont("Segoe UI", 7 if small else 9))
        item.setZValue(z)
        rect = item.boundingRect()
        item.setPos(x - rect.width() / 2, y - rect.height() / 2)

        bg = QGraphicsRectItem(item.x() - 2, item.y() - 1, rect.width() + 4, rect.height() + 2)
        bg.setBrush(QBrush(COLOR_LABEL_BG))
        bg.setPen(QPen(Qt.PenStyle.NoPen))
        bg.setZValue(z - 0.05)
        self.scene_.addItem(bg)
        self.scene_.addItem(item)


def _fmt(value):
    if value == float("inf"):
        return "INF"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)
