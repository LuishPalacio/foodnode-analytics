"""
Algoritmo BFS — Busca em Largura.

Camada: Domínio (Core)
Categoria: Busca não-informada / travessia de grafo.

Uso no projeto: pré-verificação de alcançabilidade antes do Dijkstra.
Permite detectar e responder explicitamente quando o destino está em um
componente disjunto (ex.: rua sem saída a partir da origem em malha viária).

Complexidade:
    Tempo:  O(V + E) — cada vértice e cada aresta são visitados no máximo uma vez.
    Espaço: O(V) — fila FIFO + conjunto de visitados.

Referência:
    CORMEN, T. H. et al. Algoritmos: teoria e prática. 3 ed.
    Rio de Janeiro: Elsevier, 2012. Cap. 22, seção 22.2.
"""

from collections import deque
from dataclasses import dataclass

from src.domain.graph import Graph


@dataclass(frozen=True)
class BFSResult:
    """
    Resultado da execução do BFS a partir de uma origem.

    Atributos:
        origin: id do vértice de origem.
        reachable: conjunto de vértices alcançáveis (inclui a origem).
        levels: dict[id_vertice, nivel] — distância em número de arestas.
                Origem tem nível 0. Vértices não alcançáveis não estão no dict.
    """
    origin: int
    reachable: set[int]
    levels: dict[int, int]

    def is_reachable(self, target: int) -> bool:
        """O(1) — verifica se o destino está no conjunto de alcançáveis."""
        return target in self.reachable

    def level_of(self, target: int) -> int:
        """
        Retorna o nível (distância em número de arestas) até o destino.

        Raises:
            ValueError: se o destino não é alcançável a partir da origem.
        """
        if target not in self.levels:
            raise ValueError(
                f"vértice {target} não é alcançável a partir de {self.origin}"
            )
        return self.levels[target]


def bfs(graph: Graph, origin: int) -> BFSResult:
    """
    Executa busca em largura (BFS) a partir do vértice 'origin'.

    Algoritmo:
        1. Marca origem como visitada (nível 0) e enfileira.
        2. Enquanto a fila não está vazia:
           a. Desenfileira o vértice u do início.
           b. Para cada vizinho v de u ainda não visitado:
              - Marca v como visitado (nível = nível(u) + 1).
              - Enfileira v.
        3. Retorna o conjunto de vértices visitados.

    Args:
        graph: grafo dirigido (pesos das arestas são ignorados em BFS).
        origin: id do vértice de origem.

    Returns:
        BFSResult com vértices alcançáveis e seus níveis.

    Raises:
        ValueError: se o vértice de origem não existe no grafo.

    Complexidade:
        Tempo:  O(V + E)
        Espaço: O(V) — fila + conjunto de visitados.
    """
    if not graph.has_vertex(origin):
        raise ValueError(
            f"vértice de origem {origin} não existe no grafo"
        )

    reachable: set[int] = {origin}
    levels: dict[int, int] = {origin: 0}
    queue: deque[int] = deque([origin])

    # Loop principal — cada vértice entra na fila no máximo uma vez. O(V + E).
    while queue:
        current = queue.popleft()
        current_level = levels[current]

        for neighbor, _weight in graph.neighbors(current):
            # _weight é ignorado: BFS não usa pesos.
            if neighbor not in reachable:
                reachable.add(neighbor)
                levels[neighbor] = current_level + 1
                queue.append(neighbor)

    return BFSResult(
        origin=origin,
        reachable=reachable,
        levels=levels,
    )


def is_reachable(graph: Graph, origin: int, destination: int) -> bool:
    """
    Atalho: verifica se 'destination' é alcançável a partir de 'origin' via BFS.

    Útil quando só queremos a resposta booleana, sem precisar do BFSResult completo.

    Complexidade: O(V + E) no pior caso (mesma do BFS — early-stop seria
    uma otimização possível, mas para grafos pequenos do domínio não compensa).
    """
    return bfs(graph, origin).is_reachable(destination)
