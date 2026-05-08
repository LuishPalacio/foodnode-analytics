"""
RandomGraphGenerator — geração reprodutível de grafos aleatórios.

Camada: Infraestrutura (I/O)
"""

import json
import random
from pathlib import Path

from src.domain.graph import Graph
from src.domain.vertex import Vertex
from src.domain.edge import Edge


class RandomGraphGenerator:
    """Gerador de grafos dirigidos ponderados aleatórios."""

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
            raise ValueError(f"weight_max ({weight_max}) deve ser >= weight_min ({weight_min})")

        self.n_vertices = n_vertices
        self.density = density
        self.weight_min = weight_min
        self.weight_max = weight_max
        self.seed = seed
        self.force_connected = force_connected
        self._rng = random.Random(seed)

    def generate(self) -> Graph:
        graph = Graph(directed=True)
        for i in range(self.n_vertices):
            label = "Restaurante (origem)" if i == 0 else f"Cruzamento {i}"
            v_type = "origin" if i == 0 else "intersection"
            graph.add_vertex(Vertex(id=i, label=label, type=v_type))

        existing_edges: set[tuple[int, int]] = set()
        if self.force_connected:
            self._add_spanning_tree(graph, existing_edges)

        for u in range(self.n_vertices):
            for v in range(self.n_vertices):
                if u == v or (u, v) in existing_edges:
                    continue
                if self._rng.random() < self.density:
                    weight = self._rng.uniform(self.weight_min, self.weight_max)
                    graph.add_edge(Edge(origin=u, destination=v, weight=round(weight, 2)))
                    existing_edges.add((u, v))

        return graph

    def _add_spanning_tree(self, graph: Graph, existing_edges: set[tuple[int, int]]) -> None:
        order = list(range(self.n_vertices))
        self._rng.shuffle(order)
        for i in range(1, len(order)):
            v = order[i]
            u = order[self._rng.randint(0, i - 1)]
            weight = self._rng.uniform(self.weight_min, self.weight_max)
            graph.add_edge(Edge(origin=u, destination=v, weight=round(weight, 2)))
            existing_edges.add((u, v))

    def export_to_json(self, path: str | Path) -> None:
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
