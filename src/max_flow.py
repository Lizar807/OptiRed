"""
max_flow.py
Módulo 6: Flujo máximo mediante el algoritmo de Ford-Fulkerson. La búsqueda
de caminos aumentantes se realiza con BFS (variante conocida como
Edmonds-Karp), lo que garantiza que el algoritmo termine en tiempo polinomial.
"""

from collections import defaultdict, deque


def _bfs_buscar_camino_aumentante(capacidad, fuente, sumidero, nodos):
    """Busca un camino desde fuente hasta sumidero con capacidad residual > 0.
    Devuelve la lista de nodos del camino, o None si no existe."""
    padre = {fuente: None}
    visitados = {fuente}
    cola = deque([fuente])

    while cola:
        actual = cola.popleft()
        if actual == sumidero:
            break
        for vecino in nodos:
            if vecino not in visitados and capacidad[actual][vecino] > 0:
                visitados.add(vecino)
                padre[vecino] = actual
                cola.append(vecino)

    if sumidero not in padre:
        return None

    camino = []
    nodo = sumidero
    while nodo is not None:
        camino.append(nodo)
        nodo = padre[nodo]
    camino.reverse()
    return camino


def ford_fulkerson(grafo, fuente, sumidero):
    """
    Calcula el flujo máximo desde 'fuente' hasta 'sumidero'. Los pesos de las
    aristas del grafo se interpretan como capacidades máximas.
    Devuelve {'flujo_maximo': valor, 'flujo_por_arista': {(u, v): (flujo, capacidad)},
    'tiene_camino': bool}.
    """
    if not grafo.tiene_nodo(fuente):
        raise ValueError(f"El nodo fuente '{fuente}' no existe en el grafo.")
    if not grafo.tiene_nodo(sumidero):
        raise ValueError(f"El nodo sumidero '{sumidero}' no existe en el grafo.")

    nodos = grafo.obtener_nodos()
    capacidad_original = defaultdict(float)
    capacidad = defaultdict(lambda: defaultdict(float))

    for u, v, w in grafo.obtener_aristas():
        capacidad_original[(u, v)] += w
        capacidad[u][v] += w
        capacidad[v].setdefault(u, capacidad[v][u])  # asegura arista residual inversa

    primer_camino = _bfs_buscar_camino_aumentante(capacidad, fuente, sumidero, nodos)
    if primer_camino is None:
        return {"flujo_maximo": 0, "flujo_por_arista": {}, "tiene_camino": False}

    flujo_maximo = 0
    camino = primer_camino
    while camino is not None:
        capacidad_camino = min(capacidad[u][v] for u, v in zip(camino, camino[1:]))
        for u, v in zip(camino, camino[1:]):
            capacidad[u][v] -= capacidad_camino
            capacidad[v][u] += capacidad_camino
        flujo_maximo += capacidad_camino
        camino = _bfs_buscar_camino_aumentante(capacidad, fuente, sumidero, nodos)

    flujo_por_arista = {}
    for (u, v), cap in capacidad_original.items():
        usado = cap - capacidad[u][v]
        if usado > 1e-9:
            flujo_por_arista[(u, v)] = (usado, cap)

    return {"flujo_maximo": flujo_maximo, "flujo_por_arista": flujo_por_arista, "tiene_camino": True}


def imprimir_resultado_flujo_maximo(resultado, fuente, sumidero):
    print(f"Fuente: {fuente}")
    print(f"Sumidero: {sumidero}")
    if not resultado["tiene_camino"]:
        print(f"No existe camino desde {fuente} hasta {sumidero}.")
        return
    print(f"Flujo máximo encontrado: {resultado['flujo_maximo']}")
    print("Flujo por arista:")
    for (u, v), (usado, cap) in resultado["flujo_por_arista"].items():
        usado_str = int(usado) if float(usado).is_integer() else usado
        cap_str = int(cap) if float(cap).is_integer() else cap
        print(f"{u} -> {v} : {usado_str}/{cap_str}")
