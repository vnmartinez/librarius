"""Gerador de slides `.pptx` no padrão visual UniRV / Fasoft, em python-pptx (sem Node).

Reimplementa, em Python, o "Padrão Visual de Slides - UniRV Fasoft" (`09 - Modelos/Modelo de Slides
UniRV/`): medidas, paleta e componentes são transcritos das seções do documento, que fica no
workspace do professor e é apenas lido (os logos vêm da pasta `assets/` do modelo, nunca do Git).

Cobertura do MVP, por tipo de slide (`conteudo["slides"]["slides"][i]["tipo"]`):

- `capa`        — §2.4 capa (`titleSlide`): caixa verde, curso, "Aula NN — tema", professor, período, logos.
- `topicos`     — §3 `bullets` com marcador ▪ (até 6 itens).
- `codigo`      — §3 `code`: bloco escuro 10231B, Courier New, comentários 8FB79E (até 16 linhas).
- `tabela`      — §3 `table`: cabeçalho verde, 1ª coluna em negrito verde, linhas alternadas.
- `cards`       — §3 `cards`: selo circular + título + texto, 2 a 4 colunas.
- `fluxo`       — §3 `flow`: 3 a 5 etapas com setas.
- `nota`        — §3 `note` em destaque (rótulo + texto).
- `referencias` — §3 `refsSlide`.

Qualquer slide de conteúdo aceita `lead` (linha-guia, §3), `nota` (`{rotulo, texto}`, fecho do slide) e
`notas_professor` (vai para as notas do apresentador, nunca para a projeção).

Medidas (§2.1, §2.4): 10 × 5,625 pol. (9 144 000 × 5 143 500 EMU); barra do título 0,47/0,28/7,07/0,63;
filete inferior 0,18/5,33/9,35/0,108; número do slide 8,95/5,02/0,55/0,26; área útil y 1,02–5,00.
Paleta (§2.2) e tipografia (§2.3): Calibri; Courier New só no código; nunca abaixo de 9 pt.
"""
from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path
from typing import Callable

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

from acad.erros import ErroAcad

# §2.2 Paleta
VERDE = "015537"
VERDE2 = "0E7A4E"
VERDE_CLARO = "E4EFE9"
VERDE_CLARO2 = "F2F7F4"
TINTA = "1C2B24"
CORPO = "2E3B34"
APAGADO = "6A7A72"
LINHA = "C9D8D0"
BRANCO = "FFFFFF"
SUBTITULO_CAPA = "D7E7DF"
CODIGO_FUNDO = "10231B"
CODIGO_COMENTARIO = "8FB79E"
CODIGO_TEXTO = "D8E8DF"

# §2.3 Tipografia
FONTE = "Calibri"
FONTE_CODIGO = "Courier New"

# §2.1 Dimensões
LARGURA = 9144000
ALTURA = 5143500

# §2.5 Assets (lidos da pasta do modelo, no workspace)
LOGOS = {"cabecalho": "logo-header-unirv.png", "unirv": "logo-unirv.png", "fasoft": "logo-fasoft.png"}

MAX_TOPICOS = 6
MAX_LINHAS_CODIGO = 16
MAX_LINHAS_TABELA = 8
TIPOS_SEM_LEAD = {"capa", "referencias"}


def _rgb(hexa: str) -> RGBColor:
    return RGBColor.from_string(hexa)


def _sem_estilo(forma) -> None:
    """Tira o <p:style> padrão (sombra e contorno do tema) para a forma ficar como no pptxgenjs."""
    estilo = forma._element.find(qn("p:style"))
    if estilo is not None:
        forma._element.remove(estilo)


def _forma(slide, tipo, x, y, w, h, preenchimento, linha=None, largura_linha=0.75, raio=None):
    forma = slide.shapes.add_shape(tipo, Inches(x), Inches(y), Inches(w), Inches(h))
    _sem_estilo(forma)
    forma.fill.solid()
    forma.fill.fore_color.rgb = _rgb(preenchimento)
    if linha:
        forma.line.color.rgb = _rgb(linha)
        forma.line.width = Pt(largura_linha)
    else:
        forma.line.fill.background()
    if raio is not None:
        forma.adjustments[0] = min(0.5, raio / min(w, h))
    return forma


def _retangulo(slide, x, y, w, h, cor):
    return _forma(slide, MSO_SHAPE.RECTANGLE, x, y, w, h, cor)


def _caixa_arredondada(slide, x, y, w, h, preenchimento, linha, largura_linha, raio):
    return _forma(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, preenchimento, linha, largura_linha, raio)


