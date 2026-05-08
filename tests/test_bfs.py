"""Testes unitários para o algoritmo de BFS."""

import pytest

from src.domain.graph import Graph
from src.domain.vertex import Vertex
from src.domain.edge import Edge
from src.domain.algorithms.bfs import bfs, is_reachable


def _build_graph(vertices: list[int], edges: list[tuple[int, int, float]]) -> Graph:
    g = Graph(directed=True)
    for v_id in vertices:
        g.add_vertex(Vertex(id=v_id, label=f"V{v_id}"))
    for origin, dest, weight in edges:
        g.add_edge(Edge(origin=origin, destination=dest, weight=weight))
    return g


class TestBFSCasoBase:

    def test_caso_base_visita_todos_alcancaveis(self):
        graph = _build_graph(
            vertices=[0, 1, 2, 3],
            edges=[(0, 1, 10.0), (0, 3, 5.0), (1, 2, 7.0), (3, 1, 4.0)],
        )
        result = bfs(graph, origin=0)
        assert result.reachable == {0, 1, 2, 3}

    def test_caso_base_niveis_corretos(self):
        graph = _build_graph(
            vertices=[0, 1, 2, 3],
            edges=[(0, 1, 10.0), (1, 2, 10.0), (2, 3, 10.0)],
        )
        result = bfs(graph, origin=0)
        assert result.level_of(0) == 0
        assert result.level_of(1) == 1
        assert result.level_of(2) == 2
        assert result.level_of(3) == 3


class TestBFSGrafoVazio:

    def test_grafo_sem_vertices_levanta_erro(self):
        graph = Graph()
        with pytest.raises(ValueError, match="origem 0 não existe"):
            bfs(graph, origin=0)

    def test_grafo_com_um_unico_vertice(self):
        graph = _build_graph(vertices=[0], edges=[])
        result = bfs(graph, origin=0)
        assert result.reachable == {0}
        assert result.level_of(0) == 0

    def test_grafo_sem_arestas_apenas_origem(self):
        graph = _build_graph(vertices=[0, 1, 2], edges=[])
        result = bfs(graph, origin=0)
        assert result.reachable == {0}
        assert not result.is_reachable(1)
        assert not result.is_reachable(2)


class TestBFSGrafoCompleto:

    def test_grafo_completo_todos_alcancaveis_em_um_passo(self):
        n = 5
        edges = [(i, j, 1.0) for i in range(n) for j in range(n) if i != j]
        graph = _build_graph(vertices=list(range(n)), edges=edges)
        result = bfs(graph, origin=0)
        assert result.reachable == set(range(n))
        assert result.level_of(0) == 0
        for v in range(1, n):
            assert result.level_of(v) == 1


class TestBFSCasosAdicionais:

    def test_componente_disjunto_nao_e_alcancado(self):
        graph = _build_graph(
            vertices=[0, 1, 2, 3],
            edges=[(0, 1, 5.0), (2, 3, 10.0)],
        )
        result = bfs(graph, origin=0)
        assert result.reachable == {0, 1}

    def test_direcao_e_respeitada(self):
        graph = _build_graph(vertices=[0, 1], edges=[(0, 1, 5.0)])
        assert bfs(graph, origin=0).is_reachable(1) is True
        assert bfs(graph, origin=1).is_reachable(0) is False

    def test_ciclo_nao_causa_loop(self):
        graph = _build_graph(
            vertices=[0, 1, 2],
            edges=[(0, 1, 1.0), (1, 2, 1.0), (2, 0, 1.0)],
        )
        result = bfs(graph, origin=0)
        assert result.reachable == {0, 1, 2}

    def test_is_reachable_helper_funciona(self):
        graph = _build_graph(vertices=[0, 1, 2], edges=[(0, 1, 5.0)])
        assert is_reachable(graph, 0, 1) is True
        assert is_reachable(graph, 0, 2) is False

    def test_level_of_inalcancavel_levanta_erro(self):
        graph = _build_graph(vertices=[0, 1], edges=[])
        result = bfs(graph, origin=0)
        with pytest.raises(ValueError, match="não é alcançável"):
            result.level_of(1)
