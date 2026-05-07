"""
JSONReader — carga de grafos a partir de arquivos JSON no schema definido em E2.

Camada: Infraestrutura (I/O)
Responsabilidade: ler arquivo do disco, parsear JSON e construir um Graph válido.
Valida invariantes (ids únicos, pesos >= 0, referências válidas) antes de retornar.
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
            "metadata": {
                "name": str,
                "vertices_count": int,
                "edges_count": int,
                "directed": bool,
                "weighted": bool,
                "weight_unit": str
            },
            "vertices": [
                { "id": int, "label": str, "type": "origin"|"destination"|"intersection" }
            ],
            "edges": [
                { "origem": int, "destino": int, "peso": float }
            ]
        }
    """

    @staticmethod
    def read(path: str | Path) -> Graph:
        """
        Lê um arquivo JSON e constrói um Graph.

        Args:
            path: caminho para o arquivo JSON.

        Returns:
            Graph populado com os vértices e arestas do arquivo.

        Raises:
            FileNotFoundError: se o arquivo não existe.
            ValueError: se o JSON é inválido ou viola invariantes do grafo.
            KeyError: se faltam campos obrigatórios no schema.
        """
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
        """Constrói o Graph a partir do dict já parseado."""
        if "vertices" not in data:
            raise KeyError(f"campo 'vertices' ausente em {source_path}")
        if "edges" not in data:
            raise KeyError(f"campo 'edges' ausente em {source_path}")

        # Lê metadados (opcionais, com defaults)
        metadata = data.get("metadata", {})
        directed = metadata.get("directed", True)

        graph = Graph(directed=directed)

        # Adiciona vértices — valida ids únicos via Graph.add_vertex()
        seen_ids: set[int] = set()
        for v_data in data["vertices"]:
            if "id" not in v_data:
                raise KeyError(f"vértice sem campo 'id' em {source_path}: {v_data}")
            if "label" not in v_data:
                raise KeyError(f"vértice sem campo 'label' em {source_path}: {v_data}")

            v_id = v_data["id"]
            if v_id in seen_ids:
                raise ValueError(
                    f"id de vértice duplicado: {v_id} em {source_path}"
                )
            seen_ids.add(v_id)

            vertex = Vertex(
                id=v_id,
                label=v_data["label"],
                type=v_data.get("type", "intersection"),
            )
            graph.add_vertex(vertex)

        # Adiciona arestas — valida referências e pesos via Edge/Graph
        for e_data in data["edges"]:
            if "origem" not in e_data or "destino" not in e_data:
                raise KeyError(
                    f"aresta com campos faltantes em {source_path}: {e_data}"
                )
            if "peso" not in e_data:
                raise KeyError(
                    f"aresta sem campo 'peso' em {source_path}: {e_data}"
                )

            edge = Edge(
                origin=e_data["origem"],
                destination=e_data["destino"],
                weight=float(e_data["peso"]),
            )
            graph.add_edge(edge)

        # Validação cruzada com metadados (warning, não erro)
        if "vertices_count" in metadata:
            declared = metadata["vertices_count"]
            actual = graph.vertex_count
            if declared != actual:
                # Não levanta erro — metadados são informativos.
                # Mas isso poderia ser um log/warning em produção.
                pass

        return graph
