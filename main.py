"""Ponto de entrada do Gerenciador Inteligente de Tarefas."""

from pathlib import Path
import sys


RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

from gerenciador_tarefas.cli import AplicacaoCLI  # noqa: E402


if __name__ == "__main__":
    AplicacaoCLI().executar()

