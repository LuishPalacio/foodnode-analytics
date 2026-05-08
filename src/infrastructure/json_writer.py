"""
JSONWriter — exportação de rotas em arquivos JSON.

Camada: Infraestrutura (I/O)
"""

import json
from pathlib import Path


class JSONWriter:
    """Escritor de resultados de roteamento em formato JSON."""

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
