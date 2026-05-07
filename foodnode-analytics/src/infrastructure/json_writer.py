"""
JSONWriter — exportação de resultados (rotas calculadas) em arquivos JSON.

Camada: Infraestrutura (I/O)
"""

import json
from pathlib import Path


class JSONWriter:
    """
    Escritor de resultados de roteamento em formato JSON.

    Formato de saída (item 6 do backlog do E2):
        {
            "origem": int,
            "destino": int,
            "caminho": [int, ...],
            "custo_total_metros": float,
            "algoritmo": str,
            "tempo_ms": float
        }
    """

    @staticmethod
    def write_route(
        path: str | Path,
        origin: int,
        destination: int,
        path_vertices: list[int],
        total_cost: float,
        algorithm: str,
        time_ms: float,
    ) -> None:
        """
        Escreve uma rota calculada em arquivo JSON.

        Args:
            path: caminho do arquivo de saída.
            origin: id do vértice de origem.
            destination: id do vértice de destino.
            path_vertices: sequência ordenada de ids do caminho mínimo.
            total_cost: custo total da rota (em metros).
            algorithm: nome do algoritmo usado (ex.: "dijkstra").
            time_ms: tempo de execução em milissegundos.

        Raises:
            OSError: se não foi possível escrever no caminho informado.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "origem": origin,
            "destino": destination,
            "caminho": path_vertices,
            "custo_total_metros": total_cost,
            "algoritmo": algorithm,
            "tempo_ms": round(time_ms, 3),
        }

        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")
