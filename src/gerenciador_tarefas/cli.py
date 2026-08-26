"""Interface de linha de comando do projeto."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Callable

from .excecoes import GerenciadorError, ValidacaoError
from .exportacao import ExportadorRelatorios
from .modelos import Prioridade, StatusTarefa
from .relatorios import RelatorioService
from .servicos import GerenciadorTarefas


class AplicacaoCLI:
    def __init__(self, sistema: GerenciadorTarefas | None = None) -> None:
        self.sistema = sistema or GerenciadorTarefas()
        self._acoes: dict[str, Callable[[], None]] = {
            "1": self._cadastrar_usuario,
            "2": self._listar_usuarios,
            "3": self._remover_usuario,
            "4": self._cadastrar_projeto,
            "5": self._listar_projetos,
            "6": self._remover_projeto,
            "7": self._cadastrar_tarefa,
            "8": self._listar_tarefas,
            "9": self._alterar_status,
            "10": self._remover_tarefa,
            "11": self._exibir_relatorios,
            "12": self._exportar_relatorios,
        }

    def executar(self) -> None:
        print("\nGERENCIADOR INTELIGENTE DE TAREFAS")
        while True:
            self._mostrar_menu()
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "0":
                print("Programa encerrado.")
                return
            acao = self._acoes.get(opcao)
            if acao is None:
                print("Opção inválida.")
                continue
            try:
                acao()
            except (GerenciadorError, ValueError) as erro:
                print(f"Erro: {erro}")

    @staticmethod
    def _mostrar_menu() -> None:
        print(
            """
