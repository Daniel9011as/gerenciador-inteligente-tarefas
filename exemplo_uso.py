"""Cenário pronto para demonstrar as funcionalidades sem digitação manual."""

from datetime import date
from pathlib import Path
import sys


RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

from gerenciador_tarefas.exportacao import ExportadorRelatorios  # noqa: E402
from gerenciador_tarefas.modelos import Prioridade  # noqa: E402
from gerenciador_tarefas.relatorios import RelatorioService  # noqa: E402
from gerenciador_tarefas.servicos import GerenciadorTarefas  # noqa: E402


def executar_demonstracao() -> None:
    sistema = GerenciadorTarefas()
    sistema.criar_usuario(1, "Ana Lima", "ana@example.com", "1234")
    projeto = sistema.criar_projeto(
        1, 1, "Projeto de POO", "Atividade prática da Unidade 03"
    )
    modelagem = sistema.criar_tarefa(
        1,
        1,
        1,
        "Modelar classes",
        "Criar Usuario, Projeto e Tarefa",
        Prioridade.ALTA,
        date(2026, 8, 25),
    )
    sistema.criar_tarefa(
        1,
        1,
        2,
        "Publicar no GitHub",
        "Criar o repositório público",
        Prioridade.URGENTE,
        date(2026, 8, 26),
    )
    modelagem.marcar_concluida()

    relatorios = RelatorioService(sistema)
    print(f"Projeto: {projeto.nome}")
    print(f"Progresso: {projeto.calcular_progresso():.1f}%")
    print("Pendências:")
    for item in relatorios.tarefas_pendentes_por_prioridade():
        print(f"- [{item.tarefa.prioridade.rotulo}] {item.tarefa.titulo}")

    destino = RAIZ / "relatorios"
    ExportadorRelatorios(sistema).exportar_csv(destino / "tarefas_pendentes.csv")
    ExportadorRelatorios(sistema).exportar_txt(destino / "produtividade.txt")
    print(f"Relatórios exportados em: {destino}")


if __name__ == "__main__":
    executar_demonstracao()

