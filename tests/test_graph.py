"""Testes unitários para a classe Graph."""

import pytest

from src.domain.graph import Graph
from src.domain.vertex import Vertex
from src.domain.edge import Edge


class TestGraphConstruction:

    def test_empty_graph_has_zero_vertices_and_edges(self):
        graph = Graph()
        assert graph.vertex_count == 0
        assert graph.edge_count == 0
        assert len(graph) == 0

    def test_graph_is_directed_by_default(self):
        graph = Graph()
        assert graph.is_directed is True

    def test_graph_can_be_undirected(self):
        graph = Graph(directed=False)
        assert graph.is_directed is False


class TestAddVertex:

    def test_add_single_vertex(self):
        graph = Graph()
        graph.add_vertex(Vertex(id=0, label="Origem"))
        assert graph.vertex_count == 1
        assert graph.has_vertex(0) is True

    def test_add_multiple_vertices(self):
        graph = Graph()
        for i in range(5):
            graph.add_vertex(Vertex(id=i, label=f"V{i}"))
        assert graph.vertex_count == 5

    def test_add_duplicate_vertex_raises(self):
        graph = Graph()
        graph.add_vertex(Vertex(id=0, label="Original"))
        with pytest.raises(ValueError, match="já existe"):
            graph.add_vertex(Vertex(id=0, label="Duplicado"))

    def test_get_vertex_returns_correct_object(self):
        graph = Graph()
        v = Vertex(id=42, label="Especial", type="origin")
        graph.add_vertex(v)
        assert graph.get_vertex(42) == v

    def test_get_nonexistent_vertex_raises(self):
        graph = Graph()
        with pytest.raises(ValueError, match="não existe"):
            graph.get_vertex(999)


class TestAddEdge:

    def test_add_edge_between_existing_vertices(self):
        graph = Graph()
        graph.add_vertex(Vertex(id=0, label="A"))
        graph.add_vertex(Vertex(id=1, label="B"))
        graph.add_edge(Edge(origin=0, destination=1, weight=10.0))
        assert graph.edge_count == 1

    def test_add_edge_with_nonexistent_origin_raises(self):
        graph = Graph()
        graph.add_vertex(Vertex(id=0, label="A"))
        with pytest.raises(ValueError, match="origem"):
            graph.add_edge(Edge(origin=99, destination=0, weight=10.0))

    def test_add_edge_with_nonexistent_destination_raises(self):
        graph = Graph()
        graph.add_vertex(Vertex(id=0, label="A"))
        with pytest.raises(ValueError, match="destino"):
            graph.add_edge(Edge(origin=0, destination=99, weight=10.0))

    def test_negative_weight_raises_at_edge_creation(self):
        with pytest.raises(ValueError, match="peso de aresta deve ser >= 0"):
            Edge(origin=0, destination=1, weight=-5.0)

    def test_directed_graph_has_one_directed_edge_per_add(self):
        graph = Graph(directed=True)
        graph.add_vertex(Vertex(id=0, label="A"))
        graph.add_vertex(Vertex(id=1, label="B"))
        graph.add_edge(Edge(origin=0, destination=1, weight=10.0))
        assert graph.neighbors(0) == [(1, 10.0)]
        assert graph.neighbors(1) == []

    def test_undirected_graph_creates_reverse_edge(self):
        graph = Graph(directed=False)
        graph.add_vertex(Vertex(id=0, label="A"))
        graph.add_vertex(Vertex(id=1, label="B"))
        graph.add_edge(Edge(origin=0, destination=1, weight=10.0))
        assert (1, 10.0) in graph.neighbors(0)
        assert (0, 10.0) in graph.neighbors(1)
        assert graph.edge_count == 2


class TestNeighbors:

    def test_neighbors_of_isolated_vertex_is_empty(self):
        graph = Graph()
        graph.add_vertex(Vertex(id=0, label="Solitário"))
        assert graph.neighbors(0) == []

    def test_neighbors_returns_correct_pairs(self):
        graph = Graph()
        graph.add_vertex(Vertex(id=0, label="A"))
        graph.add_vertex(Vertex(id=1, label="B"))
        graph.add_vertex(Vertex(id=2, label="C"))
        graph.add_edge(Edge(origin=0, destination=1, weight=10.0))
        graph.add_edge(Edge(origin=0, destination=2, weight=20.0))
        neighbors = graph.neighbors(0)
        assert len(neighbors) == 2
        assert (1, 10.0) in neighbors
        assert (2, 20.0) in neighbors

    def test_neighbors_returns_copy_not_reference(self):
        graph = Graph()
        graph.add_vertex(Vertex(id=0, label="A"))
        graph.add_vertex(Vertex(id=1, label="B"))
        graph.add_edge(Edge(origin=0, destination=1, weight=10.0))
        neighbors = graph.neighbors(0)
        neighbors.append((999, 999.0))
        assert graph.neighbors(0) == [(1, 10.0)]

    def test_neighbors_of_nonexistent_vertex_raises(self):
        graph = Graph()
        with pytest.raises(ValueError, match="não existe"):
            graph.neighbors(999)
