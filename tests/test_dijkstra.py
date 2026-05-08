"""Testes unitários para o algoritmo de Dijkstra."""

import pytest

from src.domain.graph import Graph
from src.domain.vertex import Vertex
from src.domain.edge import Edge
from src.domain.algorithms.dijkstra import dijkstra, INFINITY


def _build_graph(vertices: list[int], edges: list[tuple[int, int, float]]) -> Graph:
    g = Graph(directed=True)
    for v_id in vertices:
        g.add_vertex(Vertex(id=v_id, label=f"V{v_id}"))
    for origin, dest, weight in edges:
        g.add_edge(Edge(origin=origin, destination=dest, weight=weight))
    return g


class TestDijkstraCasoBase:
    """Caso base exigido pelo enunciado do E3."""

    def test_caso_base_caminho_otimo_correto(self):
        graph = _build_graph(
            vertices=[0, 1, 2, 3],
            edges=[(0, 1, 10.0), (0, 2, 50.0), (1, 3, 20.0), (2, 1, 15.0)],
        )
        result = dijkstra(graph, origin=0)
        assert result.distances[0] == 0.0
        assert result.distances[1] == 10.0
        assert result.distances[2] == 50.0
        assert result.distances[3] == 30.0
        assert result.path_to(3) == [0, 1, 3]

    def test_caso_base_predecessores_corretos(self):
        graph = _build_graph(
            vertices=[0, 1, 2],
            edges=[(0, 1, 5.0), (1, 2, 3.0), (0, 2, 100.0)],
        )
        result = dijkstra(graph, origin=0)
        assert result.distances[2] == 8.0
        assert result.predecessors[2] == 1
        assert result.predecessors[1] == 0
        assert result.predecessors[0] is None


class TestDijkstraGrafoVazio:
    """Caso com grafo vazio exigido pelo enunciado."""

    def test_grafo_sem_vertices_levanta_erro_em_origem_inexistente(self):
        graph = Graph()
        with pytest.raises(ValueError, match="origem 0 não existe"):
            dijkstra(graph, origin=0)

    def test_grafo_com_um_unico_vertice(self):
        graph = _build_graph(vertices=[0], edges=[])
        result = dijkstra(graph, origin=0)
        assert result.distances[0] == 0.0
        assert result.path_to(0) == [0]

    def test_grafo_sem_arestas_apenas_origem_alcancavel(self):
        graph = _build_graph(vertices=[0, 1, 2], edges=[])
        result = dijkstra(graph, origin=0)
        assert result.distances[0] == 0.0
        assert result.distances[1] == INFINITY
        assert result.distances[2] == INFINITY
        assert result.is_reachable(1) is False
        assert result.path_to(1) == []


class TestDijkstraGrafoCompleto:
    """Caso com grafo completo exigido pelo enunciado."""

    def test_grafo_completo_4_vertices(self):
        n = 4
        edges = [(i, j, 10.0) for i in range(n) for j in range(n) if i != j]
        graph = _build_graph(vertices=list(range(n)), edges=edges)
        result = dijkstra(graph, origin=0)
        assert result.distances[0] == 0.0
        for v in range(1, n):
            assert result.distances[v] == 10.0
            assert result.is_reachable(v) is True

    def test_grafo_completo_com_pesos_variados(self):
        graph = _build_graph(
            vertices=[0, 1, 2, 3],
            edges=[
                (0, 1, 1.0), (0, 2, 100.0), (0, 3, 100.0),
                (1, 2, 2.0), (1, 3, 50.0),
                (2, 3, 3.0),
                (3, 2, 100.0), (3, 1, 100.0), (3, 0, 100.0),
                (2, 1, 100.0), (2, 0, 100.0), (1, 0, 100.0),
            ],
        )
        result = dijkstra(graph, origin=0)
        assert result.distances[1] == 1.0
        assert result.distances[2] == 3.0
        assert result.path_to(2) == [0, 1, 2]
        assert result.distances[3] == 6.0
        assert result.path_to(3) == [0, 1, 2, 3]


class TestDijkstraCasosAdicionais:

    def test_componente_disjunto_destino_inalcancavel(self):
        graph = _build_graph(
            vertices=[0, 1, 2, 3],
            edges=[(0, 1, 5.0), (2, 3, 10.0)],
        )
        result = dijkstra(graph, origin=0)
        assert result.distances[1] == 5.0
        assert result.distances[2] == INFINITY
        assert result.distances[3] == INFINITY

    def test_grafo_com_ciclo(self):
        graph = _build_graph(
            vertices=[0, 1, 2],
            edges=[(0, 1, 1.0), (1, 2, 1.0), (2, 0, 1.0), (2, 1, 1.0)],
        )
        result = dijkstra(graph, origin=0)
        assert result.distances[0] == 0.0
        assert result.distances[1] == 1.0
        assert result.distances[2] == 2.0

    def test_path_to_origem_retorna_lista_unitaria(self):
        graph = _build_graph(vertices=[0, 1], edges=[(0, 1, 10.0)])
        result = dijkstra(graph, origin=0)
        assert result.path_to(0) == [0]

    def test_path_to_inalcancavel_retorna_lista_vazia(self):
        graph = _build_graph(vertices=[0, 1], edges=[])
        result = dijkstra(graph, origin=0)
        assert result.path_to(1) == []

    def test_origem_inexistente_levanta_erro(self):
        graph = _build_graph(vertices=[0, 1], edges=[(0, 1, 10.0)])
        with pytest.raises(ValueError, match="origem 99 não existe"):
            dijkstra(graph, origin=99)

    def test_pesos_decimais_funcionam(self):
        graph = _build_graph(
            vertices=[0, 1, 2],
            edges=[(0, 1, 1.5), (1, 2, 2.7)],
        )
        result = dijkstra(graph, origin=0)
        assert result.distances[2] == pytest.approx(4.2)

    def test_peso_zero_funciona(self):
        graph = _build_graph(vertices=[0, 1], edges=[(0, 1, 0.0)])
        result = dijkstra(graph, origin=0)
        assert result.distances[1] == 0.0
