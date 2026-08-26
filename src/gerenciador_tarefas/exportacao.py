"""Exportação opcional de relatórios em CSV e TXT."""

from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from pathlib import Path

from .relatorios import RelatorioService
from .servicos import GerenciadorTarefas


class Exportador(ABC):
    """Contrato comum que demonstra abstração e polimorfismo."""

    def __init__(self, sistema: GerenciadorTarefas) -> None:
        self._relatorios = RelatorioService(sistema)

    @abstractmethod
    def exportar(self, destino: str | Path) -> Path:
        """Exporta o relatório e devolve o caminho criado."""


class ExportadorCSV(Exportador):
    def exportar(self, destino: str | Path) -> Path:
        caminho = Path(destino)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with caminho.open("w", encoding="utf-8-sig", newline="") as arquivo:
            campos = [
                "usuario",
                "projeto",
                "tarefa",
                "prioridade",
                "data_limite",
                "status",
            ]
            escritor = csv.DictWriter(arquivo, fieldnames=campos)
            escritor.writeheader()
            for item in self._relatorios.tarefas_pendentes_por_prioridade():
                escritor.writerow(
                    {
                        "usuario": item.usuario.nome,
                        "projeto": item.projeto.nome,
                        "tarefa": item.tarefa.titulo,
                        "prioridade": item.tarefa.prioridade.rotulo,
                        "data_limite": item.tarefa.data_limite.isoformat(),
                        "status": item.tarefa.status.rotulo,
                    }
                )
        return caminho


class ExportadorTXT(Exportador):
    def exportar(self, destino: str | Path) -> Path:
        caminho = Path(destino)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        linhas = ["RELATÓRIO DE PRODUTIVIDADE", "=" * 30, ""]
        linhas.append("TAREFAS NÃO CONCLUÍDAS POR PRIORIDADE")
        pendentes = self._relatorios.tarefas_pendentes_por_prioridade()
        if not pendentes:
            linhas.append("Nenhuma tarefa pendente.")
        for item in pendentes:
            linhas.append(
                f"- [{item.tarefa.prioridade.rotulo}] {item.tarefa.titulo} "
                f"| {item.usuario.nome} / {item.projeto.nome} "
                f"| prazo: {item.tarefa.data_limite:%d/%m/%Y}"
            )

        linhas.extend(["", "PROGRESSO DOS PROJETOS"])
        for item in self._relatorios.projetos_por_progresso():
            linhas.append(
                f"- {item.projeto.nome} ({item.usuario.nome}): "
                f"{item.percentual:.1f}%"
            )

        linhas.extend(["", "TAREFAS CONCLUÍDAS POR USUÁRIO"])
        for item in self._relatorios.total_concluidas_por_usuario():
            linhas.append(f"- {item.usuario.nome}: {item.total_concluidas}")

        caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        return caminho


class ExportadorRelatorios:
    """Fachada simples mantida para facilitar o uso pela interface."""

    def __init__(self, sistema: GerenciadorTarefas) -> None:
        self._csv: Exportador = ExportadorCSV(sistema)
        self._txt: Exportador = ExportadorTXT(sistema)

    def exportar_csv(self, destino: str | Path) -> Path:
        return self._csv.exportar(destino)

    def exportar_txt(self, destino: str | Path) -> Path:
        return self._txt.exportar(destino)
