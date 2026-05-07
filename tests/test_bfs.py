"""
Testes unitários para o algoritmo de BFS.

Casos exigidos pelo enunciado do E3:
    - Caso base: entrada válida com resultado esperado conhecido.
    - Grafo vazio: comportamento com entrada vazia ou nula.
    - Grafo completo: todos os vértices conectados entre si.
"""

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


# ===================================================================
# CASO 1 — CASO BASE
# ===================================================================

class TestBFSCasoBase:
    """Caso base: grafo conhecido com resultado esperado verificável."""

    def test_caso_base_visita_todos_alcancaveis(self):
        """
        Grafo:  0 -> 1 -> 2
                |    ^
                v    |
                3 ---+

        A partir de 0, todos são alcançáveis.
        """
        graph = _build_graph(
            vertices=[0, 1, 2, 3],
            edges=[
                (0, 1, 10.0),
                (0, 3, 5.0),
                (1, 2, 7.0),
                (3, 1, 4.0),
            ],
        )
        result = bfs(graph, origin=0)
        assert result.reachable == {0, 1, 2, 3}

    def test_caso_base_niveis_corretos(self):
        """
        Grafo:  0 -> 1 -> 2 -> 3
        Níveis esperados a partir de 0: 0=0, 1=1, 2=2, 3=3.
        """
        graph = _build_graph(
            vertices=[0, 1, 2, 3],
            edges=[
                (0, 1, 10.0),
                (1, 2, 10.0),
                (2, 3, 10.0),
            ],
        )
        result = bfs(graph, origin=0)
        assert result.level_of(0) == 0
        assert result.level_of(1) == 1
        assert result.level_of(2) == 2
        assert result.level_of(3) == 3


# ===================================================================
# CASO 2 — GRAFO VAZIO
# ===================================================================

class TestBFSGrafoVazio:
    """Casos com grafo vazio ou sem arestas."""

    def test_grafo_sem_vertices_levanta_erro(self):
        graph = Graph()
        with pytest.raises(ValueError, match="origem 0 não existe"):
            bfs(graph, origin=0)

    def test_grafo_com_um_unico_vertice(self):
        """Vértice isolado é alcançável de si mesmo no nível 0."""
        graph = _build_graph(vertices=[0], edges=[])
        result = bfs(graph, origin=0)
        assert result.reachable == {0}
        assert result.level_of(0) == 0

    def test_grafo_sem_arestas_apenas_origem(self):
        """Sem arestas, só a origem é alcançável."""
        graph = _build_graph(vertices=[0, 1, 2], edges=[])
        result = bfs(graph, origin=0)
        assert result.reachable == {0}
        assert not result.is_reachable(1)
        assert not result.is_reachable(2)


# ===================================================================
# CASO 3 — GRAFO COMPLETO
# ===================================================================

class TestBFSGrafoCompleto:
    """Caso com grafo completo (todos os vértices conectados a todos)."""

    def test_grafo_completo_todos_alcancaveis_em_um_passo(self):
        """
        Em K_n dirigido completo, a partir de qualquer vértice, todos os
        outros são alcançáveis em exatamente um passo (nível 1).
        """
        n = 5
        edges = [(i, j, 1.0) for i in range(n) for j in range(n) if i != j]
        graph = _build_graph(vertices=list(range(n)), edges=edges)

        result = bfs(graph, origin=0)
        assert result.reachable == set(range(n))
        assert result.level_of(0) == 0
        for v in range(1, n):
            assert result.level_of(v) == 1


# ===================================================================
# CASOS ADICIONAIS
# ===================================================================

class TestBFSCasosAdicionais:
    """Casos extras de robustez e cobertura."""

    def test_componente_disjunto_nao_e_alcancado(self):
        graph = _build_graph(
            vertices=[0, 1, 2, 3],
            edges=[
                (0, 1, 5.0),
                # 2 e 3 em componente disjunto
                (2, 3, 10.0),
            ],
        )
        result = bfs(graph, origin=0)
        assert result.reachable == {0, 1}
        assert not result.is_reachable(2)
        assert not result.is_reachable(3)

    def test_direcao_e_respeitada(self):
        """Em grafo dirigido, 1 não atinge 0 se só existir 0->1."""
        graph = _build_graph(
            vertices=[0, 1],
            edges=[(0, 1, 5.0)],
        )
        result_from_0 = bfs(graph, origin=0)
        result_from_1 = bfs(graph, origin=1)
        assert result_from_0.is_reachable(1) is True
        assert result_from_1.is_reachable(0) is False

    def test_ciclo_nao_causa_loop(self):
        graph = _build_graph(
            vertices=[0, 1, 2],
            edges=[
                (0, 1, 1.0),
                (1, 2, 1.0),
                (2, 0, 1.0),
            ],
        )
        result = bfs(graph, origin=0)
        assert result.reachable == {0, 1, 2}

    def test_is_reachable_helper_funciona(self):
        graph = _build_graph(
            vertices=[0, 1, 2],
            edges=[(0, 1, 5.0)],
        )
        assert is_reachable(graph, 0, 1) is True
        assert is_reachable(graph, 0, 2) is False

    def test_level_of_inalcancavel_levanta_erro(self):
        graph = _build_graph(vertices=[0, 1], edges=[])
        result = bfs(graph, origin=0)
        with pytest.raises(ValueError, match="não é alcançável"):
            result.level_of(1)
