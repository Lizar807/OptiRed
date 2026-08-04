"""
dynamic_structures.py
Estructuras de datos dinámicas utilizadas por los algoritmos del sistema:
Cola (para BFS), Pila (para DFS iterativo), Conjuntos Disjuntos / Union-Find
(para Kruskal) y una Cola de Prioridad mínima (para Prim, Dijkstra y Johnson).
"""

from collections import deque
import heapq


class Cola:
    """Cola FIFO simple, usada por BFS."""

    def __init__(self):
        self._elementos = deque()

    def encolar(self, elemento):
        self._elementos.append(elemento)

    def desencolar(self):
        return self._elementos.popleft()

    def esta_vacia(self):
        return len(self._elementos) == 0

    def __len__(self):
        return len(self._elementos)


class Pila:
    """Pila LIFO simple, usada por DFS iterativo."""

    def __init__(self):
        self._elementos = []

    def apilar(self, elemento):
        self._elementos.append(elemento)

    def desapilar(self):
        return self._elementos.pop()

    def ver_tope(self):
        return self._elementos[-1]

    def esta_vacia(self):
        return len(self._elementos) == 0

    def __len__(self):
        return len(self._elementos)


class ConjuntosDisjuntos:
    """
    Estructura Union-Find (Conjuntos Disjuntos) con compresión de caminos y
    unión por rango. Se usa en Kruskal para detectar ciclos de forma eficiente.
    """

    def __init__(self, elementos):
        self.padre = {e: e for e in elementos}
        self.rango = {e: 0 for e in elementos}

    def encontrar(self, x):
        if self.padre[x] != x:
            self.padre[x] = self.encontrar(self.padre[x])  # compresión de camino
        return self.padre[x]

    def unir(self, x, y):
        """Une los conjuntos de x e y. Devuelve False si ya estaban en el mismo
        conjunto (lo que indicaría un ciclo), True si la unión se realizó."""
        raiz_x, raiz_y = self.encontrar(x), self.encontrar(y)
        if raiz_x == raiz_y:
            return False
        if self.rango[raiz_x] < self.rango[raiz_y]:
            raiz_x, raiz_y = raiz_y, raiz_x
        self.padre[raiz_y] = raiz_x
        if self.rango[raiz_x] == self.rango[raiz_y]:
            self.rango[raiz_x] += 1
        return True

    def conectados(self, x, y):
        return self.encontrar(x) == self.encontrar(y)


class ColaPrioridadMinima:
    """
    Cola de prioridad mínima basada en heapq, usada por Prim, Dijkstra y
    Johnson. Cada elemento se inserta como (prioridad, contador, elemento); el
    contador evita comparar el elemento directamente cuando dos prioridades
    empatan.
    """

    def __init__(self):
        self._monticulo = []
        self._contador = 0

    def insertar(self, prioridad, elemento):
        heapq.heappush(self._monticulo, (prioridad, self._contador, elemento))
        self._contador += 1

    def extraer_minimo(self):
        prioridad, _, elemento = heapq.heappop(self._monticulo)
        return prioridad, elemento

    def esta_vacia(self):
        return len(self._monticulo) == 0

    def __len__(self):
        return len(self._monticulo)
