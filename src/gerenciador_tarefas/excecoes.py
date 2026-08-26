"""Exceções de domínio usadas pelo sistema."""


class GerenciadorError(Exception):
    """Erro-base apresentado de forma amigável na interface."""


class ValidacaoError(GerenciadorError):
    """Os dados informados não atendem às regras do domínio."""


class EntidadeDuplicadaError(GerenciadorError):
    """Já existe uma entidade com o identificador informado."""


class EntidadeNaoEncontradaError(GerenciadorError):
    """A entidade solicitada não foi encontrada."""

