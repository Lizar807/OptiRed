from src.graph import Grafo
from src.max_flow import ford_fulkerson


def construir_grafo_de_flujo():
    """Red de flujo tomada del ejemplo del enunciado (sección 2.6): dos rutas
    S-A-C-T y S-B-D-T, con flujo máximo esperado de 23."""
    g = Grafo(dirigido=True, ponderado=True, con_capacidad=True)
    g.agregar_arista("S", "A", 16)
    g.agregar_arista("S", "B", 13)
    g.agregar_arista("A", "C", 12)
    g.agregar_arista("B", "D", 14)
    g.agregar_arista("C", "T", 20)
    g.agregar_arista("D", "T", 11)
    return g


def test_flujo_maximo_ejemplo_clasico():
    g = construir_grafo_de_flujo()
    resultado = ford_fulkerson(g, "S", "T")
    assert resultado["flujo_maximo"] == 23
    assert resultado["tiene_camino"] is True


def test_flujo_maximo_respeta_capacidades():
    g = construir_grafo_de_flujo()
    resultado = ford_fulkerson(g, "S", "T")
    for (u, v), (usado, cap) in resultado["flujo_por_arista"].items():
        assert usado <= cap + 1e-9


def test_sin_camino_devuelve_flujo_cero():
    g = Grafo(dirigido=True, ponderado=True, con_capacidad=True)
    g.agregar_arista("S", "A", 5)
    g.agregar_nodo("T")  # sin conexión hacia T
    resultado = ford_fulkerson(g, "S", "T")
    assert resultado["flujo_maximo"] == 0
    assert resultado["tiene_camino"] is False
