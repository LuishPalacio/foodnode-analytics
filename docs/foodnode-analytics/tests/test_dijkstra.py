"""
Testes unitários para o algoritmo de Dijkstra.

Casos exigidos pelo enunciado do E3:
    - Caso base: entrada válida com resultado esperado conhecido.
    - Grafo vazio: comportamento com entrada vazia ou nula.
    - Grafo completo: todos os vértices conectados entre si.

Adicionalmente:
    - Caminho ótimo entre múltiplas alternativas (verifica otimalidade).
    - Vértice inalcançável (componente disjunto).
    - Origem == destino (caso degenerado).
    - Validação de erro quando origem não existe.
"""

import pytest

from src.domain.graph import Graph
from src.domain.vertex import Vertex
from src.domain.edge import Edge
from src.domain.algorithms.dijkstra import dijkstra, INFINITY


def _build_graph(vertices: list[int], edges: list[tuple[int, int, float]]) -> Graph:
    """Helper: constrói um grafo dirigido a partir de listas de ids e arestas."""
    g = Graph(directed=True)
    for v_id in vertices:
        g.add_vertex(Vertex(id=v_id, label=f"V{v_id}"))
    for origin, dest, weight in edges:
        g.add_edge(Edge(origin=origin, destination=dest, weight=weight))
    return g


# ===================================================================
# CASO 1 — CASO BASE (exigido pelo enunciado)
# ===================================================================

class TestDijkstraCasoBase:
    """Caso base: grafo conhecido com resultado esperado verificável manualmente."""

    def test_caso_base_caminho_otimo_correto(self):
        """
        Grafo:    0 --10--> 1 --20--> 3
                  |          ^
                 50         15
                  v          |
                  2 ---------+

        Caminhos de 0 para 3:
            0 -> 1 -> 3: 10 + 20 = 30
            0 -> 2 -> 1 -> 3: 50 + 15 + 20 = 85
        Resultado esperado: caminho [0, 1, 3] com custo 30.
        """
        graph = _build_graph(
            vertices=[0, 1, 2, 3],
            edges=[
                (0, 1, 10.0),
                (0, 2, 50.0),
                (1, 3, 20.0),
                (2, 1, 15.0),
            ],
        )

        result = dijkstra(graph, origin=0)

        assert result.distances[0] == 0.0
        assert result.distances[1] == 10.0
        assert result.distances[2] == 50.0
        assert result.distances[3] == 30.0

        path = result.path_to(3)
        assert path == [0, 1, 3]

    def test_caso_base_predecessores_corretos(self):
        """Verifica que os predecessores formam o caminho ótimo."""
        graph = _build_graph(
            vertices=[0, 1, 2],
            edges=[
                (0, 1, 5.0),
                (1, 2, 3.0),
                (0, 2, 100.0),  # caminho direto mas pior
            ],
        )
        result = dijkstra(graph, origin=0)

        # Caminho ótimo 0->2 deve ser 0->1->2 (custo 8), não direto (custo 100)
        assert result.distances[2] == 8.0
        assert result.predecessors[2] == 1
        assert result.predecessors[1] == 0
        assert result.predecessors[0] is None


# ===================================================================
# CASO 2 — GRAFO VAZIO (exigido pelo enunciado)
# ===================================================================

class TestDijkstraGrafoVazio:
    """Caso com grafo vazio ou com poucos vértices."""

    def test_grafo_sem_vertices_levanta_erro_em_origem_inexistente(self):
        graph = Graph()
        with pytest.raises(ValueError, match="origem 0 não existe"):
            dijkstra(graph, origin=0)

    def test_grafo_com_um_unico_vertice(self):
        """Vértice único é alcançável de si mesmo com distância 0."""
        graph = _build_graph(vertices=[0], edges=[])
        result = dijkstra(graph, origin=0)
        assert result.distances[0] == 0.0
        assert result.path_to(0) == [0]

    def test_grafo_sem_arestas_apenas_origem_alcancavel(self):
        """Em grafo sem arestas, apenas a origem é alcançável; demais são INFINITY."""
        graph = _build_graph(vertices=[0, 1, 2], edges=[])
        result = dijkstra(graph, origin=0)
        assert result.distances[0] == 0.0
        assert result.distances[1] == INFINITY
        assert result.distances[2] == INFINITY
        assert result.is_reachable(1) is False
        assert result.path_to(1) == []


