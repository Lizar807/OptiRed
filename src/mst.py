"""
mst.py
Módulo 3: Árboles de expansión mínima (MST) mediante los algoritmos de Prim
y Kruskal. Ambos requieren un grafo no dirigido y ponderado; si además el
grafo no es conexo, se calcula un bosque de expansión mínima por componentes.
"""

from src.dynamic_structures import ColaPrioridadMinima, ConjuntosDisjuntos


def _componentes_conexas(grafo):
    """Devuelve una lista de componentes conexas (listas de nodos)."""
    nodos = grafo.obtener_nodos()
    visitados = set()
    componentes = []

    for nodo in nodos:
        if nodo in visitados:
            continue
        componente = []
        pila = [nodo]
        visitados.add(nodo)
        while pila:
            actual = pila.pop()
            componente.append(actual)
            for vecino, _ in grafo.vecinos(actual):
                if vecino not in visitados:
                    visitados.add(vecino)
                    pila.append(vecino)
        componentes.append(componente)

    return componentes


def prim(grafo, inicio=None):
    """
    Ejecuta Prim sobre 'grafo' (o sobre cada componente conexa, si el grafo
    no es conexo, formando un bosque de expansión mínima).
    Devuelve {'aristas': [(u, v, peso), ...], 'costo': total, 'es_bosque': bool}.
    """
    grafo.verificar_compatibilidad(requiere_no_dirigido=True, requiere_ponderado=True)

    componentes = _componentes_conexas(grafo)
    es_bosque = len(componentes) > 1

    todas_las_aristas = []
    costo_total = 0.0

    for componente in componentes:
        conjunto_componente = set(componente)
        origen = componente[0] if inicio is None or inicio not in conjunto_componente else inicio
        visitados = {origen}
        cola_prioridad = ColaPrioridadMinima()
        for vecino, peso in grafo.vecinos(origen):
            cola_prioridad.insertar(peso, (origen, vecino, peso))

        while not cola_prioridad.esta_vacia() and len(visitados) < len(componente):
            peso, (u, v, w) = cola_prioridad.extraer_minimo()
            if v in visitados:
                continue
            visitados.add(v)
            todas_las_aristas.append((u, v, w))
            costo_total += w
            for vecino, peso_vecino in grafo.vecinos(v):
                if vecino not in visitados:
                    cola_prioridad.insertar(peso_vecino, (v, vecino, peso_vecino))

    return {"aristas": todas_las_aristas, "costo": costo_total, "es_bosque": es_bosque}


def kruskal(grafo):
    """
    Ejecuta Kruskal usando Conjuntos Disjuntos para detectar ciclos. Si el
    grafo no es conexo, el resultado es un bosque de expansión mínima.
    Devuelve {'aristas': [(u, v, peso), ...], 'costo': total, 'es_bosque': bool}.
    """
    grafo.verificar_compatibilidad(requiere_no_dirigido=True, requiere_ponderado=True)

    aristas = sorted(grafo.obtener_aristas(), key=lambda a: a[2])
    conjuntos = ConjuntosDisjuntos(grafo.obtener_nodos())

    aristas_seleccionadas = []
    costo_total = 0.0

    for u, v, w in aristas:
        if conjuntos.unir(u, v):
            aristas_seleccionadas.append((u, v, w))
            costo_total += w

    es_bosque = len(_componentes_conexas(grafo)) > 1

    return {"aristas": aristas_seleccionadas, "costo": costo_total, "es_bosque": es_bosque}


def imprimir_resultado_mst(resultado, nombre_algoritmo):
    print(f"Árbol de expansión mínima usando {nombre_algoritmo}:")
    if resultado["es_bosque"]:
        print("Aviso: el grafo no es conexo. Se muestra un bosque de expansión mínima.")
    print("Aristas seleccionadas:")
    for u, v, w in resultado["aristas"]:
        print(f"{u} - {v} : {w}")
    print(f"Costo total: {resultado['costo']}")
