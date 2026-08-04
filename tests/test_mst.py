import pytest

from src.graph import Grafo
from src.mst import prim, kruskal


def construir_grafo_mst():
    g = Grafo(dirigido=False, ponderado=True)
    g.agregar_arista("A", "B", 4)
    g.agregar_arista("A", "C", 2)
    g.agregar_arista("B", "D", 5)
    g.agregar_arista("C", "D", 1)
    g.agregar_arista("D", "E", 3)
    return g


def test_costo_total_de_kruskal():
    g = construir_grafo_mst()
    resultado = kruskal(g)
    assert resultado["costo"] == 10
    assert len(resultado["aristas"]) == 4
    assert resultado["es_bosque"] is False


def test_costo_de_prim_coincide_con_kruskal():
    g = construir_grafo_mst()
    resultado_prim = prim(g)
    resultado_kruskal = kruskal(g)
    assert resultado_prim["costo"] == resultado_kruskal["costo"]


def test_mst_rechaza_grafo_dirigido():
    g = Grafo(dirigido=True, ponderado=True)
    g.agregar_arista("A", "B", 1)
    with pytest.raises(ValueError):
        kruskal(g)


def test_mst_grafo_no_conexo_devuelve_bosque():
    g = Grafo(dirigido=False, ponderado=True)
    g.agregar_arista("A", "B", 1)
    g.agregar_arista("C", "D", 2)  # componente separada
    resultado = kruskal(g)
    assert resultado["es_bosque"] is True
    assert resultado["costo"] == 3
