from src.graph import Grafo
from src.bfs_dfs import bfs, dfs, dfs_iterativo


def construir_grafo_simple():
    g = Grafo(dirigido=False, ponderado=False)
    g.agregar_arista("A", "B")
    g.agregar_arista("A", "C")
    g.agregar_arista("B", "D")
    g.agregar_arista("C", "D")
    g.agregar_arista("D", "E")
    g.agregar_nodo("F")  # nodo aislado, no alcanzable
    return g


def test_bfs_visita_todos_los_nodos_alcanzables():
    g = construir_grafo_simple()
    resultado = bfs(g, "A")
    assert resultado["orden"][0] == "A"
    assert set(resultado["orden"]) == {"A", "B", "C", "D", "E"}
    assert resultado["no_alcanzables"] == ["F"]


def test_dfs_visita_todos_los_nodos_alcanzables():
    g = construir_grafo_simple()
    resultado = dfs(g, "A")
    assert resultado["orden"][0] == "A"
    assert set(resultado["orden"]) == {"A", "B", "C", "D", "E"}
    assert resultado["no_alcanzables"] == ["F"]


def test_dfs_iterativo_coincide_con_recursivo_en_conjunto_de_nodos():
    g = construir_grafo_simple()
    resultado_recursivo = dfs(g, "A")
    resultado_iterativo = dfs_iterativo(g, "A")
    assert set(resultado_recursivo["orden"]) == set(resultado_iterativo["orden"])


def test_bfs_lanza_error_si_falta_el_nodo_de_inicio():
    g = construir_grafo_simple()
    try:
        bfs(g, "Z")
        assert False, "Debería haber lanzado ValueError"
    except ValueError:
        pass


def test_bfs_respeta_el_orden_de_insercion_de_vecinos():
    g = Grafo(dirigido=True, ponderado=False)
    g.agregar_arista("A", "C")
    g.agregar_arista("A", "B")
    resultado = bfs(g, "A")
    # Los vecinos de A se agregaron en orden C, B -> BFS debe visitarlos así.
    assert resultado["orden"] == ["A", "C", "B"]
