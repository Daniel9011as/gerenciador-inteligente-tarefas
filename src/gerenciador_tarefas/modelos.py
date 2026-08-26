"""Entidades e enums do domínio de gerenciamento de tarefas."""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from datetime import date
from enum import Enum

from .excecoes import EntidadeDuplicadaError, ValidacaoError


def _texto_obrigatorio(valor: str, campo: str) -> str:
    texto = valor.strip()
    if not texto:
        raise ValidacaoError(f"{campo} é obrigatório.")
    return texto


def _id_positivo(valor: int, campo: str = "ID") -> int:
    if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
        raise ValidacaoError(f"{campo} deve ser um número inteiro positivo.")
    return valor


class Prioridade(Enum):
    BAIXA = 1
    MEDIA = 2
    ALTA = 3
    URGENTE = 4

    @property
    def rotulo(self) -> str:
        return {
            Prioridade.BAIXA: "Baixa",
            Prioridade.MEDIA: "Média",
            Prioridade.ALTA: "Alta",
            Prioridade.URGENTE: "Urgente",
        }[self]

    @classmethod
    def de_texto(cls, valor: str) -> Prioridade:
        normalizado = valor.strip().upper().replace("É", "E")
        try:
            return cls[normalizado]
        except KeyError as erro:
            opcoes = ", ".join(item.rotulo for item in cls)
            raise ValidacaoError(f"Prioridade inválida. Use: {opcoes}.") from erro


class StatusTarefa(Enum):
    PENDENTE = "Pendente"
    EM_ANDAMENTO = "Em andamento"
    CONCLUIDA = "Concluída"

    @property
    def rotulo(self) -> str:
        return self.value

    @classmethod
    def de_texto(cls, valor: str) -> StatusTarefa:
        normalizado = (
            valor.strip()
            .upper()
            .replace(" ", "_")
            .replace("Í", "I")
            .replace("Ã", "A")
        )
        try:
            return cls[normalizado]
        except KeyError as erro:
            opcoes = ", ".join(item.rotulo for item in cls)
            raise ValidacaoError(f"Status inválido. Use: {opcoes}.") from erro


class Tarefa:
    """Uma atividade pertencente a exatamente um projeto."""

    def __init__(
        self,
        id: int,
        titulo: str,
        descricao: str,
        prioridade: Prioridade,
        data_limite: date,
        projeto: Projeto,
        status: StatusTarefa = StatusTarefa.PENDENTE,
    ) -> None:
        self.id = _id_positivo(id, "ID da tarefa")
        self.titulo = _texto_obrigatorio(titulo, "Título")
        self.descricao = _texto_obrigatorio(descricao, "Descrição")
        if not isinstance(prioridade, Prioridade):
            raise ValidacaoError("Prioridade deve ser uma opção do enum Prioridade.")
        if not isinstance(data_limite, date):
            raise ValidacaoError("Data limite deve ser uma data válida.")
        if not isinstance(status, StatusTarefa):
            raise ValidacaoError("Status deve ser uma opção do enum StatusTarefa.")
        self.prioridade = prioridade
        self.data_limite = data_limite
        self.projeto = projeto
        self.status = status

    def marcar_pendente(self) -> None:
        self.status = StatusTarefa.PENDENTE

    def iniciar(self) -> None:
        self.status = StatusTarefa.EM_ANDAMENTO

    def marcar_concluida(self) -> None:
        self.status = StatusTarefa.CONCLUIDA

    def esta_vencida(self, referencia: date | None = None) -> bool:
        hoje = referencia or date.today()
        return self.status is not StatusTarefa.CONCLUIDA and self.data_limite < hoje

    def __repr__(self) -> str:
        return f"Tarefa(id={self.id}, titulo={self.titulo!r}, status={self.status.name})"


