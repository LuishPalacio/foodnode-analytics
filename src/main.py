"""
FoodNode Analytics — Entry point principal.

Inicia a interface gráfica (GUI Tkinter) por padrão.

Para usar a CLI alternativa:
    python -m src.presentation.cli <subcomando> [opções]
"""

import sys

from src.presentation.gui import run


if __name__ == "__main__":
    sys.exit(run() or 0)
