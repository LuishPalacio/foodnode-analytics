"""
GraphService — caso de uso de gestão de grafos.

Camada: Aplicação (Service)
"""

from pathlib import Path

from src.domain.graph import Graph
from src.infrastructure.json_reader import JSONReader
from src.infrastructure.random_graph_generator import RandomGraphGenerator


class GraphService:
    @staticmethod
    def load_from_file(path: str | Path) -> Graph:
        return JSONReader.read(path)

    @staticmethod
    def generate_random(
        n_vertices: int,
        density: float = 0.15,
        weight_min: float = 30.0,
        weight_max: float = 2000.0,
        seed: int | None = None,
        force_connected: bool = False,
        output_path: str | Path | None = None,
    ) -> Graph:
        generator = RandomGraphGenerator(
            n_vertices=n_vertices,
            density=density,
            weight_min=weight_min,
            weight_max=weight_max,
            seed=seed,
            force_connected=force_connected,
        )
        if output_path is not None:
            generator.export_to_json(output_path)
            return JSONReader.read(output_path)
        return generator.generate()

    @staticmethod
    def graph_info(graph: Graph) -> dict:
        v_count = graph.vertex_count
        e_count = graph.edge_count
        max_edges = (
            v_count * (v_count - 1) if graph.is_directed
            else v_count * (v_count - 1) // 2
        )
        density = e_count / max_edges if max_edges > 0 else 0.0
        origins = sum(1 for v in graph.vertices() if v.type == "origin")
        destinations = sum(1 for v in graph.vertices() if v.type == "destination")
        return {
            "vertex_count": v_count,
            "edge_count": e_count,
            "directed": graph.is_directed,
            "density": round(density, 4),
            "origin_vertices": origins,
            "destination_vertices": destinations,
        }
