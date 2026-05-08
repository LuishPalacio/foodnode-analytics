"""Testes de performance — validação empírica da promessa do E2."""

import time

import pytest

from src.application.route_service import RouteService
from src.infrastructure.random_graph_generator import RandomGraphGenerator


@pytest.mark.performance
class TestPerformanceDijkstra:

    def test_50_vertices_executa_em_menos_de_1_segundo(self):
        generator = RandomGraphGenerator(
            n_vertices=50, density=0.15, seed=42, force_connected=True
        )
        graph = generator.generate()
        service = RouteService(graph)
        start = time.perf_counter()
        service.shortest_route(0, 49)
        elapsed_s = time.perf_counter() - start
        assert elapsed_s < 1.0
        print(f"\n[perf] 50 vértices: {elapsed_s*1000:.2f} ms")

    def test_500_vertices_executa_em_menos_de_1_segundo(self):
        generator = RandomGraphGenerator(
            n_vertices=500, density=0.05, seed=1234, force_connected=True
        )
        graph = generator.generate()
        service = RouteService(graph)
        start = time.perf_counter()
        service.shortest_route(0, 499)
        elapsed_s = time.perf_counter() - start
        assert elapsed_s < 1.0
        print(f"\n[perf] 500 vértices: {elapsed_s*1000:.2f} ms")

    def test_1000_vertices_executa_em_menos_de_2_segundos(self):
        generator = RandomGraphGenerator(
            n_vertices=1000, density=0.02, seed=9999, force_connected=True
        )
        graph = generator.generate()
        service = RouteService(graph)
        start = time.perf_counter()
        service.shortest_route(0, 999)
        elapsed_s = time.perf_counter() - start
        assert elapsed_s < 2.0
        print(f"\n[perf] 1000 vértices: {elapsed_s*1000:.2f} ms")

    def test_reprodutibilidade_com_seed(self):
        gen1 = RandomGraphGenerator(n_vertices=20, density=0.2, seed=42)
        gen2 = RandomGraphGenerator(n_vertices=20, density=0.2, seed=42)
        g1, g2 = gen1.generate(), gen2.generate()
        assert g1.vertex_count == g2.vertex_count
        assert g1.edge_count == g2.edge_count
        for v_id in g1.vertex_ids():
            assert sorted(g1.neighbors(v_id)) == sorted(g2.neighbors(v_id))
