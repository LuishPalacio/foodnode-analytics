"""
Algoritmo BFS — Busca em Largura.

Camada: Domínio (Core)
Tempo:  O(V + E)
Espaço: O(V)

Uso no projeto: pré-verificação de alcançabilidade antes do Dijkstra.

Referência:
    CORMEN, T. H. et al. Algoritmos: teoria e prática. 3 ed.
    Rio de Janeiro: Elsevier, 2012. Cap. 22, seção 22.2.
"""

from collections import deque
from dataclasses import dataclass

from src.domain.graph import Graph


@dataclass(frozen=True)
class BFSResult:
    origin: int
    reachable: set[int]
    levels: dict[int, int]

    def is_reachable(self, target: int) -> bool:
        return target in self.reachable

    def level_of(self, target: int) -> int:
        if target not in self.levels:
            raise ValueError(
                f"vértice {target} não é alcançável a partir de {self.origin}"
            )
        return self.levels[target]


def bfs(graph: Graph, origin: int) -> BFSResult:
    """
    Executa busca em largura a partir de 'origin'.

    Tempo:  O(V + E)
    Espaço: O(V)
    """
    if not graph.has_vertex(origin):
        raise ValueError(f"vértice de origem {origin} não existe no grafo")

    reachable: set[int] = {origin}
    levels: dict[int, int] = {origin: 0}
    queue: deque[int] = deque([origin])

    while queue:
        current = queue.popleft()
        current_level = levels[current]

        for neighbor, _weight in graph.neighbors(current):
            if neighbor not in reachable:
                reachable.add(neighbor)
                levels[neighbor] = current_level + 1
                queue.append(neighbor)

    return BFSResult(origin=origin, reachable=reachable, levels=levels)


def is_reachable(graph: Graph, origin: int, destination: int) -> bool:
    """Atalho: retorna True se destination é alcançável a partir de origin."""
    return bfs(graph, origin).is_reachable(destination)
