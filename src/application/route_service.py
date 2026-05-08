"""
RouteService — caso de uso de cálculo de rotas.

Camada: Aplicação (Service)
"""

import time
from dataclasses import dataclass

from src.domain.graph import Graph
from src.domain.algorithms.dijkstra import dijkstra, INFINITY
from src.domain.algorithms.bfs import bfs


@dataclass(frozen=True)
class RouteResponse:
    success: bool
    origin: int
    destination: int
    path: list[int]
    total_cost: float
    algorithm: str
    time_ms: float
    message: str


class RouteService:
    """Serviço de cálculo de rotas no grafo."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph

    def shortest_route(self, origin: int, destination: int) -> RouteResponse:
        start = time.perf_counter()

        if not self._graph.has_vertex(origin):
            elapsed_ms = (time.perf_counter() - start) * 1000
            return RouteResponse(
                success=False, origin=origin, destination=destination,
                path=[], total_cost=INFINITY, algorithm="none",
                time_ms=elapsed_ms,
                message=f"Vértice de origem {origin} não existe no grafo.",
            )

        if not self._graph.has_vertex(destination):
            elapsed_ms = (time.perf_counter() - start) * 1000
            return RouteResponse(
                success=False, origin=origin, destination=destination,
                path=[], total_cost=INFINITY, algorithm="none",
                time_ms=elapsed_ms,
                message=f"Vértice de destino {destination} não existe no grafo.",
            )

        if origin == destination:
            elapsed_ms = (time.perf_counter() - start) * 1000
            return RouteResponse(
                success=True, origin=origin, destination=destination,
                path=[origin], total_cost=0.0, algorithm="trivial",
                time_ms=elapsed_ms,
                message="Origem e destino são o mesmo vértice.",
            )

        # 1. BFS para alcançabilidade — O(V + E)
        bfs_result = bfs(self._graph, origin)
        if not bfs_result.is_reachable(destination):
            elapsed_ms = (time.perf_counter() - start) * 1000
            return RouteResponse(
                success=False, origin=origin, destination=destination,
                path=[], total_cost=INFINITY, algorithm="bfs",
                time_ms=elapsed_ms,
                message=(
                    f"Destino {destination} não é alcançável a partir da "
                    f"origem {origin} no grafo atual."
                ),
            )

        # 2. Dijkstra para caminho mínimo — O((V + E) log V)
        dijkstra_result = dijkstra(self._graph, origin)
        path = dijkstra_result.path_to(destination)
        cost = dijkstra_result.distance_to(destination)
        elapsed_ms = (time.perf_counter() - start) * 1000

        return RouteResponse(
            success=True, origin=origin, destination=destination,
            path=path, total_cost=cost, algorithm="dijkstra",
            time_ms=elapsed_ms,
            message=(
                f"Rota encontrada com {len(path)} vértices, "
                f"custo total {cost:.2f} m."
            ),
        )

    @property
    def graph(self) -> Graph:
        return self._graph
