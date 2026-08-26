"""Consultas de produtividade solicitadas na atividade."""

from __future__ import annotations

from dataclasses import dataclass

from .modelos import Projeto, StatusTarefa, Tarefa, Usuario
from .servicos import GerenciadorTarefas


@dataclass(frozen=True, slots=True)
class ItemTarefaPendente:
    usuario: Usuario
    projeto: Projeto
    tarefa: Tarefa


@dataclass(frozen=True, slots=True)
class ItemProgressoProjeto:
    usuario: Usuario
    projeto: Projeto
    percentual: float


@dataclass(frozen=True, slots=True)
class ItemProdutividadeUsuario:
    usuario: Usuario
    total_concluidas: int


class RelatorioService:
    def __init__(self, sistema: GerenciadorTarefas) -> None:
        self._sistema = sistema

    def tarefas_pendentes_por_prioridade(self) -> list[ItemTarefaPendente]:
        itens = [
            ItemTarefaPendente(usuario, projeto, tarefa)
            for usuario in self._sistema.listar_usuarios()
            for projeto in usuario.listar_projetos()
            for tarefa in projeto.listar_tarefas()
            if tarefa.status is not StatusTarefa.CONCLUIDA
        ]
        return sorted(
            itens,
            key=lambda item: (
                -item.tarefa.prioridade.value,
                item.tarefa.data_limite,
                item.usuario.id,
                item.projeto.id,
                item.tarefa.id,
            ),
        )

    def projetos_por_progresso(self) -> list[ItemProgressoProjeto]:
        itens = [
            ItemProgressoProjeto(usuario, projeto, projeto.calcular_progresso())
            for usuario in self._sistema.listar_usuarios()
            for projeto in usuario.listar_projetos()
        ]
        return sorted(
            itens,
            key=lambda item: (
                -item.percentual,
                item.projeto.nome.casefold(),
                item.usuario.id,
                item.projeto.id,
            ),
        )

    def total_concluidas_por_usuario(self) -> list[ItemProdutividadeUsuario]:
        itens = []
        for usuario in self._sistema.listar_usuarios():
            total = sum(
                tarefa.status is StatusTarefa.CONCLUIDA
                for projeto in usuario.listar_projetos()
                for tarefa in projeto.listar_tarefas()
            )
            itens.append(ItemProdutividadeUsuario(usuario, total))
        return sorted(
            itens,
            key=lambda item: (-item.total_concluidas, item.usuario.nome.casefold()),
        )

