"""
Testes do RouteService — integração entre Dijkstra, BFS e a camada de aplicação.
"""

import pytest

from src.domain.graph import Graph
from src.domain.vertex import Vertex
from src.domain.edge import Edge
from src.application.route_service import RouteService
from src.domain.algorithms.dijkstra import INFINITY


def _build_graph(vertices: list[int], edges: list[tuple[int, int, float]]) -> Graph:
    g = Graph(directed=True)
    for v_id in vertices:
        g.add_vertex(Vertex(id=v_id, label=f"V{v_id}"))
    for origin, dest, weight in edges:
        g.add_edge(Edge(origin=origin, destination=dest, weight=weight))
    return g


class TestRouteServiceSucesso:

    def test_rota_existente_retorna_caminho_e_custo(self):
        graph = _build_graph(
            vertices=[0, 1, 2],
            edges=[(0, 1, 5.0), (1, 2, 3.0)],
        )
        service = RouteService(graph)
        response = service.shortest_route(0, 2)

        assert response.success is True
        assert response.path == [0, 1, 2]
        assert response.total_cost == 8.0
        assert response.algorithm == "dijkstra"
        assert response.time_ms >= 0

    def test_origem_igual_destino_retorna_caminho_unitario(self):
        graph = _build_graph(vertices=[0, 1], edges=[(0, 1, 5.0)])
        service = RouteService(graph)
        response = service.shortest_route(0, 0)

        assert response.success is True
        assert response.path == [0]
        assert response.total_cost == 0.0
        assert response.algorithm == "trivial"


class TestRouteServiceFalhas:

    def test_origem_inexistente_retorna_falha(self):
        graph = _build_graph(vertices=[0, 1], edges=[(0, 1, 5.0)])
        service = RouteService(graph)
        response = service.shortest_route(99, 1)

        assert response.success is False
        assert response.path == []
        assert response.total_cost == INFINITY
        assert "origem" in response.message.lower()

    def test_destino_inexistente_retorna_falha(self):
        graph = _build_graph(vertices=[0, 1], edges=[(0, 1, 5.0)])
        service = RouteService(graph)
        response = service.shortest_route(0, 99)

        assert response.success is False
        assert "destino" in response.message.lower()

    def test_destino_em_componente_disjunto_retorna_falha_com_bfs(self):
        graph = _build_graph(
            vertices=[0, 1, 2, 3],
            edges=[
                (0, 1, 5.0),
                # 2 e 3 desconectados de 0
                (2, 3, 10.0),
            ],
        )
        service = RouteService(graph)
        response = service.shortest_route(0, 3)

        assert response.success is False
        assert response.algorithm == "bfs"  # BFS detectou inalcançabilidade
        assert "não é alcançável" in response.message
        assert response.total_cost == INFINITY


class TestRouteServiceComGrafoReal:
    """Testa o serviço usando o grafo de exemplo do projeto (centro de Mogi)."""

    def test_grafo_real_caminho_otimo_0_para_6(self, tmp_path):
        from pathlib import Path
        from src.application.graph_service import GraphService

        path = Path(__file__).parent.parent / "data" / "sample_bairro_8v.json"
        if not path.exists():
            pytest.skip("Arquivo de dados não disponível")

        graph = GraphService.load_from_file(path)
        service = RouteService(graph)
        response = service.shortest_route(0, 6)

        # Caminho ótimo conhecido: 0 -> 3 -> 4 -> 6 com custo 260m
        # Validado manualmente no E2.
        assert response.success is True
        assert response.path == [0, 3, 4, 6]
        assert response.total_cost == pytest.approx(260.0)
