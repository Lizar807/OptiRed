"""
all_pairs.py
Módulo 5: Caminos más cortos entre todos los pares de nodos, mediante
Floyd-Warshall (programación dinámica) y Johnson (Bellman-Ford + Dijkstra
con reponderación de aristas).

Además de la matriz de distancias, ambas funciones devuelven la información
necesaria para reconstruir el camino entre cualquier par de nodos (usada por
la interfaz gráfica para resaltar la ruta seleccionada).
"""

from src.graph import Grafo
from src.shortest_paths import bellman_ford, dijkstra, reconstruir_camino
from src.utils import INF, imprimir_tabla

NODO_AUXILIAR = "__q_aux__"


def _lista_aristas_dirigidas(grafo):
    """Devuelve todas las aristas como pares dirigidos, expandiendo ambos
    sentidos si el grafo original es no dirigido."""
    aristas = []
    for u, v, w in grafo.obtener_aristas():
        aristas.append((u, v, w))
        if not grafo.dirigido:
            aristas.append((v, u, w))
    return aristas


def floyd_warshall(grafo):
    """
    Calcula la matriz de distancias mínimas entre todos los pares de nodos.
    Devuelve {'distancias': {u: {v: distancia}}, 'tiene_ciclo_negativo': bool,
    'siguiente': {u: {v: siguiente_nodo}}}.
    """
    nodos = grafo.obtener_nodos()
    distancias = {u: {v: INF for v in nodos} for u in nodos}
    siguiente = {u: {v: None for v in nodos} for u in nodos}

    for u in nodos:
        distancias[u][u] = 0
        siguiente[u][u] = u

    for u, v, w in _lista_aristas_dirigidas(grafo):
        if w < distancias[u][v]:
            distancias[u][v] = w
            siguiente[u][v] = v

    for k in nodos:
        for i in nodos:
            if distancias[i][k] == INF:
                continue
            for j in nodos:
                candidato = distancias[i][k] + distancias[k][j]
                if candidato < distancias[i][j]:
                    distancias[i][j] = candidato
                    siguiente[i][j] = siguiente[i][k]

    tiene_ciclo_negativo = any(distancias[i][i] < 0 for i in nodos)

    return {"distancias": distancias, "tiene_ciclo_negativo": tiene_ciclo_negativo, "siguiente": siguiente}


def reconstruir_camino_floyd(siguiente, distancias, origen, destino):
    """Reconstruye el camino origen->destino a partir de la matriz 'siguiente'
    devuelta por floyd_warshall(). Devuelve None si no existe camino."""
    if distancias[origen][destino] == INF or siguiente[origen][destino] is None:
        return None
    camino = [origen]
    actual = origen
    while actual != destino:
        actual = siguiente[actual][destino]
        camino.append(actual)
    return camino


def johnson(grafo):
    """
    Calcula la matriz de distancias mínimas entre todos los pares usando el
    algoritmo de Johnson: reponderación de aristas vía Bellman-Ford desde un
    nodo auxiliar, seguida de Dijkstra desde cada nodo.
    Devuelve {'distancias': {u: {v: distancia}}, 'tiene_ciclo_negativo': bool,
    'anteriores_por_origen': {u: {v: nodo_anterior}}} donde
    'anteriores_por_origen[u]' es el diccionario de predecesores de Dijkstra
    ejecutado desde el nodo u (sobre pesos reponderados), útil para
    reconstruir caminos con reconstruir_camino().
    """
    nodos = grafo.obtener_nodos()
    aristas_originales = _lista_aristas_dirigidas(grafo)

    # Paso 1-2: grafo aumentado con nodo auxiliar q conectado a todos con peso 0.
    grafo_aumentado = Grafo(dirigido=True, ponderado=True)
    for nodo in nodos:
        grafo_aumentado.agregar_nodo(nodo)
    for u, v, w in aristas_originales:
        grafo_aumentado.agregar_arista(u, v, w)
    grafo_aumentado.agregar_nodo(NODO_AUXILIAR)
    for nodo in nodos:
        grafo_aumentado.agregar_arista(NODO_AUXILIAR, nodo, 0)

    # Paso 3-4: Bellman-Ford desde q para obtener h(v); detiene si hay ciclo negativo.
    resultado_bf = bellman_ford(grafo_aumentado, NODO_AUXILIAR)
    if resultado_bf["tiene_ciclo_negativo"]:
        return {"distancias": None, "tiene_ciclo_negativo": True, "anteriores_por_origen": None}

    h = resultado_bf["distancias"]

    # Paso 5: reponderar cada arista w'(u,v) = w(u,v) + h(u) - h(v).
    grafo_reponderado = Grafo(dirigido=True, ponderado=True)
    for nodo in nodos:
        grafo_reponderado.agregar_nodo(nodo)
    for u, v, w in aristas_originales:
        grafo_reponderado.agregar_arista(u, v, w + h[u] - h[v])

    # Paso 6-7: Dijkstra desde cada nodo con pesos reponderados y conversión
    # de vuelta a las distancias originales.
    distancias = {u: {v: INF for v in nodos} for u in nodos}
    anteriores_por_origen = {}
    for u in nodos:
        distancias[u][u] = 0

    for origen in nodos:
        resultado_dijkstra = dijkstra(grafo_reponderado, origen)
        anteriores_por_origen[origen] = resultado_dijkstra["anteriores"]
        for destino in nodos:
            d_reponderada = resultado_dijkstra["distancias"][destino]
            if d_reponderada != INF:
                distancias[origen][destino] = d_reponderada - h[origen] + h[destino]

    return {"distancias": distancias, "tiene_ciclo_negativo": False, "anteriores_por_origen": anteriores_por_origen}


def reconstruir_camino_johnson(anteriores_por_origen, origen, destino):
    """Reconstruye el camino origen->destino a partir de 'anteriores_por_origen'
    devuelto por johnson(). Devuelve None si no existe camino."""
    return reconstruir_camino(anteriores_por_origen[origen], origen, destino)


def imprimir_matriz_distancias(resultado, nodos, nombre_algoritmo):
    print(f"Matriz de distancias mínimas usando {nombre_algoritmo}:")
    if resultado["tiene_ciclo_negativo"]:
        print("Se detectó un ciclo negativo. No es posible calcular una matriz de "
              "distancias bien definida.")
        return
    encabezados = [""] + nodos
    filas = [[u] + [resultado["distancias"][u][v] for v in nodos] for u in nodos]
    imprimir_tabla(encabezados, filas)
