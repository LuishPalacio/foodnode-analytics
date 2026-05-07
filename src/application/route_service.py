"""
RouteService — caso de uso de cálculo de rotas.

Camada: Aplicação (Service)
Responsabilidade: orquestrar a execução dos algoritmos de domínio (BFS e Dijkstra)
para responder à pergunta de negócio: "qual o caminho mínimo de A para B?".

Estratégia:
    1. BFS prévio para verificar alcançabilidade (responde explicitamente
       quando o destino está em componente disjunto).
    2. Se alcançável, executa Dijkstra para obter caminho de menor peso.
    3. Mede tempos de execução para diagnóstico e validação de performance.
"""

import time
from dataclasses import dataclass

from src.domain.graph import Graph
from src.domain.algorithms.dijkstra import dijkstra, INFINITY
from src.domain.algorithms.bfs import bfs


@dataclass(frozen=True)
class RouteResponse:
    """
    Resposta de uma consulta de rota.

    Atributos:
        success: True se foi possível calcular uma rota.
        origin: id do vértice de origem.
        destination: id do vértice de destino.
        path: sequência ordenada de vértices [origem, ..., destino].
              Vazia se success=False.
        total_cost: custo total da rota em metros. INFINITY se não há rota.
        algorithm: nome do algoritmo usado.
        time_ms: tempo total de execução em milissegundos.
        message: mensagem informativa para o usuário.
    """
    success: bool
    origin: int
    destination: int
    path: list[int]
    total_cost: float
    algorithm: str
    time_ms: float
    message: str


class RouteService:
    """
    Serviço de cálculo de rotas no grafo.

    Não conhece detalhes de I/O — recebe um Graph já carregado e devolve
    uma RouteResponse pronta para ser apresentada pela camada de UI.
    """

    def __init__(self, graph: Graph) -> None:
        self._graph = graph

    def shortest_route(self, origin: int, destination: int) -> RouteResponse:
        """
        Calcula a rota de menor peso entre origem e destino.

        Args:
            origin: id do vértice de origem (restaurante).
            destination: id do vértice de destino (cliente).

        Returns:
            RouteResponse com o resultado da consulta.
        """
        start = time.perf_counter()

        # Validações de existência
        if not self._graph.has_vertex(origin):
            elapsed_ms = (time.perf_counter() - start) * 1000
            return RouteResponse(
                success=False,
                origin=origin,
                destination=destination,
                path=[],
                total_cost=INFINITY,
                algorithm="none",
                time_ms=elapsed_ms,
                message=f"Vértice de origem {origin} não existe no grafo.",
            )

        if not self._graph.has_vertex(destination):
            elapsed_ms = (time.perf_counter() - start) * 1000
            return RouteResponse(
                success=False,
                origin=origin,
                destination=destination,
                path=[],
                total_cost=INFINITY,
                algorithm="none",
                time_ms=elapsed_ms,
                message=f"Vértice de destino {destination} não existe no grafo.",
            )

        # Caso degenerado: origem == destino
        if origin == destination:
            elapsed_ms = (time.perf_counter() - start) * 1000
            return RouteResponse(
                success=True,
                origin=origin,
                destination=destination,
                path=[origin],
                total_cost=0.0,
                algorithm="trivial",
                time_ms=elapsed_ms,
                message="Origem e destino são o mesmo vértice.",
            )

        # 1. BFS para verificar alcançabilidade — O(V + E)
        bfs_result = bfs(self._graph, origin)

        if not bfs_result.is_reachable(destination):
            elapsed_ms = (time.perf_counter() - start) * 1000
            return RouteResponse(
                success=False,
                origin=origin,
                destination=destination,
                path=[],
                total_cost=INFINITY,
                algorithm="bfs",
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
            success=True,
            origin=origin,
            destination=destination,
            path=path,
            total_cost=cost,
            algorithm="dijkstra",
            time_ms=elapsed_ms,
            message=(
                f"Rota encontrada com {len(path)} vértices, "
                f"custo total {cost:.2f} m."
            ),
        )

    @property
    def graph(self) -> Graph:
        """Acesso ao grafo subjacente (para diagnóstico)."""
        return self._graph
