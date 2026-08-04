"""
bfs_dfs.py
Módulo 2: Recorridos BFS (búsqueda en anchura) y DFS (búsqueda en profundidad).

Los vecinos de cada nodo se procesan en el orden en que fueron agregados al
grafo (orden de inserción en la lista de adyacencia), tanto en BFS como en DFS.
"""

from src.dynamic_structures import Cola, Pila


def bfs(grafo, inicio):
    """
    Ejecuta BFS desde 'inicio'. Devuelve un diccionario con:
      - 'orden': lista con el orden de visita
      - 'arbol': diccionario nodo -> nodo_padre (árbol de recorrido)
      - 'no_alcanzables': lista de nodos no alcanzados desde 'inicio'
    """
    if not grafo.tiene_nodo(inicio):
        raise ValueError(f"El nodo de origen '{inicio}' no existe en el grafo.")

    visitados = {inicio}
    orden = [inicio]
    arbol = {inicio: None}

    cola = Cola()
    cola.encolar(inicio)

    while not cola.esta_vacia():
        actual = cola.desencolar()
        for vecino, _ in grafo.vecinos(actual):
            if vecino not in visitados:
                visitados.add(vecino)
                orden.append(vecino)
                arbol[vecino] = actual
                cola.encolar(vecino)

    no_alcanzables = [n for n in grafo.obtener_nodos() if n not in visitados]
    return {"orden": orden, "arbol": arbol, "no_alcanzables": no_alcanzables}


def dfs(grafo, inicio):
    """
    Ejecuta DFS recursivo desde 'inicio'. Devuelve la misma estructura que
    bfs(): 'orden', 'arbol' y 'no_alcanzables'.
    """
    if not grafo.tiene_nodo(inicio):
        raise ValueError(f"El nodo de origen '{inicio}' no existe en el grafo.")

    visitados = set()
    orden = []
    arbol = {inicio: None}

    def _visitar(nodo):
        visitados.add(nodo)
        orden.append(nodo)
        for vecino, _ in grafo.vecinos(nodo):
            if vecino not in visitados:
                arbol[vecino] = nodo
                _visitar(vecino)

    _visitar(inicio)

    no_alcanzables = [n for n in grafo.obtener_nodos() if n not in visitados]
    return {"orden": orden, "arbol": arbol, "no_alcanzables": no_alcanzables}


def dfs_iterativo(grafo, inicio):
    """
    Variante iterativa de DFS usando una pila explícita (Pila), útil para
    evitar el límite de recursión en grafos grandes. Devuelve la misma
    estructura que dfs().
    """
    if not grafo.tiene_nodo(inicio):
        raise ValueError(f"El nodo de origen '{inicio}' no existe en el grafo.")

    visitados = set()
    orden = []
    arbol = {inicio: None}

    pila = Pila()
    pila.apilar(inicio)

    while not pila.esta_vacia():
        actual = pila.desapilar()
        if actual in visitados:
            continue
        visitados.add(actual)
        orden.append(actual)
        # Se apilan en orden inverso para mantener el orden de vecinos original.
        for vecino, _ in reversed(grafo.vecinos(actual)):
            if vecino not in visitados:
                if vecino not in arbol:
                    arbol[vecino] = actual
                pila.apilar(vecino)

    no_alcanzables = [n for n in grafo.obtener_nodos() if n not in visitados]
    return {"orden": orden, "arbol": arbol, "no_alcanzables": no_alcanzables}


def imprimir_resultado_recorrido(resultado, nombre_algoritmo, inicio):
    print(f"Recorrido {nombre_algoritmo} desde {inicio}:")
    print("Orden de visita:")
    print(" -> ".join(resultado["orden"]) if resultado["orden"] else "(vacío)")
    print("Nodos no alcanzables:")
    print(", ".join(resultado["no_alcanzables"]) if resultado["no_alcanzables"] else "(ninguno)")
