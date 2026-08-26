"""Camada de aplicação que coordena usuários, projetos e tarefas."""

from __future__ import annotations

from datetime import date

from .excecoes import EntidadeDuplicadaError, EntidadeNaoEncontradaError
from .modelos import Prioridade, Projeto, StatusTarefa, Tarefa, Usuario


class GerenciadorTarefas:
    def __init__(self) -> None:
        self._usuarios: dict[int, Usuario] = {}

    def criar_usuario(self, id: int, nome: str, email: str, senha: str) -> Usuario:
        if id in self._usuarios:
            raise EntidadeDuplicadaError(f"Já existe um usuário com ID {id}.")
        email_normalizado = email.strip().lower()
        if any(usuario.email == email_normalizado for usuario in self._usuarios.values()):
            raise EntidadeDuplicadaError(f"O e-mail {email_normalizado} já está em uso.")
        usuario = Usuario(id, nome, email_normalizado, senha)
        self._usuarios[usuario.id] = usuario
        return usuario

    def listar_usuarios(self) -> list[Usuario]:
        return sorted(self._usuarios.values(), key=lambda usuario: usuario.id)

    def obter_usuario(self, usuario_id: int) -> Usuario:
        usuario = self._usuarios.get(usuario_id)
        if usuario is None:
            raise EntidadeNaoEncontradaError(
                f"Usuário com ID {usuario_id} não encontrado."
            )
        return usuario

    def remover_usuario(self, usuario_id: int) -> bool:
        return self._usuarios.pop(usuario_id, None) is not None

    def criar_projeto(
        self,
        usuario_id: int,
        projeto_id: int,
        nome: str,
        descricao: str,
        data_criacao: date | None = None,
    ) -> Projeto:
        usuario = self.obter_usuario(usuario_id)
        return usuario.criar_projeto(projeto_id, nome, descricao, data_criacao)

    def listar_projetos(self, usuario_id: int) -> list[Projeto]:
        return self.obter_usuario(usuario_id).listar_projetos()

    def obter_projeto(self, usuario_id: int, projeto_id: int) -> Projeto:
        projeto = self.obter_usuario(usuario_id).obter_projeto(projeto_id)
        if projeto is None:
            raise EntidadeNaoEncontradaError(
                f"Projeto com ID {projeto_id} não encontrado para o usuário {usuario_id}."
            )
        return projeto

    def remover_projeto(self, usuario_id: int, projeto_id: int) -> bool:
        return self.obter_usuario(usuario_id).remover_projeto(projeto_id)

    def criar_tarefa(
        self,
        usuario_id: int,
        projeto_id: int,
        tarefa_id: int,
        titulo: str,
        descricao: str,
        prioridade: Prioridade,
        data_limite: date,
    ) -> Tarefa:
        projeto = self.obter_projeto(usuario_id, projeto_id)
        return projeto.criar_tarefa(
            tarefa_id, titulo, descricao, prioridade, data_limite
        )

    def listar_tarefas(self, usuario_id: int, projeto_id: int) -> list[Tarefa]:
        return self.obter_projeto(usuario_id, projeto_id).listar_tarefas()

    def obter_tarefa(
        self, usuario_id: int, projeto_id: int, tarefa_id: int
    ) -> Tarefa:
        tarefa = self.obter_projeto(usuario_id, projeto_id).obter_tarefa(tarefa_id)
        if tarefa is None:
            raise EntidadeNaoEncontradaError(
                f"Tarefa com ID {tarefa_id} não encontrada no projeto {projeto_id}."
            )
        return tarefa

    def alterar_status(
        self,
        usuario_id: int,
        projeto_id: int,
        tarefa_id: int,
        novo_status: StatusTarefa,
    ) -> Tarefa:
        tarefa = self.obter_tarefa(usuario_id, projeto_id, tarefa_id)
        if novo_status is StatusTarefa.PENDENTE:
            tarefa.marcar_pendente()
        elif novo_status is StatusTarefa.EM_ANDAMENTO:
            tarefa.iniciar()
        else:
            tarefa.marcar_concluida()
        return tarefa

    def remover_tarefa(
        self, usuario_id: int, projeto_id: int, tarefa_id: int
    ) -> bool:
        return self.obter_projeto(usuario_id, projeto_id).remover_tarefa(tarefa_id)