1. Cadastrar usuário          7. Cadastrar tarefa
2. Listar usuários            8. Listar tarefas
3. Remover usuário            9. Alterar status da tarefa
4. Cadastrar projeto         10. Remover tarefa
5. Listar projetos           11. Exibir relatórios
6. Remover projeto           12. Exportar relatórios
0. Sair
"""
        )

    @staticmethod
    def _ler_inteiro(rotulo: str) -> int:
        try:
            return int(input(rotulo).strip())
        except ValueError as erro:
            raise ValidacaoError("Informe um número inteiro.") from erro

    @staticmethod
    def _ler_data(rotulo: str) -> date:
        texto = input(rotulo).strip()
        try:
            return datetime.strptime(texto, "%d/%m/%Y").date()
        except ValueError as erro:
            raise ValidacaoError("Use uma data válida no formato DD/MM/AAAA.") from erro

    def _ler_ids_projeto(self) -> tuple[int, int]:
        usuario_id = self._ler_inteiro("ID do usuário: ")
        projeto_id = self._ler_inteiro("ID do projeto: ")
        return usuario_id, projeto_id

    def _ler_ids_tarefa(self) -> tuple[int, int, int]:
        usuario_id, projeto_id = self._ler_ids_projeto()
        tarefa_id = self._ler_inteiro("ID da tarefa: ")
        return usuario_id, projeto_id, tarefa_id

    def _cadastrar_usuario(self) -> None:
        usuario = self.sistema.criar_usuario(
            self._ler_inteiro("ID: "),
            input("Nome: "),
            input("E-mail: "),
            input("Senha: "),
        )
        print(f"Usuário {usuario.nome} cadastrado.")

    def _listar_usuarios(self) -> None:
        usuarios = self.sistema.listar_usuarios()
        if not usuarios:
            print("Nenhum usuário cadastrado.")
            return
        for usuario in usuarios:
            print(f"[{usuario.id}] {usuario.nome} - {usuario.email}")

    def _remover_usuario(self) -> None:
        removido = self.sistema.remover_usuario(self._ler_inteiro("ID do usuário: "))
        print("Usuário removido." if removido else "Usuário não encontrado.")

    def _cadastrar_projeto(self) -> None:
        usuario_id = self._ler_inteiro("ID do usuário: ")
        projeto = self.sistema.criar_projeto(
            usuario_id,
            self._ler_inteiro("ID do projeto: "),
            input("Nome do projeto: "),
            input("Descrição: "),
        )
        print(f"Projeto {projeto.nome} cadastrado.")

    def _listar_projetos(self) -> None:
        usuario_id = self._ler_inteiro("ID do usuário: ")
        projetos = self.sistema.listar_projetos(usuario_id)
        if not projetos:
            print("Nenhum projeto cadastrado para este usuário.")
            return
        for projeto in projetos:
            print(
                f"[{projeto.id}] {projeto.nome} - "
                f"progresso: {projeto.calcular_progresso():.1f}%"
            )

    def _remover_projeto(self) -> None:
        usuario_id, projeto_id = self._ler_ids_projeto()
        removido = self.sistema.remover_projeto(usuario_id, projeto_id)
        print("Projeto removido." if removido else "Projeto não encontrado.")

    def _cadastrar_tarefa(self) -> None:
        usuario_id, projeto_id = self._ler_ids_projeto()
        tarefa = self.sistema.criar_tarefa(
            usuario_id,
            projeto_id,
            self._ler_inteiro("ID da tarefa: "),
            input("Título: "),
            input("Descrição: "),
            Prioridade.de_texto(input("Prioridade (Baixa/Média/Alta/Urgente): ")),
            self._ler_data("Data limite (DD/MM/AAAA): "),
        )
        print(f"Tarefa {tarefa.titulo} cadastrada.")

    def _listar_tarefas(self) -> None:
        usuario_id, projeto_id = self._ler_ids_projeto()
        tarefas = self.sistema.listar_tarefas(usuario_id, projeto_id)
        if not tarefas:
            print("Nenhuma tarefa cadastrada neste projeto.")
            return
        for tarefa in tarefas:
            atraso = " - ATRASADA" if tarefa.esta_vencida() else ""
            print(
                f"[{tarefa.id}] {tarefa.titulo} | {tarefa.prioridade.rotulo} | "
                f"{tarefa.status.rotulo} | {tarefa.data_limite:%d/%m/%Y}{atraso}"
            )

    def _alterar_status(self) -> None:
        usuario_id, projeto_id, tarefa_id = self._ler_ids_tarefa()
        status = StatusTarefa.de_texto(
            input("Novo status (Pendente/Em andamento/Concluída): ")
        )
        tarefa = self.sistema.alterar_status(
            usuario_id, projeto_id, tarefa_id, status
        )
        print(f"Status de {tarefa.titulo}: {tarefa.status.rotulo}.")

    def _remover_tarefa(self) -> None:
        removido = self.sistema.remover_tarefa(*self._ler_ids_tarefa())
        print("Tarefa removida." if removido else "Tarefa não encontrada.")

    def _exibir_relatorios(self) -> None:
        relatorios = RelatorioService(self.sistema)
        print("\nTAREFAS NÃO CONCLUÍDAS POR PRIORIDADE")
        pendentes = relatorios.tarefas_pendentes_por_prioridade()
        if not pendentes:
            print("Nenhuma tarefa pendente.")
        for item in pendentes:
            print(
                f"[{item.tarefa.prioridade.rotulo}] {item.tarefa.titulo} - "
                f"{item.usuario.nome} / {item.projeto.nome}"
            )

        print("\nPROJETOS POR PERCENTUAL DE CONCLUSÃO")
        for item in relatorios.projetos_por_progresso():
            print(f"{item.projeto.nome}: {item.percentual:.1f}%")

        print("\nTAREFAS CONCLUÍDAS POR USUÁRIO")
        for item in relatorios.total_concluidas_por_usuario():
            print(f"{item.usuario.nome}: {item.total_concluidas}")

    def _exportar_relatorios(self) -> None:
        diretorio = Path(input("Diretório de destino [relatorios]: ").strip() or "relatorios")
        exportador = ExportadorRelatorios(self.sistema)
        csv_criado = exportador.exportar_csv(diretorio / "tarefas_pendentes.csv")
        txt_criado = exportador.exportar_txt(diretorio / "produtividade.txt")
        print(f"Arquivos criados: {csv_criado} e {txt_criado}")

