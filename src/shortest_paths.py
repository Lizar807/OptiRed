"""
shortest_paths.py
Módulo 4: Rutas más cortas desde un nodo origen mediante Dijkstra (solo pesos
no negativos) y Bellman-Ford (admite pesos negativos y detecta ciclos
negativos).
"""

from src.dynamic_structures import ColaPrioridadMinima
from src.utils import INF


def dijkstra(grafo, origen):
    """
    Ejecuta Dijkstra desde 'origen'. Requiere que el grafo no tenga pesos
    negativos (se valida antes de ejecutar).
    Devuelve {'distancias': {nodo: distancia}, 'anteriores': {nodo: nodo_anterior}}.
    """
    grafo.verificar_compatibilidad(prohibir_negativos=True)
    if not grafo.tiene_nodo(origen):
        raise ValueError(f"El nodo de origen '{origen}' no existe en el grafo.")

    distancias = {nodo: INF for nodo in grafo.obtener_nodos()}
    anteriores = {nodo: None for nodo in grafo.obtener_nodos()}
    distancias[origen] = 0

    visitados = set()
    cola_prioridad = ColaPrioridadMinima()
    cola_prioridad.insertar(0, origen)

    while not cola_prioridad.esta_vacia():
        _, actual = cola_prioridad.extraer_minimo()
        if actual in visitados:
            continue
        visitados.add(actual)

        for vecino, peso in grafo.vecinos(actual):
            if vecino in visitados:
                continue
            nueva_distancia = distancias[actual] + peso
            if nueva_distancia < distancias[vecino]:
                distancias[vecino] = nueva_distancia
                anteriores[vecino] = actual
                cola_prioridad.insertar(nueva_distancia, vecino)

    return {"distancias": distancias, "anteriores": anteriores}


def bellman_ford(grafo, origen):
    """
    Ejecuta Bellman-Ford desde 'origen'. Admite pesos negativos y detecta
    ciclos negativos alcanzables desde el origen.
    Devuelve {'distancias': {...}, 'anteriores': {...}, 'tiene_ciclo_negativo': bool}.
    Si tiene_ciclo_negativo es True, las distancias de los nodos afectados
    por el ciclo no están bien definidas.
    """
    if not grafo.tiene_nodo(origen):
        raise ValueError(f"El nodo de origen '{origen}' no existe en el grafo.")

    nodos = grafo.obtener_nodos()
    aristas = grafo.obtener_aristas()
    if not grafo.dirigido:
        # Aseguramos ambas direcciones explícitamente para la relajación.
        aristas = aristas + [(v, u, w) for u, v, w in aristas]

    distancias = {nodo: INF for nodo in nodos}
    anteriores = {nodo: None for nodo in nodos}
    distancias[origen] = 0

    for _ in range(len(nodos) - 1):
        actualizado = False
        for u, v, w in aristas:
            if distancias[u] != INF and distancias[u] + w < distancias[v]:
                distancias[v] = distancias[u] + w
                anteriores[v] = u
                actualizado = True
        if not actualizado:
            break  # convergió antes de las n-1 iteraciones

    tiene_ciclo_negativo = False
    for u, v, w in aristas:
        if distancias[u] != INF and distancias[u] + w < distancias[v]:
            tiene_ciclo_negativo = True
            break

    return {"distancias": distancias, "anteriores": anteriores, "tiene_ciclo_negativo": tiene_ciclo_negativo}


def reconstruir_camino(anteriores, origen, destino):
    """Reconstruye el camino desde 'origen' hasta 'destino' usando el diccionario
    'anteriores' devuelto por dijkstra() o bellman_ford(). Devuelve None si no hay camino."""
    if destino not in anteriores:
        return None
    camino = []
    actual = destino
    while actual is not None:
        camino.append(actual)
        actual = anteriores.get(actual)
    camino.reverse()
    if camino[0] != origen:
        return None  # no existe camino desde origen hasta destino
    return camino


def imprimir_resultado_dijkstra(resultado, grafo, origen, destino=None):
    print(f"Distancias mínimas desde {origen} usando Dijkstra:")
    for nodo, d in resultado["distancias"].items():
        print(f"{nodo} : {'INF' if d == INF else d}")
    if destino is not None:
        camino = reconstruir_camino(resultado["anteriores"], origen, destino)
        if camino:
            print(f"Camino desde {origen} hasta {destino}:")
            print(" -> ".join(camino))
            print(f"Costo total: {resultado['distancias'][destino]}")
        else:
            print(f"No existe camino desde {origen} hasta {destino}.")


def imprimir_resultado_bellman_ford(resultado, origen):
    print(f"Bellman-Ford desde {origen}:")
    if resultado["tiene_ciclo_negativo"]:
        print("Se detectó un ciclo negativo alcanzable desde el origen.")
        print("No es posible calcular rutas mínimas bien definidas.")
        return
    print("Distancias mínimas:")
    for nodo, d in resultado["distancias"].items():
        print(f"{nodo} : {'INF' if d == INF else d}")
    print("No se detectaron ciclos negativos.")
