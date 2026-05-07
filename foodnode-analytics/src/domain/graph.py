"""
Graph — grafo dirigido e ponderado representado por lista de adjacências.

Camada: Domínio (Core)
Responsabilidade: estrutura de dados do grafo. Sem I/O.

Representação interna:
    self._adjacency: dict[int, list[tuple[int, float]]]
        Mapeia id_origem -> lista de (id_destino, peso).

Justificativa (E1/E2): malhas viárias urbanas são tipicamente esparsas
(E ≈ 2V a 4V), tornando a lista de adjacências mais eficiente em memória
que matriz de adjacências (O(V+E) vs O(V²)).
"""

from typing import Iterator

from src.domain.vertex import Vertex
from src.domain.edge import Edge


class Graph:
    """
    Grafo dirigido e ponderado com pesos não-negativos.

    Operações principais:
        - add_vertex(vertex): adiciona um vértice.
        - add_edge(edge): adiciona uma aresta dirigida.
        - neighbors(vertex_id): retorna vizinhos com seus pesos.
        - has_vertex(vertex_id): consulta existência.
        - get_vertex(vertex_id): recupera o objeto Vertex.

    Complexidade:
        - add_vertex: O(1) amortizado.
        - add_edge: O(1) amortizado.
        - neighbors: O(grau(v)) — proporcional ao número de arestas saindo de v.
        - has_vertex / get_vertex: O(1).
        - vertex_count / edge_count: O(1).
    """

    def __init__(self, directed: bool = True) -> None:
        """
        Inicializa um grafo vazio.

        Args:
            directed: True para grafo dirigido (default — coerente com E1).
                     Mantido como parâmetro para extensibilidade futura.
        """
        self._directed: bool = directed
        self._vertices: dict[int, Vertex] = {}
        self._adjacency: dict[int, list[tuple[int, float]]] = {}
        self._edge_count: int = 0

    # ------------------------------------------------------------------
    # Operações de construção
    # ------------------------------------------------------------------

    def add_vertex(self, vertex: Vertex) -> None:
        """
        Adiciona um vértice ao grafo.

        Raises:
            ValueError: se já existir vértice com o mesmo id.

        Complexidade: O(1) amortizado.
        """
        if vertex.id in self._vertices:
            raise ValueError(
                f"vértice com id {vertex.id} já existe (rótulo atual: "
                f"'{self._vertices[vertex.id].label}')"
            )
        self._vertices[vertex.id] = vertex
        self._adjacency[vertex.id] = []

    def add_edge(self, edge: Edge) -> None:
        """
        Adiciona uma aresta dirigida ao grafo.

        Raises:
            ValueError: se origem ou destino não existem como vértices.

        Complexidade: O(1) amortizado.
        """
        if edge.origin not in self._vertices:
            raise ValueError(
                f"vértice de origem {edge.origin} não existe no grafo"
            )
        if edge.destination not in self._vertices:
            raise ValueError(
                f"vértice de destino {edge.destination} não existe no grafo"
            )
        self._adjacency[edge.origin].append((edge.destination, edge.weight))
        self._edge_count += 1

        # Se o grafo for não-dirigido, adiciona aresta reversa também.
        # Mantido para extensibilidade — domínio atual usa apenas directed=True.
        if not self._directed and edge.origin != edge.destination:
            self._adjacency[edge.destination].append((edge.origin, edge.weight))
            self._edge_count += 1

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def neighbors(self, vertex_id: int) -> list[tuple[int, float]]:
        """
        Retorna a lista de vizinhos de um vértice como (destino, peso).

        Raises:
            ValueError: se o vértice não existe.

        Complexidade: O(1) (retorna referência à lista interna copiada).
        """
        if vertex_id not in self._vertices:
            raise ValueError(f"vértice {vertex_id} não existe no grafo")
        # retorna cópia para evitar mutação externa da estrutura interna
        return list(self._adjacency[vertex_id])

    def has_vertex(self, vertex_id: int) -> bool:
        """Consulta se o vértice existe. O(1)."""
        return vertex_id in self._vertices

    def get_vertex(self, vertex_id: int) -> Vertex:
        """
        Recupera o objeto Vertex pelo id.

        Raises:
            ValueError: se o vértice não existe.

        Complexidade: O(1).
        """
        if vertex_id not in self._vertices:
            raise ValueError(f"vértice {vertex_id} não existe no grafo")
        return self._vertices[vertex_id]

    @property
    def vertex_count(self) -> int:
        """Número total de vértices. O(1)."""
        return len(self._vertices)

    @property
    def edge_count(self) -> int:
        """Número total de arestas. O(1)."""
        return self._edge_count

    @property
    def is_directed(self) -> bool:
        return self._directed

    def vertex_ids(self) -> Iterator[int]:
        """Iterador sobre os ids de todos os vértices."""
        return iter(self._vertices.keys())

    def vertices(self) -> Iterator[Vertex]:
        """Iterador sobre os objetos Vertex."""
        return iter(self._vertices.values())

    # ------------------------------------------------------------------
    # Representação
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Graph(directed={self._directed}, "
            f"vertices={self.vertex_count}, edges={self._edge_count})"
        )

    def __len__(self) -> int:
        """len(graph) retorna o número de vértices."""
        return self.vertex_count