def _estilizar(run, tamanho, cor, negrito=False, italico=False, fonte=FONTE):
    run.font.name = fonte
    run.font.size = Pt(tamanho)
    run.font.bold = negrito
    run.font.italic = italico
    run.font.color.rgb = _rgb(cor)


def _texto(slide, x, y, w, h, paragrafos, alinhamento=PP_ALIGN.LEFT, ancora=MSO_ANCHOR.TOP):
    """`paragrafos`: lista de listas de (texto, {tamanho, cor, negrito, italico, fonte})."""
    caixa = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    quadro = caixa.text_frame
    quadro.word_wrap = True
    quadro.auto_size = MSO_AUTO_SIZE.NONE
    quadro.margin_left = quadro.margin_right = quadro.margin_top = quadro.margin_bottom = 0
    quadro.vertical_anchor = ancora
    for i, runs in enumerate(paragrafos):
        paragrafo = quadro.paragraphs[0] if i == 0 else quadro.add_paragraph()
        paragrafo.alignment = alinhamento
        for texto, estilo in runs:
            run = paragrafo.add_run()
            run.text = texto
            _estilizar(run, **estilo)
    return caixa


def _estilo(tamanho, cor=CORPO, negrito=False, italico=False, fonte=FONTE):
    return {"tamanho": tamanho, "cor": cor, "negrito": negrito, "italico": italico, "fonte": fonte}


def _marcador(paragrafo, nivel: int) -> None:
    """Marcador ▪ (§3 `bullets`) com recuo pendente."""
    pPr = paragrafo._p.get_or_add_pPr()
    recuo = int(Inches(0.2))
    pPr.set("marL", str(recuo * (nivel + 1)))
    pPr.set("indent", str(-recuo))
    fonte = etree.SubElement(pPr, qn("a:buFont"))
    fonte.set("typeface", "Arial")
    marca = etree.SubElement(pPr, qn("a:buChar"))
    marca.set("char", "▪")


