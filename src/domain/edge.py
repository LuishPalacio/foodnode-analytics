"""
Edge — aresta dirigida e ponderada (trecho de via navegável).

Camada: Domínio (Core)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Edge:
    """
    Aresta dirigida com peso não-negativo.

    Atributos:
        origin: id do vértice de origem.
        destination: id do vértice de destino.
        weight: peso da aresta (distância em metros). Deve ser >= 0
                (premissa do algoritmo de Dijkstra).
    """
    origin: int
    destination: int
    weight: float

    def __post_init__(self) -> None:
        if self.weight < 0:
            raise ValueError(
                f"peso de aresta deve ser >= 0 (Dijkstra exige pesos não-negativos), "
                f"recebido: {self.weight} entre {self.origin} -> {self.destination}"
            )
        if self.origin < 0 or self.destination < 0:
            raise ValueError(
                f"ids de vértice devem ser >= 0, recebido: "
                f"origin={self.origin}, destination={self.destination}"
            )

    def __repr__(self) -> str:
        return f"Edge({self.origin} -> {self.destination}, peso={self.weight})"
