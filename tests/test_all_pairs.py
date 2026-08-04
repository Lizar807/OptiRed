from src.graph import Grafo
from src.all_pairs import floyd_warshall, johnson
from src.utils import INF


def construir_grafo():
    g = Grafo(dirigido=True, ponderado=True)
    g.agregar_arista("A", "B", 4)
    g.agregar_arista("A", "C", 2)
    g.agregar_arista("B", "C", 1)
    g.agregar_arista("B", "D", 5)
    g.agregar_arista("C", "D", 8)
    g.agregar_arista("D", "E", 2)
    return g


def test_floyd_warshall_coincide_con_johnson():
    g = construir_grafo()
    fw = floyd_warshall(g)
    jh = johnson(g)
    for u in g.obtener_nodos():
        for v in g.obtener_nodos():
            assert fw["distancias"][u][v] == jh["distancias"][u][v]


def test_floyd_warshall_diagonal_es_cero():
    g = construir_grafo()
    fw = floyd_warshall(g)
    for nodo in g.obtener_nodos():
        assert fw["distancias"][nodo][nodo] == 0


def test_floyd_warshall_par_no_alcanzable_es_infinito():
    g = construir_grafo()
    fw = floyd_warshall(g)
    assert fw["distancias"]["E"]["A"] == INF  # E no tiene salida hacia A


def test_johnson_detecta_ciclo_negativo():
    g = Grafo(dirigido=True, ponderado=True)
    g.agregar_arista("A", "B", 1)
    g.agregar_arista("B", "C", -1)
    g.agregar_arista("C", "A", -1)  # ciclo negativo A->B->C->A
    resultado = johnson(g)
    assert resultado["tiene_ciclo_negativo"] is True
    assert resultado["distancias"] is None
