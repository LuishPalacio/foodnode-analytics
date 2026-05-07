"""
Algoritmo de Dijkstra — caminho mínimo de origem única em grafo dirigido
ponderado com pesos não-negativos.

Camada: Domínio (Core)
Categoria: Guloso (greedy) com relaxamento de arestas via fila de prioridade.

Complexidade:
    Tempo:  O((V + E) log V) — usando min-heap binário (heapq).
    Espaço: O(V + E) — vetores de distância e predecessor + lista de adjacências.

Referência:
    DIJKSTRA, E. W. A note on two problems in connexion with graphs.
    Numerische Mathematik, v. 1, n. 1, p. 269-271, 1959.

    CORMEN, T. H. et al. Algoritmos: teoria e prática. 3 ed.
    Rio de Janeiro: Elsevier, 2012. Cap. 24, seção 24.3.
"""

import heapq
from dataclasses import dataclass

from src.domain.graph import Graph


# Representa "infinito" para distâncias ainda não calculadas.
INFINITY = float("inf")


@dataclass(frozen=True)
class DijkstraResult:
    """
    Resultado da execução do Dijkstra a partir de uma origem.

    Atributos:
        origin: id do vértice de origem.
        distances: dict[id_vertice, distancia_minima].
                   Valor é INFINITY se inalcançável.
        predecessors: dict[id_vertice, id_vertice_anterior].
                     Valor é None se for a origem ou inalcançável.
    """
    origin: int
    distances: dict[int, float]
    predecessors: dict[int, int | None]

    def is_reachable(self, target: int) -> bool:
        """Retorna True se o destino é alcançável a partir da origem."""
        return target in self.distances and self.distances[target] != INFINITY

    def distance_to(self, target: int) -> float:
        """Retorna a distância mínima até o destino. INFINITY se inalcançável."""
        if target not in self.distances:
            raise ValueError(f"vértice {target} não está no resultado")
        return self.distances[target]

    def path_to(self, target: int) -> list[int]:
        """
        Reconstrói o caminho mínimo da origem até o destino.

        Returns:
            Lista ordenada de ids de vértices [origem, ..., destino].
            Lista vazia se o destino é inalcançável.

        Complexidade: O(V) no pior caso (caminho passa por todos os vértices).
        """
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
    Executa o algoritmo de Dijkstra a partir do vértice 'origin'.

    Algoritmo:
        1. Inicializa distâncias: 0 para origem, INFINITY para os demais.
        2. Fila de prioridade (min-heap) com tuplas (distancia, vertice).
        3. Em cada iteração, extrai o vértice de menor distância (greedy).
        4. Para cada vizinho, tenta relaxar a aresta.
        5. Termina quando a fila está vazia.

    Args:
        graph: grafo dirigido e ponderado (pesos >= 0).
        origin: id do vértice de origem.

    Returns:
        DijkstraResult com distâncias e predecessores para todos os vértices
        alcançáveis. Vértices inalcançáveis terão distância INFINITY.

    Raises:
        ValueError: se o vértice de origem não existe no grafo.

    Complexidade:
        Tempo:  O((V + E) log V)
            - Cada vértice entra/sai do heap no máximo O(grau(v)+1) vezes
            - Cada operação de heap é O(log V)
            - Soma das operações: O((V + E) log V)
        Espaço: O(V + E)
            - distances e predecessors: O(V)
            - heap pode conter até E entradas no pior caso
            - lista de adjacências do grafo: O(V + E)
    """
    if not graph.has_vertex(origin):
        raise ValueError(
            f"vértice de origem {origin} não existe no grafo"
        )

    # Inicialização — O(V)
    distances: dict[int, float] = {
        v_id: INFINITY for v_id in graph.vertex_ids()
    }
    predecessors: dict[int, int | None] = {
        v_id: None for v_id in graph.vertex_ids()
    }
    distances[origin] = 0.0

    # Min-heap: tuplas (distancia_acumulada, id_vertice)
    # heapq mantém a menor no topo, o que dá comportamento de fila de prioridade.
    heap: list[tuple[float, int]] = [(0.0, origin)]

    # Conjunto de vértices já finalizados (com distância mínima definitiva).
    # Uma vez que um vértice é extraído com sua menor distância, não precisa
    # ser reprocessado — propriedade do Dijkstra para pesos não-negativos.
    finalized: set[int] = set()

    # Loop principal — O((V + E) log V)
    while heap:
        # Extrai o vértice de menor distância — O(log V)
        current_dist, current_vertex = heapq.heappop(heap)

        # Pode haver entradas obsoletas no heap (lazy deletion).
        # Se já finalizamos este vértice, ignoramos.
        if current_vertex in finalized:
            continue
        finalized.add(current_vertex)

        # Se a distância armazenada é menor que a extraída, é entrada obsoleta.
        if current_dist > distances[current_vertex]:
            continue

        # Relaxamento de arestas — O(grau(v))
        for neighbor, weight in graph.neighbors(current_vertex):
            if neighbor in finalized:
                continue

            new_distance = current_dist + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                predecessors[neighbor] = current_vertex
                # Inserção no heap — O(log V)
                heapq.heappush(heap, (new_distance, neighbor))

    return DijkstraResult(
        origin=origin,
        distances=distances,
        predecessors=predecessors,
    )
