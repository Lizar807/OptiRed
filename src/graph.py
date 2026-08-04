"""
graph.py
Módulo 1: Gestión del grafo.

Representa el grafo mediante una lista de adyacencia (diccionario de nodo ->
lista de [vecino, peso]). Permite crear, cargar, modificar, guardar y validar
grafos dirigidos/no dirigidos, ponderados/no ponderados y con capacidades.
"""

import os

from src.utils import (
    INF,
    es_numero,
    leer_aristas_csv,
    leer_grafo_json,
    leer_aristas_txt,
    escribir_aristas_csv,
    escribir_grafo_json,
)


class Grafo:
    def __init__(self, dirigido=True, ponderado=True, con_capacidad=False):
        self.dirigido = dirigido
        self.ponderado = ponderado
        self.con_capacidad = con_capacidad
        self.adyacencia = {}   # nodo -> lista de [vecino, peso]
        self.etiquetas = {}    # id de nodo -> nombre legible (opcional, desde JSON)
        self.descripcion = ""  # descripción del dataset (opcional, desde JSON)
        self.metadatos = {}    # metadatos extra, p.ej. {"fuente": "N01", "sumidero": "N09"}

    # ------------------------------------------------------------------ #
    # Construcción y modificación
    # ------------------------------------------------------------------ #
    def agregar_nodo(self, nodo):
        """Agrega un nodo vacío al grafo si no existe."""
        if nodo not in self.adyacencia:
            self.adyacencia[nodo] = []

    def agregar_arista(self, u, v, peso=1.0):
        """
        Agrega una arista u->v con el peso indicado. Si el grafo no es
        dirigido, también agrega la arista v->u. Crea automáticamente los
        nodos si no existen. Evita duplicados (actualiza el peso si la
        arista ya existía).
        """
        if not es_numero(peso):
            raise ValueError(f"El peso de la arista ({u}, {v}) debe ser numérico.")

        self.agregar_nodo(u)
        self.agregar_nodo(v)

        self._insertar_o_actualizar_arista(u, v, peso)
        if not self.dirigido:
            self._insertar_o_actualizar_arista(v, u, peso)

    def _insertar_o_actualizar_arista(self, u, v, peso):
        for arista in self.adyacencia[u]:
            if arista[0] == v:
                arista[1] = peso  # evita aristas duplicadas: actualiza el peso
                return
        self.adyacencia[u].append([v, peso])

    def eliminar_nodo(self, nodo):
        """Elimina un nodo y todas las aristas que lo involucran."""
        if nodo not in self.adyacencia:
            raise ValueError(f"El nodo '{nodo}' no existe en el grafo.")
        del self.adyacencia[nodo]
        for n in self.adyacencia:
            self.adyacencia[n] = [a for a in self.adyacencia[n] if a[0] != nodo]

    def eliminar_arista(self, u, v):
        """Elimina la arista u->v (y v->u si el grafo no es dirigido)."""
        if u not in self.adyacencia:
            raise ValueError(f"El nodo '{u}' no existe en el grafo.")
        self.adyacencia[u] = [a for a in self.adyacencia[u] if a[0] != v]
        if not self.dirigido and v in self.adyacencia:
            self.adyacencia[v] = [a for a in self.adyacencia[v] if a[0] != u]

    # ------------------------------------------------------------------ #
    # Consultas
    # ------------------------------------------------------------------ #
    def obtener_nodos(self):
        return list(self.adyacencia.keys())

    def obtener_aristas(self):
        """
        Devuelve la lista de aristas como tuplas (u, v, peso). En grafos no
        dirigidos, cada arista se devuelve una sola vez.
        """
        aristas = []
        vistas = set()
        for u in self.adyacencia:
            for v, w in self.adyacencia[u]:
                if self.dirigido:
                    aristas.append((u, v, w))
                else:
                    clave = tuple(sorted((u, v)))
                    if clave not in vistas:
                        vistas.add(clave)
                        aristas.append((u, v, w))
        return aristas

    def vecinos(self, nodo):
        return self.adyacencia.get(nodo, [])

    def tiene_nodo(self, nodo):
        return nodo in self.adyacencia

    def tiene_arista(self, u, v):
        return any(n == v for n, _ in self.adyacencia.get(u, []))

    def num_nodos(self):
        return len(self.adyacencia)

    def num_aristas(self):
        return len(self.obtener_aristas())

    # ------------------------------------------------------------------ #
    # Validaciones
    # ------------------------------------------------------------------ #
    def es_conexo(self):
        """
        Indica si el grafo es conexo. Para grafos dirigidos, verifica
        conectividad débil (ignorando la dirección de las aristas).
        """
        nodos = self.obtener_nodos()
        if not nodos:
            return True

        visitados = set()
        pila = [nodos[0]]
        visitados.add(nodos[0])

        # Construye una vista no dirigida para el recorrido de conectividad.
        adyacencia_no_dirigida = {n: set() for n in nodos}
        for u in self.adyacencia:
            for v, _ in self.adyacencia[u]:
                adyacencia_no_dirigida[u].add(v)
                adyacencia_no_dirigida[v].add(u)

        while pila:
            actual = pila.pop()
            for vecino in adyacencia_no_dirigida[actual]:
                if vecino not in visitados:
                    visitados.add(vecino)
                    pila.append(vecino)

        return len(visitados) == len(nodos)

    def tiene_pesos_negativos(self):
        return any(w < 0 for _, _, w in self.obtener_aristas())

    def verificar_compatibilidad(self, requiere_no_dirigido=False, requiere_ponderado=False,
                                  requiere_conexo=False, prohibir_negativos=False):
        """
        Lanza ValueError con un mensaje claro si el grafo no cumple los
        requisitos de un algoritmo determinado (advertencia de tipo de grafo
        no compatible).
        """
        if requiere_no_dirigido and self.dirigido:
            raise ValueError(
                "Este algoritmo requiere un grafo NO dirigido, pero el grafo "
                "cargado es dirigido."
            )
        if requiere_ponderado and not self.ponderado:
            raise ValueError(
                "Este algoritmo requiere un grafo ponderado, pero el grafo "
                "cargado no lo es."
            )
        if requiere_conexo and not self.es_conexo():
            raise ValueError(
                "El grafo no es conexo. No existe un árbol de expansión mínima "
                "que cubra todos los nodos; puede calcularse un bosque de "
                "expansión mínima por componentes."
            )
        if prohibir_negativos and self.tiene_pesos_negativos():
            raise ValueError(
                "Este algoritmo no admite pesos negativos. Se detectaron pesos "
                "negativos en el grafo; use Bellman-Ford o Johnson en su lugar."
            )

    # ------------------------------------------------------------------ #
    # Carga y guardado
    # ------------------------------------------------------------------ #
    @classmethod
    def cargar_desde_archivo(cls, ruta, dirigido=True, ponderado=True, con_capacidad=False):
        """
        Carga un grafo desde un archivo .csv, .txt o .json. Para .csv/.txt,
        dirigido/ponderado/con_capacidad se reciben como parámetros ya que el
        formato no los declara explícitamente. Para .json, si el archivo
        declara 'dirigido'/'ponderado', esos valores tienen prioridad.
        """
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

        ext = os.path.splitext(ruta)[1].lower()
        etiquetas, descripcion, metadatos, nodos_extra = {}, "", {}, []

        if ext == ".csv":
            aristas = leer_aristas_csv(ruta)
        elif ext == ".txt":
            aristas = leer_aristas_txt(ruta)
        elif ext == ".json":
            analizado = leer_grafo_json(ruta)
            dirigido = analizado["dirigido"]
            ponderado = analizado["ponderado"]
            con_capacidad = analizado["con_capacidad"]
            aristas = analizado["aristas"]
            etiquetas = analizado["etiquetas"]
            descripcion = analizado["descripcion"]
            metadatos = analizado["metadatos"]
            nodos_extra = analizado["nodos"]
        else:
            raise ValueError(
                f"Formato de archivo no soportado: '{ext}'. Use .csv, .txt o .json."
            )

        grafo = cls(dirigido=dirigido, ponderado=ponderado, con_capacidad=con_capacidad)
        for nodo in nodos_extra:
            grafo.agregar_nodo(nodo)  # incluye nodos aislados declarados en 'nodos'
        for u, v, w in aristas:
            grafo.agregar_arista(u, v, w if ponderado else 1.0)

        grafo.etiquetas = etiquetas
        grafo.descripcion = descripcion
        grafo.metadatos = metadatos

        print("Grafo cargado correctamente.")
        return grafo

    def guardar_en_archivo(self, ruta):
        """Guarda el grafo en formato .csv o .json según la extensión de la ruta."""
        ext = os.path.splitext(ruta)[1].lower()
        aristas = self.obtener_aristas()

        if ext == ".csv":
            escribir_aristas_csv(ruta, aristas)
        elif ext == ".json":
            escribir_grafo_json(ruta, aristas, self.dirigido, self.ponderado)
        else:
            raise ValueError(
                f"Formato de archivo no soportado para guardar: '{ext}'. Use .csv o .json."
            )

    # ------------------------------------------------------------------ #
    # Presentación
    # ------------------------------------------------------------------ #
    def describir_tipo(self):
        tipo_dir = "dirigido" if self.dirigido else "no dirigido"
        tipo_peso = "ponderado" if self.ponderado else "no ponderado"
        extra = ", con capacidades" if self.con_capacidad else ""
        return f"{tipo_dir} y {tipo_peso}{extra}"

    def imprimir_resumen(self):
        print(f"Tipo de grafo: {self.describir_tipo()}")
        print("Nodos:")
        print(", ".join(self.obtener_nodos()) if self.obtener_nodos() else "(sin nodos)")
        print("Aristas:")
        if not self.obtener_aristas():
            print("(sin aristas)")
        for u, v, w in self.obtener_aristas():
            flecha = "->" if self.dirigido else "--"
            print(f"{u} {flecha} {v} : {w}")

    def __repr__(self):
        return f"Grafo(nodos={self.num_nodos()}, aristas={self.num_aristas()}, {self.describir_tipo()})"
