"""
JSONReader — carga de grafos a partir de arquivos JSON.

Camada: Infraestrutura (I/O)
"""

import json
from pathlib import Path

from src.domain.graph import Graph
from src.domain.vertex import Vertex
from src.domain.edge import Edge


class JSONReader:
    """
    Leitor de grafos em formato JSON.

    Schema esperado (documentado no E2 - seção 4):
        {
            "metadata": { "name": str, "directed": bool, ... },
            "vertices": [ { "id": int, "label": str, "type": str } ],
            "edges": [ { "origem": int, "destino": int, "peso": float } ]
        }
    """

    @staticmethod
    def read(path: str | Path) -> Graph:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"arquivo não encontrado: {path}")

        with path.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON inválido em {path}: {e}") from e

        return JSONReader._build_graph(data, path)

    @staticmethod
    def _build_graph(data: dict, source_path: Path) -> Graph:
        if "vertices" not in data:
            raise KeyError(f"campo 'vertices' ausente em {source_path}")
        if "edges" not in data:
            raise KeyError(f"campo 'edges' ausente em {source_path}")

        metadata = data.get("metadata", {})
        directed = metadata.get("directed", True)
        graph = Graph(directed=directed)

        seen_ids: set[int] = set()
        for v_data in data["vertices"]:
            if "id" not in v_data:
                raise KeyError(f"vértice sem campo 'id' em {source_path}: {v_data}")
            if "label" not in v_data:
                raise KeyError(f"vértice sem campo 'label' em {source_path}: {v_data}")
            v_id = v_data["id"]
            if v_id in seen_ids:
                raise ValueError(f"id de vértice duplicado: {v_id} em {source_path}")
            seen_ids.add(v_id)
            graph.add_vertex(Vertex(
                id=v_id,
                label=v_data["label"],
                type=v_data.get("type", "intersection"),
            ))

        for e_data in data["edges"]:
            if "origem" not in e_data or "destino" not in e_data:
                raise KeyError(f"aresta com campos faltantes em {source_path}: {e_data}")
            if "peso" not in e_data:
                raise KeyError(f"aresta sem campo 'peso' em {source_path}: {e_data}")
            graph.add_edge(Edge(
                origin=e_data["origem"],
                destination=e_data["destino"],
                weight=float(e_data["peso"]),
            ))

        return graph
