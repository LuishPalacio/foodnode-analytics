"""
RandomGraphGenerator — geração reprodutível de grafos aleatórios para testes.

Camada: Infraestrutura (I/O)
Responsabilidade: produzir grafos sintéticos com parâmetros configuráveis,
úteis para testes de stress e validação de performance.

Reprodutibilidade: usa random.Random(seed) isolado, evitando interferência
com outras fontes de aleatoriedade.
"""

import json
import random
from pathlib import Path

from src.domain.graph import Graph
from src.domain.vertex import Vertex
from src.domain.edge import Edge


class RandomGraphGenerator:
    """
    Gerador de grafos dirigidos ponderados aleatórios.

    Parâmetros (item 4 do backlog do E2):
        - n_vertices: número de vértices.
        - density: probabilidade de existir aresta dirigida (u, v).
                   Para malhas viárias esparsas, valores típicos: 0.05 a 0.20.
        - weight_min, weight_max: faixa de pesos sorteados uniformemente.
        - seed: semente para reprodutibilidade. None = usa timestamp.
        - force_connected: se True, garante conectividade fraca via árvore
                          geradora antes de adicionar arestas aleatórias.
    """

    def __init__(
        self,
        n_vertices: int,
        density: float = 0.15,
        weight_min: float = 30.0,
        weight_max: float = 2000.0,
        seed: int | None = None,
        force_connected: bool = False,
    ) -> None:
        if n_vertices < 2:
            raise ValueError(f"n_vertices deve ser >= 2, recebido: {n_vertices}")
        if not 0.0 <= density <= 1.0:
            raise ValueError(f"density deve estar em [0.0, 1.0], recebido: {density}")
        if weight_min < 0:
            raise ValueError(f"weight_min deve ser >= 0, recebido: {weight_min}")
        if weight_max < weight_min:
            raise ValueError(
                f"weight_max ({weight_max}) deve ser >= weight_min ({weight_min})"
            )

        self.n_vertices = n_vertices
        self.density = density
        self.weight_min = weight_min
        self.weight_max = weight_max
        self.seed = seed
        self.force_connected = force_connected

        # Random isolado para reprodutibilidade
        self._rng = random.Random(seed)

    def generate(self) -> Graph:
        """
        Gera um grafo aleatório com os parâmetros do construtor.

        Returns:
            Graph dirigido ponderado.
        """
        graph = Graph(directed=True)

        # 1. Adiciona vértices
        for i in range(self.n_vertices):
            label = (
                "Restaurante (origem)" if i == 0
                else f"Cruzamento {i}"
            )
            v_type = "origin" if i == 0 else "intersection"
            graph.add_vertex(Vertex(id=i, label=label, type=v_type))

        # 2. Se forçar conectividade fraca, gera primeiro uma árvore aleatória
        existing_edges: set[tuple[int, int]] = set()
        if self.force_connected:
            self._add_spanning_tree(graph, existing_edges)

        # 3. Adiciona arestas aleatórias até a densidade alvo
        for u in range(self.n_vertices):
            for v in range(self.n_vertices):
                if u == v:
                    continue
                if (u, v) in existing_edges:
                    continue
                if self._rng.random() < self.density:
                    weight = self._rng.uniform(self.weight_min, self.weight_max)
                    graph.add_edge(Edge(origin=u, destination=v, weight=round(weight, 2)))
                    existing_edges.add((u, v))

        return graph

    def _add_spanning_tree(
        self,
        graph: Graph,
        existing_edges: set[tuple[int, int]],
    ) -> None:
        """
        Adiciona uma árvore geradora aleatória ao grafo, garantindo
        conectividade fraca (todo vértice atinge ao menos um outro).
        """
        # Embaralha a ordem dos vértices para árvore aleatória
        order = list(range(self.n_vertices))
        self._rng.shuffle(order)

        # Conecta cada vértice (a partir do segundo) a um vértice anterior na ordem
        for i in range(1, len(order)):
            v = order[i]
            u = order[self._rng.randint(0, i - 1)]
            weight = self._rng.uniform(self.weight_min, self.weight_max)
            graph.add_edge(Edge(origin=u, destination=v, weight=round(weight, 2)))
            existing_edges.add((u, v))

    def export_to_json(self, path: str | Path) -> None:
        """
        Gera o grafo e escreve diretamente em arquivo JSON no schema documentado.

        Args:
            path: caminho de saída do arquivo .json.
        """
        graph = self.generate()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "metadata": {
                "name": f"Grafo aleatório (seed={self.seed})",
                "vertices_count": graph.vertex_count,
                "edges_count": graph.edge_count,
                "directed": True,
                "weighted": True,
                "weight_unit": "meters",
                "generator_params": {
                    "n_vertices": self.n_vertices,
                    "density": self.density,
                    "weight_min": self.weight_min,
                    "weight_max": self.weight_max,
                    "seed": self.seed,
                    "force_connected": self.force_connected,
                },
            },
            "vertices": [
                {"id": v.id, "label": v.label, "type": v.type}
                for v in graph.vertices()
            ],
            "edges": [
                {"origem": u, "destino": dest, "peso": w}
                for u in graph.vertex_ids()
                for dest, w in graph.neighbors(u)
            ],
        }

        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")
