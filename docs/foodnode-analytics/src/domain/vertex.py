"""
Vertex — vértice do grafo (cruzamento de ruas, restaurante ou cliente).

Camada: Domínio (Core)
Responsabilidade: estrutura de dados pura, sem lógica de I/O.
"""

from dataclasses import dataclass
from typing import Literal

VertexType = Literal["origin", "destination", "intersection"]


@dataclass(frozen=True)
class Vertex:
    """
    Vértice do grafo.

    Atributos:
        id: identificador único (inteiro não-negativo).
        label: rótulo legível (ex.: "Rua A x Rua 1", "Restaurante FoodNode").
        type: classificação do vértice no domínio do problema.
            - "origin": ponto de partida (restaurante)
            - "destination": ponto de chegada (cliente)
            - "intersection": cruzamento intermediário

    Imutável (frozen=True) para poder ser usado como chave em dicionários e sets.
    """
    id: int
    label: str
    type: VertexType = "intersection"

    def __post_init__(self) -> None:
        if self.id < 0:
            raise ValueError(f"id de vértice deve ser >= 0, recebido: {self.id}")
        if not self.label:
            raise ValueError("label do vértice não pode ser vazio")

    def __repr__(self) -> str:
        return f"Vertex(id={self.id}, label='{self.label}', type='{self.type}')"