class GeradorSlidesPptx:
    """`gerar(conteudo, template) -> bytes`.

    `template` é a pasta `Modelo de Slides UniRV` (só para ler os logos em `assets/`); sem ela, os
    slides saem sem logos. `ler_bytes` permite ler pela porta de leitura do workspace.
    """

    def __init__(self, ler_bytes: Callable[[Path], bytes] | None = None):
        self._ler = ler_bytes or (lambda caminho: caminho.read_bytes())
        self._template: Path | None = None

    # ---------- entrada ----------
    def gerar(self, conteudo: dict, template: Path | None) -> bytes:
        self._template = Path(template) if template else None
        itens = conteudo.get("slides", {}).get("slides", [])
        apresentacao = Presentation()
        apresentacao.slide_width = Emu(LARGURA)
        apresentacao.slide_height = Emu(ALTURA)
        apresentacao.core_properties.title = str(conteudo.get("tema", ""))
        apresentacao.core_properties.author = str(conteudo.get("professor", ""))
        apresentacao.core_properties.subject = str(conteudo.get("tema", ""))
        for posicao, item in enumerate(itens, 1):
            tipo = item.get("tipo")
            if tipo == "capa":
                slide = self._capa(apresentacao, conteudo, item)
            else:
                slide = self._conteudo(apresentacao, conteudo, item, posicao)
            if item.get("notas_professor"):
                slide.notes_slide.notes_text_frame.text = str(item["notas_professor"])
        saida = io.BytesIO()
        apresentacao.save(saida)
        return saida.getvalue()

    # ---------- logos ----------
    def _logo(self, slide, nome: str, x, y, w, h) -> None:
        if self._template is None:
            return
        try:
            dados = self._ler(self._template / "assets" / LOGOS[nome])
        except (OSError, ErroAcad):
            return
        slide.shapes.add_picture(io.BytesIO(dados), Inches(x), Inches(y), Inches(w), Inches(h))

    # ---------- moldura ----------
    @staticmethod
    def _novo_slide(apresentacao):
        slide = apresentacao.slides.add_slide(apresentacao.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = _rgb(BRANCO)
        return slide

    def _capa(self, apresentacao, conteudo: dict, item: dict):
        s = self._novo_slide(apresentacao)
        curso = item.get("curso") or conteudo.get("curso") or ""
        aula = item.get("aula") or conteudo.get("aula_id") or ""
        tema = item.get("titulo") or conteudo.get("tema") or ""
        professor = item.get("professor") or conteudo.get("professor") or ""
        periodo = item.get("periodo") or conteudo.get("periodo") or ""
        ano = item.get("ano") or conteudo.get("ano") or datetime.now().year
        _retangulo(s, 0.7, 0.5, 8.6, 1.78, VERDE)
        _texto(s, 0.8, 0.72, 8.4, 0.62, [[(curso, _estilo(27, BRANCO, True))]], PP_ALIGN.CENTER, MSO_ANCHOR.TOP)
        rotulo = f"{aula} — {tema}" if aula else tema
        _texto(s, 0.9, 1.36, 8.2, 0.78, [[(rotulo, _estilo(15, SUBTITULO_CAPA, italico=True))]], PP_ALIGN.CENTER)
        if professor:
            _texto(s, 0.7, 2.42, 8.6, 0.3, [[(professor, _estilo(13.5, TINTA))]], PP_ALIGN.CENTER)
        if periodo:
            _texto(s, 0.7, 2.72, 8.6, 0.3, [[(periodo, _estilo(12, APAGADO, italico=True))]], PP_ALIGN.CENTER)
        self._logo(s, "unirv", 4.02, 3.16, 0.72, 0.72)
        self._logo(s, "fasoft", 4.96, 3.29, 0.87, 0.58)
        _texto(s, 0.7, 4.02, 8.6, 0.26, [[("UNIVERSIDADE DE RIO VERDE (UniRV)", _estilo(11.5, CORPO))]], PP_ALIGN.CENTER)
        _texto(s, 0.7, 4.26, 8.6, 0.26, [[("Bacharelado em Engenharia de Software", _estilo(11.5, CORPO))]], PP_ALIGN.CENTER)
        _texto(s, 0.7, 4.62, 8.6, 0.28, [[(f"RIO VERDE — {ano}", _estilo(11, VERDE, True))]], PP_ALIGN.CENTER)
        _retangulo(s, 0.18, 5.33, 9.35, 0.108, VERDE)
        return s

    def _moldura(self, apresentacao, titulo: str, posicao: int):
        s = self._novo_slide(apresentacao)
        _retangulo(s, 0.47, 0.28, 7.07, 0.63, VERDE)
        _texto(s, 0.63, 0.28, 6.8, 0.63, [[(titulo, _estilo(14, BRANCO, True))]], ancora=MSO_ANCHOR.MIDDLE)
        self._logo(s, "cabecalho", 7.65, 0.28, 1.91, 0.63)
        _retangulo(s, 0.18, 5.33, 9.35, 0.108, VERDE)
        _texto(s, 8.95, 5.02, 0.55, 0.26, [[(str(posicao), _estilo(9, APAGADO))]], PP_ALIGN.RIGHT)
        return s

    # ---------- componentes (§3) ----------
    @staticmethod
    def _lead(s, texto: str) -> None:
        _texto(s, 0.55, 1.02, 8.95, 0.42, [[(texto, _estilo(13, VERDE, True))]], ancora=MSO_ANCHOR.MIDDLE)

    @staticmethod
    def _nota(s, rotulo: str, texto: str, y: float = 4.35, h: float = 0.8, tamanho: float = 11.5) -> None:
        _caixa_arredondada(s, 0.55, y, 8.9, h, VERDE_CLARO, VERDE2, 0.9, 0.05)
        _texto(s, 0.71, y + 0.06, 8.58, h - 0.12,
               [[(rotulo + "  ", _estilo(tamanho, VERDE, True)), (texto, _estilo(tamanho, CORPO))]],
               ancora=MSO_ANCHOR.MIDDLE)

    @staticmethod
    def _topicos(s, itens: list, y: float, h: float) -> None:
        paragrafos = []
        for item in itens:
            dados = {"t": item} if isinstance(item, str) else item
            paragrafos.append((dados.get("t", ""), dados))
        caixa = _texto(s, 0.62, y, 8.8, h, [[(t, _estilo(d.get("sz", 13), d.get("c", CORPO), bool(d.get("b")))) ]
                                              for t, d in paragrafos])
        for paragrafo, (_, dados) in zip(caixa.text_frame.paragraphs, paragrafos):
            paragrafo.space_after = Pt(7)
            _marcador(paragrafo, int(dados.get("lvl", 0)))

    @staticmethod
    def _codigo(s, linhas: list, y: float, h: float) -> None:
        _caixa_arredondada(s, 0.55, y, 8.9, h, CODIGO_FUNDO, VERDE, 1, 0.04)
        tamanho = 10.5 if len(linhas) <= 14 else 10
        paragrafos = [[(l["t"], _estilo(tamanho, l.get("c", CODIGO_TEXTO), bool(l.get("b")), fonte=FONTE_CODIGO))]
                      for l in linhas]
        _texto(s, 0.75, y + 0.12, 8.5, h - 0.24, paragrafos)

    @staticmethod
    def _tabela(s, linhas: list, y: float) -> None:
        colunas = max(len(l) for l in linhas)
        linhas = [list(l) + [""] * (colunas - len(l)) for l in linhas]
        total = int(Inches(8.9))
        pesos = [max(6, max(len(str(l[c])) for l in linhas)) for c in range(colunas)]
        larguras = [int(total * p / sum(pesos)) for p in pesos]
        larguras[-1] += total - sum(larguras)
        denso = len(linhas) > 6  # §3 `table`: 8 linhas usam rowH 0,32 e fonte 9,5
        altura_linha = 0.32 if denso else 0.3
        forma = s.shapes.add_table(len(linhas), colunas, Inches(0.55), Inches(y), Emu(total),
                                   Inches(altura_linha * len(linhas)))
        tabela = forma.table
        propriedades = tabela._tbl.tblPr
        for atributo in ("firstRow", "bandRow"):
            propriedades.set(atributo, "0")
        for c, largura in enumerate(larguras):
            tabela.columns[c].width = Emu(largura)
        for r, linha in enumerate(linhas):
            tabela.rows[r].height = Inches(altura_linha)
            for c, texto in enumerate(linha):
                celula = tabela.cell(r, c)
                cabecalho = r == 0
                celula.fill.solid()
                celula.fill.fore_color.rgb = _rgb(VERDE if cabecalho else (VERDE_CLARO2 if r % 2 == 0 else BRANCO))
                celula.margin_left = celula.margin_right = Pt(7)
                celula.margin_top = celula.margin_bottom = Pt(4)
                celula.vertical_anchor = MSO_ANCHOR.MIDDLE
                paragrafo = celula.text_frame.paragraphs[0]
                run = paragrafo.add_run()
                run.text = str(texto)
                if cabecalho:
                    _estilizar(run, 10 if denso else 11.5, BRANCO, True)
                else:
                    _estilizar(run, 9.5 if denso else 10.5, VERDE if c == 0 else CORPO, c == 0)
                _bordas(celula)

    def _cards(self, s, itens: list, y: float, limite_y: float) -> None:
        n = len(itens)
        colunas = {1: 1, 2: 2, 3: 3, 4: 2}.get(n, 3)
        linhas = -(-n // colunas)
        gx, gy, largura_total = 0.28, 0.22, 8.9
        h = min(1.6, (limite_y - y - gy * (linhas - 1)) / linhas)
        w = (largura_total - gx * (colunas - 1)) / colunas
        for i, item in enumerate(itens):
            cx = 0.55 + (i % colunas) * (w + gx)
            cy = y + (i // colunas) * (h + gy)
            _caixa_arredondada(s, cx, cy, w, h, VERDE_CLARO2, LINHA, 0.75, 0.06)
            _forma(s, MSO_SHAPE.OVAL, cx + 0.16, cy + 0.16, 0.42, 0.42, item.get("cor", VERDE))
            etiqueta = str(item.get("tag") or i + 1)
            _texto(s, cx + 0.16, cy + 0.16, 0.42, 0.42,
                   [[(etiqueta, _estilo(9 if len(etiqueta) > 2 else 13, BRANCO, True))]], PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
            _texto(s, cx + 0.68, cy + 0.14, w - 0.84, 0.46,
                   [[(item.get("titulo", ""), _estilo(12.5, VERDE, True))]], ancora=MSO_ANCHOR.MIDDLE)
            _texto(s, cx + 0.2, cy + 0.62, w - 0.4, max(0.2, h - 0.76),
                   [[(item.get("texto", ""), _estilo(11, CORPO))]])

    def _fluxo(self, s, etapas: list, y: float, h: float) -> None:
        n = len(etapas)
        seta = 0.26
        largura = (8.9 - seta * (n - 1)) / n
        for i, etapa in enumerate(etapas):
            bx = 0.55 + i * (largura + seta)
            _caixa_arredondada(s, bx, y, largura, h, VERDE_CLARO if i % 2 else VERDE_CLARO2, VERDE2, 0.9, 0.06)
            _texto(s, bx + 0.08, y + 0.08, largura - 0.16, 0.36,
                   [[(etapa.get("t", ""), _estilo(11.5, VERDE, True))]], PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
            _texto(s, bx + 0.08, y + 0.44, largura - 0.16, h - 0.52,
                   [[(etapa.get("d", ""), _estilo(9.5, CORPO))]], PP_ALIGN.CENTER)
            if i < n - 1:
                _forma(s, MSO_SHAPE.RIGHT_ARROW, bx + largura + 0.04, y + h / 2 - 0.11, seta - 0.08, 0.22, VERDE2)

    # ---------- slide de conteúdo ----------
    def _conteudo(self, apresentacao, conteudo: dict, item: dict, posicao: int):
        tipo = item.get("tipo")
        titulo = "Referências" if tipo == "referencias" else item.get("titulo", "")
        s = self._moldura(apresentacao, titulo, posicao)
        lead = "Bibliografia básica e fontes normativas" if tipo == "referencias" and not item.get("lead") else item.get("lead")
        if lead:
            self._lead(s, lead)
        nota = item.get("nota")
        # a nota de fecho começa em 4,5; o conteúdo acima dela termina em 4,4
        limite = 4.4 if nota else 5.0
        y = 1.55 if lead else 1.1
        if tipo == "topicos":
            self._topicos(s, item.get("itens", []), y, limite - y)
        elif tipo == "referencias":
            self._topicos(s, [{"t": r, "sz": 11} for r in item.get("itens", [])], 1.5, limite - 1.5)
        elif tipo == "codigo":
            linhas = _linhas_de_codigo(item)
            h = min(limite - y - 0.05, len(linhas) * 0.19 + 0.3)
            self._codigo(s, linhas, y, h)
        elif tipo == "tabela":
            self._tabela(s, item.get("linhas", []), 1.5 if lead else y)
        elif tipo == "cards":
            self._cards(s, item.get("itens", []), y - 0.05, limite)
        elif tipo == "fluxo":
            self._fluxo(s, item.get("itens", []), y + 0.15, 1.3)
        elif tipo == "nota":
            self._nota(s, item.get("rotulo", ""), item.get("texto", ""), y + 0.15, 1.6, 14)
        else:
            raise ErroAcad("slide-tipo-invalido", f"Não conheço o tipo de slide '{tipo}'.")
        if nota:
            self._nota(s, nota.get("rotulo", ""), nota.get("texto", ""), 4.5, 0.5, 10.5)
        return s


def _linhas_de_codigo(item: dict) -> list[dict]:
    if "linhas" in item:
        return [{"t": l} if isinstance(l, str) else l for l in item["linhas"]]
    linhas = []
    for texto in str(item.get("codigo", "")).split("\n"):
        comentario = texto.lstrip().startswith(("//", "#", "--"))
        linhas.append({"t": texto, **({"c": CODIGO_COMENTARIO} if comentario else {})})
    return linhas


def _bordas(celula) -> None:
    """Traço fino `C9D8D0` em volta da célula (§3 `table`)."""
    tcPr = celula._tc.get_or_add_tcPr()
    for i, lado in enumerate(("a:lnL", "a:lnR", "a:lnT", "a:lnB")):
        for antigo in tcPr.findall(qn(lado)):
            tcPr.remove(antigo)
        ln = etree.Element(qn(lado), w=str(int(Pt(0.5))), cap="flat", cmpd="sng", algn="ctr")
        preenchimento = etree.SubElement(ln, qn("a:solidFill"))
        etree.SubElement(preenchimento, qn("a:srgbClr")).set("val", LINHA)
        etree.SubElement(ln, qn("a:prstDash")).set("val", "solid")
        tcPr.insert(i, ln)


def avisos_editoriais(slides: list[dict]) -> list[str]:
    """Regras editoriais verificáveis do padrão (§3, §4, §6); devolvem avisos em português simples."""
    avisos = []
    anterior = None
    for numero, item in enumerate(slides, 1):
        tipo = item.get("tipo")
        titulo = item.get("titulo") or tipo
        if tipo not in TIPOS_SEM_LEAD and not item.get("lead"):
            avisos.append(f"O slide {numero} ({titulo}) está sem linha-guia.")
        if tipo == "topicos" and len(item.get("itens", [])) > MAX_TOPICOS:
            avisos.append(f"O slide {numero} ({titulo}) tem mais de {MAX_TOPICOS} itens; divida em dois slides.")
        if tipo == "codigo" and len(_linhas_de_codigo(item)) > MAX_LINHAS_CODIGO:
            avisos.append(f"O slide {numero} ({titulo}) tem mais de {MAX_LINHAS_CODIGO} linhas de código.")
        if tipo == "tabela" and len(item.get("linhas", [])) > MAX_LINHAS_TABELA + 1:
            avisos.append(f"O slide {numero} ({titulo}) tem mais de {MAX_LINHAS_TABELA} linhas na tabela.")
        if tipo == anterior and tipo not in {"capa", "referencias"}:
            avisos.append(f"Há dois slides seguidos do mesmo tipo ({numero - 1} e {numero}); alterne o formato.")
        anterior = tipo
    return avisos
