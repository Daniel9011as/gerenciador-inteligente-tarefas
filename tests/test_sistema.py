from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from gerenciador_tarefas.excecoes import (  # noqa: E402
    EntidadeDuplicadaError,
    EntidadeNaoEncontradaError,
    ValidacaoError,
)
from gerenciador_tarefas.exportacao import ExportadorRelatorios  # noqa: E402
from gerenciador_tarefas.modelos import Prioridade, StatusTarefa  # noqa: E402
from gerenciador_tarefas.relatorios import RelatorioService  # noqa: E402
from gerenciador_tarefas.servicos import GerenciadorTarefas  # noqa: E402


class GerenciadorTarefasTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sistema = GerenciadorTarefas()
        self.usuario = self.sistema.criar_usuario(
            1, "Daniel Silva", "daniel@example.com", "senha-segura"
        )
        self.projeto = self.sistema.criar_projeto(
            usuario_id=1,
            projeto_id=10,
            nome="Trabalho de POO",
            descricao="Implementar o gerenciador de tarefas",
            data_criacao=date(2026, 8, 20),
        )

    def test_cadastro_listagem_e_remocao_de_usuario(self) -> None:
        maria = self.sistema.criar_usuario(
            2, "Maria Souza", "maria@example.com", "outra-senha"
        )

        self.assertEqual([self.usuario, maria], self.sistema.listar_usuarios())
        self.assertTrue(maria.verificar_senha("outra-senha"))
        self.assertFalse(maria.verificar_senha("incorreta"))
        self.assertTrue(self.sistema.remover_usuario(2))
        self.assertEqual([self.usuario], self.sistema.listar_usuarios())

    def test_nao_permite_id_ou_email_de_usuario_duplicado(self) -> None:
        with self.assertRaises(EntidadeDuplicadaError):
            self.sistema.criar_usuario(
                1, "Outra pessoa", "outra@example.com", "senha"
            )
        with self.assertRaises(EntidadeDuplicadaError):
            self.sistema.criar_usuario(
                2, "Outra pessoa", "DANIEL@example.com", "senha"
            )

    def test_usuario_cria_lista_e_remove_projetos(self) -> None:
        segundo = self.sistema.criar_projeto(
            usuario_id=1,
            projeto_id=11,
            nome="Estudos",
            descricao="Organizar matérias",
        )

        self.assertEqual([self.projeto, segundo], self.sistema.listar_projetos(1))
        self.assertTrue(self.sistema.remover_projeto(1, 11))
        self.assertEqual([self.projeto], self.sistema.listar_projetos(1))

    def test_tarefas_status_atraso_e_progresso_do_projeto(self) -> None:
        tarefa_1 = self.sistema.criar_tarefa(
            usuario_id=1,
            projeto_id=10,
            tarefa_id=100,
            titulo="Criar classes",
            descricao="Implementar as entidades do domínio",
            prioridade=Prioridade.ALTA,
            data_limite=date(2026, 8, 24),
        )
        tarefa_2 = self.sistema.criar_tarefa(
            usuario_id=1,
            projeto_id=10,
            tarefa_id=101,
            titulo="Criar README",
            descricao="Documentar o projeto",
            prioridade=Prioridade.MEDIA,
            data_limite=date(2026, 8, 27),
        )

        self.assertEqual(0.0, self.projeto.calcular_progresso())
        tarefa_1.iniciar()
        self.assertEqual(StatusTarefa.EM_ANDAMENTO, tarefa_1.status)
        tarefa_1.marcar_concluida()
        self.assertEqual(50.0, self.projeto.calcular_progresso())
        self.assertFalse(tarefa_1.esta_vencida(date(2026, 8, 26)))
        self.assertFalse(tarefa_2.esta_vencida(date(2026, 8, 26)))

        tarefa_2.data_limite = date(2026, 8, 25)
        self.assertTrue(tarefa_2.esta_vencida(date(2026, 8, 26)))

    def test_relatorios_de_produtividade(self) -> None:
        concluida = self.sistema.criar_tarefa(
            1,
            10,
            100,
            "Modelar domínio",
            "Criar diagrama e classes",
            Prioridade.ALTA,
            date(2026, 8, 25),
        )
        concluida.marcar_concluida()
        pendente_urgente = self.sistema.criar_tarefa(
            1,
            10,
            101,
            "Publicar",
            "Enviar ao GitHub",
            Prioridade.URGENTE,
            date(2026, 8, 26),
        )
        pendente_baixa = self.sistema.criar_tarefa(
            1,
            10,
            102,
            "Revisar estilo",
            "Melhorar mensagens do terminal",
            Prioridade.BAIXA,
            date(2026, 8, 27),
        )

        relatorios = RelatorioService(self.sistema)
        pendentes = relatorios.tarefas_pendentes_por_prioridade()
        ranking = relatorios.projetos_por_progresso()
        concluidas = relatorios.total_concluidas_por_usuario()

        self.assertEqual(
            [pendente_urgente, pendente_baixa],
            [item.tarefa for item in pendentes],
        )
        self.assertEqual(self.projeto, ranking[0].projeto)
        self.assertAlmostEqual(100 / 3, ranking[0].percentual)
        self.assertEqual(1, concluidas[0].total_concluidas)

    def test_exporta_relatorio_csv(self) -> None:
        self.sistema.criar_tarefa(
            1,
            10,
            100,
            "Entregar atividade",
            "Anexar a folha de identificação",
            Prioridade.URGENTE,
            date(2026, 8, 26),
        )

        with tempfile.TemporaryDirectory() as diretorio:
            destino = Path(diretorio) / "relatorio.csv"
            ExportadorRelatorios(self.sistema).exportar_csv(destino)

            with destino.open(encoding="utf-8-sig", newline="") as arquivo:
                linhas = list(csv.DictReader(arquivo))

        self.assertEqual(1, len(linhas))
        self.assertEqual("Entregar atividade", linhas[0]["tarefa"])
        self.assertEqual("Urgente", linhas[0]["prioridade"])
        self.assertEqual("Pendente", linhas[0]["status"])

    def test_validacoes_e_busca_de_entidade_inexistente(self) -> None:
        with self.assertRaises(ValidacaoError):
            self.sistema.criar_usuario(2, "", "email-invalido", "123")
        with self.assertRaises(EntidadeNaoEncontradaError):
            self.sistema.listar_projetos(999)
        with self.assertRaises(ValidacaoError):
            self.sistema.criar_tarefa(
                1,
                10,
                100,
                "",
                "Sem título",
                Prioridade.MEDIA,
                date(2026, 8, 30),
            )


if __name__ == "__main__":
    unittest.main()
