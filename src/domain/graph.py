"""
Graph — grafo dirigido e ponderado representado por lista de adjacências.

Camada: Domínio (Core)
"""

from typing import Iterator

from src.domain.vertex import Vertex
from src.domain.edge import Edge


class Graph:
    """
    Grafo dirigido e ponderado com pesos não-negativos.

    Operações:
        - add_vertex, add_edge: O(1) amortizado.
        - neighbors: O(grau(v)).
        - has_vertex, get_vertex: O(1).
    """

    def __init__(self, directed: bool = True) -> None:
        self._directed: bool = directed
        self._vertices: dict[int, Vertex] = {}
        self._adjacency: dict[int, list[tuple[int, float]]] = {}
        self._edge_count: int = 0

    def add_vertex(self, vertex: Vertex) -> None:
        if vertex.id in self._vertices:
            raise ValueError(
                f"vértice com id {vertex.id} já existe (rótulo atual: "
                f"'{self._vertices[vertex.id].label}')"
            )
        self._vertices[vertex.id] = vertex
        self._adjacency[vertex.id] = []

    def add_edge(self, edge: Edge) -> None:
        if edge.origin not in self._vertices:
            raise ValueError(f"vértice de origem {edge.origin} não existe no grafo")
        if edge.destination not in self._vertices:
            raise ValueError(f"vértice de destino {edge.destination} não existe no grafo")
        self._adjacency[edge.origin].append((edge.destination, edge.weight))
        self._edge_count += 1
        if not self._directed and edge.origin != edge.destination:
            self._adjacency[edge.destination].append((edge.origin, edge.weight))
            self._edge_count += 1

    def neighbors(self, vertex_id: int) -> list[tuple[int, float]]:
        if vertex_id not in self._vertices:
            raise ValueError(f"vértice {vertex_id} não existe no grafo")
        return list(self._adjacency[vertex_id])

    def has_vertex(self, vertex_id: int) -> bool:
        return vertex_id in self._vertices

    def get_vertex(self, vertex_id: int) -> Vertex:
        if vertex_id not in self._vertices:
            raise ValueError(f"vértice {vertex_id} não existe no grafo")
        return self._vertices[vertex_id]

    @property
    def vertex_count(self) -> int:
        return len(self._vertices)

    @property
    def edge_count(self) -> int:
        return self._edge_count

    @property
    def is_directed(self) -> bool:
        return self._directed

    def vertex_ids(self) -> Iterator[int]:
        return iter(self._vertices.keys())

    def vertices(self) -> Iterator[Vertex]:
        return iter(self._vertices.values())

    def __repr__(self) -> str:
        return (
            f"Graph(directed={self._directed}, "
            f"vertices={self.vertex_count}, edges={self._edge_count})"
        )

    def __len__(self) -> int:
        return self.vertex_count