class Projeto:
    """Agrupa tarefas e calcula o percentual concluído."""

    def __init__(
        self,
        id: int,
        nome: str,
        descricao: str,
        usuario: Usuario,
        data_criacao: date | None = None,
    ) -> None:
        self.id = _id_positivo(id, "ID do projeto")
        self.nome = _texto_obrigatorio(nome, "Nome do projeto")
        self.descricao = _texto_obrigatorio(descricao, "Descrição do projeto")
        self.data_criacao = data_criacao or date.today()
        if not isinstance(self.data_criacao, date):
            raise ValidacaoError("Data de criação deve ser uma data válida.")
        self.usuario = usuario
        self._tarefas: dict[int, Tarefa] = {}

    def adicionar_tarefa(self, tarefa: Tarefa) -> None:
        if tarefa.id in self._tarefas:
            raise EntidadeDuplicadaError(
                f"Já existe uma tarefa com ID {tarefa.id} neste projeto."
            )
        if tarefa.projeto is not self:
            raise ValidacaoError("A tarefa pertence a outro projeto.")
        self._tarefas[tarefa.id] = tarefa

    def criar_tarefa(
        self,
        tarefa_id: int,
        titulo: str,
        descricao: str,
        prioridade: Prioridade,
        data_limite: date,
    ) -> Tarefa:
        tarefa = Tarefa(
            tarefa_id,
            titulo,
            descricao,
            prioridade,
            data_limite,
            self,
        )
        self.adicionar_tarefa(tarefa)
        return tarefa

    def listar_tarefas(self) -> list[Tarefa]:
        return sorted(self._tarefas.values(), key=lambda tarefa: tarefa.id)

    def obter_tarefa(self, tarefa_id: int) -> Tarefa | None:
        return self._tarefas.get(tarefa_id)

    def remover_tarefa(self, tarefa_id: int) -> bool:
        return self._tarefas.pop(tarefa_id, None) is not None

    def calcular_progresso(self) -> float:
        if not self._tarefas:
            return 0.0
        concluidas = sum(
            tarefa.status is StatusTarefa.CONCLUIDA
            for tarefa in self._tarefas.values()
        )
        return concluidas / len(self._tarefas) * 100

    def __repr__(self) -> str:
        return f"Projeto(id={self.id}, nome={self.nome!r})"


class Usuario:
    """Usuário do sistema, responsável pelos próprios projetos."""

    _EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

    def __init__(self, id: int, nome: str, email: str, senha: str) -> None:
        self.id = _id_positivo(id, "ID do usuário")
        self.nome = _texto_obrigatorio(nome, "Nome")
        self.email = _texto_obrigatorio(email, "E-mail").lower()
        if not self._EMAIL.fullmatch(self.email):
            raise ValidacaoError("E-mail inválido.")
        if len(senha) < 4:
            raise ValidacaoError("A senha deve ter pelo menos 4 caracteres.")
        self._sal = secrets.token_bytes(16)
        self._senha_hash = self._gerar_hash(senha)
        self._projetos: dict[int, Projeto] = {}

    def _gerar_hash(self, senha: str) -> bytes:
        return hashlib.pbkdf2_hmac(
            "sha256", senha.encode("utf-8"), self._sal, 120_000
        )

    def verificar_senha(self, senha: str) -> bool:
        return hmac.compare_digest(self._senha_hash, self._gerar_hash(senha))

    def criar_projeto(
        self,
        projeto_id: int,
        nome: str,
        descricao: str,
        data_criacao: date | None = None,
    ) -> Projeto:
        if projeto_id in self._projetos:
            raise EntidadeDuplicadaError(
                f"Já existe um projeto com ID {projeto_id} para este usuário."
            )
        projeto = Projeto(projeto_id, nome, descricao, self, data_criacao)
        self._projetos[projeto.id] = projeto
        return projeto

    def listar_projetos(self) -> list[Projeto]:
        return sorted(self._projetos.values(), key=lambda projeto: projeto.id)

    def obter_projeto(self, projeto_id: int) -> Projeto | None:
        return self._projetos.get(projeto_id)

    def remover_projeto(self, projeto_id: int) -> bool:
        return self._projetos.pop(projeto_id, None) is not None

    def __repr__(self) -> str:
        return f"Usuario(id={self.id}, nome={self.nome!r}, email={self.email!r})"