# ===================================================================
# CASO 3 — GRAFO COMPLETO (exigido pelo enunciado)
# ===================================================================

class TestDijkstraGrafoCompleto:
    """Caso com grafo completo: todos os vértices conectados a todos."""

    def test_grafo_completo_4_vertices(self):
        """
        Grafo K4 dirigido com pesos uniformes (10).
        De qualquer vértice, todos os outros estão a distância direta = 10.
        """
        n = 4
        edges = [
            (i, j, 10.0)
            for i in range(n)
            for j in range(n)
            if i != j
        ]
        graph = _build_graph(vertices=list(range(n)), edges=edges)

        result = dijkstra(graph, origin=0)
        assert result.distances[0] == 0.0
        for v in range(1, n):
            assert result.distances[v] == 10.0
            assert result.is_reachable(v) is True

    def test_grafo_completo_com_pesos_variados(self):
        """
        Grafo K4 dirigido com pesos crescentes.
        Verifica que Dijkstra escolhe caminho indireto se for mais barato.
        """
        graph = _build_graph(
            vertices=[0, 1, 2, 3],
            edges=[
                # arestas diretas a partir de 0 com custos altos
                (0, 1, 1.0),
                (0, 2, 100.0),
                (0, 3, 100.0),
                # caminho barato via 1
                (1, 2, 2.0),
                (1, 3, 50.0),
                # caminho barato via 2
                (2, 3, 3.0),
                # arestas reversas
                (3, 2, 100.0),
                (3, 1, 100.0),
                (3, 0, 100.0),
                (2, 1, 100.0),
                (2, 0, 100.0),
                (1, 0, 100.0),
            ],
        )
        result = dijkstra(graph, origin=0)

        # 0->1: direto = 1
        assert result.distances[1] == 1.0
        # 0->2: 0->1->2 = 1+2 = 3 (vs direto 100)
        assert result.distances[2] == 3.0
        assert result.path_to(2) == [0, 1, 2]
        # 0->3: 0->1->2->3 = 1+2+3 = 6 (vs direto 100, vs 0->1->3 = 51)
        assert result.distances[3] == 6.0
        assert result.path_to(3) == [0, 1, 2, 3]


# ===================================================================
# CASOS ADICIONAIS — robustez e correção
# ===================================================================

class TestDijkstraCasosAdicionais:
    """Casos extras que aumentam a confiança na implementação."""

    def test_componente_disjunto_destino_inalcancavel(self):
        """Vértices não-alcançáveis devem ter distância INFINITY."""
        graph = _build_graph(
            vertices=[0, 1, 2, 3],
            edges=[
                (0, 1, 5.0),
                # 2 e 3 estão em componente separado
                (2, 3, 10.0),
            ],
        )
        result = dijkstra(graph, origin=0)
        assert result.distances[1] == 5.0
        assert result.distances[2] == INFINITY
        assert result.distances[3] == INFINITY
        assert not result.is_reachable(2)
        assert not result.is_reachable(3)

    def test_grafo_com_ciclo(self):
        """Ciclos não devem causar loop infinito."""
        graph = _build_graph(
            vertices=[0, 1, 2],
            edges=[
                (0, 1, 1.0),
                (1, 2, 1.0),
                (2, 0, 1.0),  # cicla de volta
                (2, 1, 1.0),
            ],
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
        """Dijkstra deve trabalhar com pesos float, não apenas int."""
        graph = _build_graph(
            vertices=[0, 1, 2],
            edges=[
                (0, 1, 1.5),
                (1, 2, 2.7),
            ],
        )
        result = dijkstra(graph, origin=0)
        assert result.distances[2] == pytest.approx(4.2)

    def test_peso_zero_funciona(self):
        """Pesos zero são válidos (>= 0)."""
        graph = _build_graph(
            vertices=[0, 1],
            edges=[(0, 1, 0.0)],
        )
        result = dijkstra(graph, origin=0)
        assert result.distances[1] == 0.0
