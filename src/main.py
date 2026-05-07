"""
FoodNode Analytics — Entry point.

Executa a CLI delegando para src.presentation.cli.

Uso:
    python -m src.main <subcomando> [opções]

Ou, se o pacote for instalado:
    foodnode <subcomando> [opções]
"""

import sys

from src.presentation.cli import main


if __name__ == "__main__":
    sys.exit(main())
