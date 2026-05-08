"""
Algoritmo de Dijkstra — caminho mínimo de origem única.

Camada: Domínio (Core)
Tempo:  O((V + E) log V) — min-heap binário (heapq).
Espaço: O(V + E)

Referência:
    DIJKSTRA, E. W. A note on two problems in connexion with graphs.
    Numerische Mathematik, v. 1, n. 1, p. 269-271, 1959.
    CORMEN, T. H. et al. Algoritmos: teoria e prática. 3 ed.
    Rio de Janeiro: Elsevier, 2012. Cap. 24, seção 24.3.
"""

import heapq
from dataclasses import dataclass

from src.domain.graph import Graph


INFINITY = float("inf")


@dataclass(frozen=True)
class DijkstraResult:
    origin: int
    distances: dict[int, float]
    predecessors: dict[int, int | None]

    def is_reachable(self, target: int) -> bool:
        return target in self.distances and self.distances[target] != INFINITY

    def distance_to(self, target: int) -> float:
        if target not in self.distances:
            raise ValueError(f"vértice {target} não está no resultado")
        return self.distances[target]

    def path_to(self, target: int) -> list[int]:
        if not self.is_reachable(target):
            return []
        path: list[int] = []
        current: int | None = target
        while current is not None:
            path.append(current)
            current = self.predecessors.get(current)
        path.reverse()
        return path


def dijkstra(graph: Graph, origin: int) -> DijkstraResult:
    """
    Executa Dijkstra a partir do vértice 'origin'.

    Tempo:  O((V + E) log V)
    Espaço: O(V + E)
    """
    if not graph.has_vertex(origin):
        raise ValueError(f"vértice de origem {origin} não existe no grafo")

    # Inicialização — O(V)
    distances: dict[int, float] = {v_id: INFINITY for v_id in graph.vertex_ids()}
    predecessors: dict[int, int | None] = {v_id: None for v_id in graph.vertex_ids()}
    distances[origin] = 0.0

    heap: list[tuple[float, int]] = [(0.0, origin)]
    finalized: set[int] = set()

    # Loop principal — O((V + E) log V)
    while heap:
        current_dist, current_vertex = heapq.heappop(heap)  # O(log V)

        if current_vertex in finalized:
            continue
        finalized.add(current_vertex)

        if current_dist > distances[current_vertex]:
            continue

        # Relaxamento — O(grau(v))
        for neighbor, weight in graph.neighbors(current_vertex):
            if neighbor in finalized:
                continue
            new_distance = current_dist + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                predecessors[neighbor] = current_vertex
                heapq.heappush(heap, (new_distance, neighbor))  # O(log V)

    return DijkstraResult(
        origin=origin,
        distances=distances,
        predecessors=predecessors,
    )
