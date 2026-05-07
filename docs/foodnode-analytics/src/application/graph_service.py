"""
GraphService — caso de uso de gestão do ciclo de vida de grafos.

Camada: Aplicação (Service)
Responsabilidade: centralizar carregamento, geração e diagnóstico de grafos.
Atua como adaptador entre a CLI e a infraestrutura de I/O.
"""

from pathlib import Path

from src.domain.graph import Graph
from src.infrastructure.json_reader import JSONReader
from src.infrastructure.random_graph_generator import RandomGraphGenerator


class GraphService:
    """
    Serviço de gestão de grafos.

    Operações:
        - load_from_file: lê um grafo de um arquivo JSON.
        - generate_random: cria um grafo aleatório com parâmetros.
        - graph_info: retorna estatísticas resumidas do grafo carregado.
    """

    @staticmethod
    def load_from_file(path: str | Path) -> Graph:
        """
        Carrega um grafo a partir de arquivo JSON no schema documentado.

        Args:
            path: caminho do arquivo .json.

        Returns:
            Graph populado.

        Raises:
            FileNotFoundError, ValueError, KeyError: ver JSONReader.
        """
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
        """
        Gera um grafo aleatório. Opcionalmente exporta para arquivo JSON.

        Args:
            n_vertices: número de vértices (>=2).
            density: probabilidade de aresta entre par ordenado [0.0, 1.0].
            weight_min, weight_max: faixa de pesos sorteados.
            seed: semente para reprodutibilidade.
            force_connected: garante conectividade fraca.
            output_path: se fornecido, escreve o grafo gerado em JSON.

        Returns:
            Graph gerado.
        """
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
            # Recarrega do arquivo para garantir consistência com o que foi escrito
            return JSONReader.read(output_path)

        return generator.generate()

    @staticmethod
    def graph_info(graph: Graph) -> dict:
        """
        Retorna estatísticas do grafo para diagnóstico.

        Returns:
            dict com:
                - vertex_count, edge_count
                - directed
                - density: razão entre arestas existentes e máximas possíveis
                - origin_vertices, destination_vertices: contagens por tipo
        """
        v_count = graph.vertex_count
        e_count = graph.edge_count

        max_edges = v_count * (v_count - 1) if graph.is_directed else v_count * (v_count - 1) // 2
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
