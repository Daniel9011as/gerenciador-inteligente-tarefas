"""Gera a folha de identificação preenchível exigida na atividade."""

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "docs" / "folha-identificacao.pdf"

LARGURA, ALTURA = A4
MARINHO = HexColor("#0B1437")
ROXO = HexColor("#5B21B6")
LARANJA = HexColor("#F97316")
CINZA_CLARO = HexColor("#F4F5F9")
CINZA = HexColor("#5B6475")
BORDA = HexColor("#D8DCE7")
VERDE = HexColor("#15803D")


def caixa_arredondada(
    pdf: canvas.Canvas,
    x: float,
    y: float,
    largura: float,
    altura: float,
    preenchimento=white,
    borda=BORDA,
    raio: float = 10,
) -> None:
    pdf.setFillColor(preenchimento)
    pdf.setStrokeColor(borda)
    pdf.setLineWidth(0.8)
    pdf.roundRect(x, y, largura, altura, raio, stroke=1, fill=1)


def campo(
    pdf: canvas.Canvas,
    nome: str,
    rotulo: str,
    x: float,
    y: float,
    largura: float,
    valor: str = "",
    tamanho: int = 10,
) -> None:
    pdf.setFillColor(MARINHO)
    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.drawString(x, y + 27, rotulo.upper())
    pdf.acroForm.textfield(
        name=nome,
        tooltip=rotulo,
        x=x,
        y=y,
        width=largura,
        height=22,
        value=valor,
        fontName="Helvetica",
        fontSize=tamanho,
        textColor=MARINHO,
        fillColor=white,
        borderColor=BORDA,
        borderWidth=1,
        borderStyle="solid",
        forceBorder=True,
    )


def checkbox_visual(
    pdf: canvas.Canvas, x: float, y: float, texto: str, marcado: bool = False
) -> None:
    pdf.setStrokeColor(VERDE)
    pdf.setLineWidth(1.2)
    pdf.setFillColor(VERDE if marcado else white)
    pdf.roundRect(x, y - 1, 11, 11, 2, stroke=1, fill=1)
    if marcado:
        pdf.setStrokeColor(white)
        pdf.setLineWidth(1.4)
        pdf.line(x + 2.5, y + 4, x + 4.8, y + 1.8)
        pdf.line(x + 4.8, y + 1.8, x + 9, y + 7.5)
    pdf.setFillColor(MARINHO)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(x + 19, y, texto)


def gerar() -> Path:
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(DESTINO), pagesize=A4)
    pdf.setTitle("Folha de Identificação - Atividade Prática Unidade 03")
    pdf.setAuthor("Estudante - Anhanguera")
    pdf.setSubject("Gerenciador Inteligente de Tarefas")

    # Cabeçalho
    pdf.setFillColor(MARINHO)
    pdf.rect(0, ALTURA - 155, LARGURA, 155, stroke=0, fill=1)
    pdf.setFillColor(LARANJA)
    pdf.rect(0, ALTURA - 8, LARGURA, 8, stroke=0, fill=1)
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(42, ALTURA - 39, "ANHANGUERA")
    pdf.setFillColor(HexColor("#C7CEE0"))
    pdf.setFont("Helvetica", 8.5)
    pdf.drawRightString(LARGURA - 42, ALTURA - 39, "PROGRAMAÇÃO ORIENTADA A OBJETOS")
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(42, ALTURA - 82, "FOLHA DE IDENTIFICAÇÃO")
    pdf.setFillColor(HexColor("#D9DCEF"))
    pdf.setFont("Helvetica", 11)
    pdf.drawString(42, ALTURA - 107, "Atividade Prática - Unidade 03")
    pdf.setFillColor(LARANJA)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(42, ALTURA - 132, "GERENCIADOR INTELIGENTE DE TAREFAS")

    # Identificação
    caixa_arredondada(pdf, 32, 456, LARGURA - 64, 215)
    pdf.setFillColor(ROXO)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(48, 643, "1. IDENTIFICAÇÃO DO ALUNO")
    pdf.setFillColor(CINZA)
    pdf.setFont("Helvetica", 8)
    pdf.drawRightString(LARGURA - 48, 644, "Clique nos campos para preencher")

    campo(pdf, "nome_completo", "Nome completo", 48, 592, LARGURA - 96)
    campo(pdf, "matricula", "Matrícula", 48, 538, 230)
    campo(pdf, "turma", "Turma", 302, 538, LARGURA - 350)
    campo(
        pdf,
        "curso_periodo",
        "Curso e período",
        48,
        484,
        332,
        "Sistemas de Informação - ____º período",
    )
    campo(pdf, "data", "Data", 404, 484, LARGURA - 452, "26/08/2026")

    # Repositório
    caixa_arredondada(pdf, 32, 338, LARGURA - 64, 96, preenchimento=CINZA_CLARO)
    pdf.setFillColor(ROXO)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(48, 407, "2. LINK DO REPOSITÓRIO PÚBLICO")
    campo(
        pdf,
        "link_github",
        "URL completa do GitHub",
        48,
        354,
        LARGURA - 96,
        "https://github.com/Daniel9011as/gerenciador-inteligente-tarefas",
        9,
    )

    # Resumo e checklist
    caixa_arredondada(pdf, 32, 147, 325, 169)
    pdf.setFillColor(ROXO)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(48, 288, "3. RESUMO DO PROJETO")
    pdf.setFillColor(MARINHO)
    pdf.setFont("Helvetica", 9)
    linhas = [
        "Sistema em Python 3.11+ para cadastrar usuários,",
        "projetos e tarefas; definir prioridade e status;",
        "calcular progresso; identificar atrasos; gerar",
        "relatórios; e exportar dados em CSV e TXT.",
    ]
    for indice, linha in enumerate(linhas):
        pdf.drawString(48, 264 - indice * 15, linha)

    pdf.setFillColor(CINZA)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(48, 190, "TECNOLOGIAS")
    pdf.setFont("Helvetica", 8.5)
    pdf.drawString(48, 174, "Python - POO - CLI - unittest - Git/GitHub")

    caixa_arredondada(pdf, 373, 147, LARGURA - 405, 169)
    pdf.setFillColor(ROXO)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(389, 288, "4. CHECKLIST")
    checkbox_visual(pdf, 389, 259, "Repositório público", marcado=True)
    checkbox_visual(pdf, 389, 232, "Código-fonte completo", marcado=True)
    checkbox_visual(pdf, 389, 205, "README documentado", marcado=True)
    checkbox_visual(pdf, 389, 178, "Testes aprovados", marcado=True)

    # Aviso e rodapé
    pdf.setFillColor(HexColor("#FFF7ED"))
    pdf.setStrokeColor(HexColor("#FDBA74"))
    pdf.roundRect(32, 79, LARGURA - 64, 50, 8, stroke=1, fill=1)
    pdf.setFillColor(LARANJA)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(48, 108, "ATENÇÃO")
    pdf.setFillColor(MARINHO)
    pdf.setFont("Helvetica", 8.5)
    pdf.drawString(
        48,
        91,
        "Preencha todos os campos, confirme que o link abre sem login e anexe este PDF.",
    )

    pdf.setFillColor(MARINHO)
    pdf.rect(0, 0, LARGURA, 51, stroke=0, fill=1)
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(42, 28, "PRAZO INDICADO NO MATERIAL: 26/08/2026 ÀS 22:40")
    pdf.setFont("Helvetica", 8)
    pdf.drawRightString(LARGURA - 42, 28, "Projeto de POO - Unidade 03")

    pdf.showPage()
    pdf.save()
    return DESTINO


if __name__ == "__main__":
    print(gerar())
