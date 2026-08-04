import pytest

from src.graph import Grafo
from src.shortest_paths import dijkstra, bellman_ford, reconstruir_camino
from src.utils import INF


def construir_grafo_positivo():
    g = Grafo(dirigido=True, ponderado=True)
    g.agregar_arista("A", "B", 4)
    g.agregar_arista("A", "C", 2)
    g.agregar_arista("C", "B", 1)
    g.agregar_arista("B", "D", 5)
    g.agregar_arista("C", "D", 8)
    g.agregar_arista("D", "E", 3)
    return g


def test_distancia_minima_de_dijkstra():
    g = construir_grafo_positivo()
    resultado = dijkstra(g, "A")
    assert resultado["distancias"]["D"] == 8  # A->C->B->D = 2+1+5
    camino = reconstruir_camino(resultado["anteriores"], "A", "D")
    assert camino == ["A", "C", "B", "D"]


def test_dijkstra_rechaza_pesos_negativos():
    g = Grafo(dirigido=True, ponderado=True)
    g.agregar_arista("A", "B", -1)
    with pytest.raises(ValueError):
        dijkstra(g, "A")


def test_bellman_ford_admite_pesos_negativos():
    g = construir_grafo_positivo()
    g.agregar_arista("C", "B", -3)  # sobreescribe con peso negativo
    resultado = bellman_ford(g, "A")
    assert resultado["tiene_ciclo_negativo"] is False
    assert resultado["distancias"]["B"] == -1  # A->C->B = 2 + (-3)


def test_bellman_ford_detecta_ciclo_negativo():
    g = Grafo(dirigido=True, ponderado=True)
    g.agregar_arista("A", "B", 1)
    g.agregar_arista("B", "C", -1)
    g.agregar_arista("C", "D", -1)
    g.agregar_arista("D", "B", -1)  # ciclo B->C->D->B con peso -3
    resultado = bellman_ford(g, "A")
    assert resultado["tiene_ciclo_negativo"] is True


def test_nodo_no_alcanzable_tiene_distancia_infinita():
    g = construir_grafo_positivo()
    g.agregar_nodo("Z")
    resultado = dijkstra(g, "A")
    assert resultado["distancias"]["Z"] == INF
    assert reconstruir_camino(resultado["anteriores"], "A", "Z") is None
