from __future__ import annotations

from datetime import datetime
from pathlib import Path
import logging
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fpdf import FPDF
from fpdf.enums import Align, XPos, YPos

LOG = logging.getLogger(__name__)
MEDIA_SETOR = 0.15
META_ERROS = 0.1


def _texto_pdf(valor: object) -> str:
    texto = str(valor).replace('—', '-').replace('–', '-')
    return texto.encode('latin-1', errors='replace').decode('latin-1')

def _escrever(pdf: FPDF, texto: object, *, tamanho: int = 10, negrito: bool = False) -> None:
    pdf.set_font('Courier', 'B' if negrito else '', tamanho)
    pdf.multi_cell(0, 6, _texto_pdf(texto), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

def _percentual_erros(df: pd.DataFrame, tamanho: int | float) -> float:
    if tamanho <= 0:
        raise ValueError('O total de linhas analisadas deve ser maior que zero.')
    if 'Qtd' not in df.columns:
        raise ValueError("Coluna obrigatória ausente: 'Qtd'.")
    return float(pd.to_numeric(df['Qtd'], errors='coerce').fillna(0).sum()) / tamanho * 100

def grafico_resultado(df_IMPR, tamanho, path, st=None):
    percentual = _percentual_erros(df_IMPR, tamanho)
    fator = percentual / MEDIA_SETOR
    destino = Path(path) / 'IMAGENS' / 'grafico_erro.png'
    destino.parent.mkdir(parents=True, exist_ok=True)

    metas = [META_ERROS, MEDIA_SETOR]
    valores = [percentual, MEDIA_SETOR]
    categorias = ['ERROS', 'ERROS SETOR']

    def cor(valor: float, meta: float):
        distancia = (valor - meta) / meta
        intensidade = min(1.0, abs(distancia))
        return (1.0, 1.0 - intensidade, 1.0 - intensidade) if distancia >= 0 else (1.0 - intensidade, 1.0, 1.0 - intensidade)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    try:
        pos = np.arange(len(categorias))
        largura = 0.35
        ax.bar(pos, metas, largura, color='green', label='Meta / referência')
        ax.bar(pos + largura, valores, largura, color=[cor(v, m) for v, m in zip(valores, metas)], label='Valor geral')
        ax.set_ylabel('%')
        ax.set_title('ERROS (INDICADOR)')
        ax.set_xticks(pos + largura / 2, categorias)
        ax.grid(axis='y', alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(destino, dpi=150)
    finally:
        plt.close(fig)
    return fator


class _PDFValidador(FPDF):
    def __init__(self, empresa: object):
        super().__init__()
        self.empresa = empresa
        self.alias_nb_pages()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_left_margin(25)
        self.set_right_margin(20)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Courier', 'B', 9)
        self.set_text_color(110, 110, 110)
        self.cell(0, 9, 'RESULTADO DO VALIDADOR', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.set_draw_color(160, 160, 160)
        self.line(20, 20, 190, 20)
        self.ln(9)
        self.set_text_color(0, 0, 0)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font('Courier', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', align='C')

    def capa(self, texto: str = ''):
        self.add_page()
        self.set_fill_color(48, 48, 48)
        self.rect(0, 0, 210, 297, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 22)
        self.ln(65)
        self.multi_cell(0, 13, _texto_pdf(f'Relatório de Análise\nEmpresa {self.empresa}'), align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', '', 13)
        self.ln(10)
        self.multi_cell(0, 9, 'Etapa de Validação de Estrutura', align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if texto:
            self.ln(22)
            self.set_font('Helvetica', '', 11)
            self.multi_cell(0, 7, _texto_pdf(texto), align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)


def _revisar(revisor, texto: str, instrucao: str = '') -> str:
    if revisor is None:
        return texto
    try:
        return str(revisor.revisar(texto, instrucao_extra=instrucao))
    except Exception:
        LOG.exception('Falha na revisão por IA; usando texto original.')
        return texto


def _criar_revisor(usar_ia: bool, st=None):
    if not usar_ia or not st:
        return None
    try:
        from ai_funcoes import RevisorLLM
        return RevisorLLM(modelo= st.session_state.modelo)
    except Exception:
        LOG.exception('RevisorLLM indisponível; relatório seguirá sem revisão.')
        return None


def _criar_resumidor(usar_ia: bool, st=None):
    if not usar_ia:
        return None
    try:
        from ai_funcoes import ResumoValidador
        return ResumoValidador(model=st.session_state.modelo)
    except Exception:
        LOG.exception('ResumoValidador indisponível; relatório seguirá sem resumo por IA.')
        return None


def _fechar(recurso) -> None:
    if recurso is not None and hasattr(recurso, 'close'):
        try:
            recurso.close()
        except Exception:
            LOG.exception('Falha ao fechar recurso de IA.')


def _detalhar_tabela(pdf: _PDFValidador, tabela: str, df: pd.DataFrame, resumidor) -> None:
    pdf.add_page()
    _escrever(pdf, f'Tabela: {tabela}', tamanho=12, negrito=True)
    pdf.ln(4)
    amostra = df.drop_duplicates().head(5000)
    if resumidor is not None:
        try:
            resumo = resumidor.gerar_resumo(amostra, max_linhas=5000)
            if resumo:
                _escrever(pdf, resumo)
                pdf.ln(4)
        except Exception:
            LOG.exception('Não foi possível resumir a tabela %s', tabela)

    _escrever(pdf, f'Total de tipos de erros encontrados: {len(df.drop_duplicates())}.')
    if len(df.drop_duplicates()) >= 5000:
        _escrever(pdf, 'O relatório apresenta no máximo 5000 tipos de erros nesta tabela.')
    _escrever(pdf, 'A seguir, os erros por tipo, quantidade e exemplos de registros:')
    pdf.ln(4)
    campos = ['Campo', 'Descrição do Erro', 'Qtd', 'Exemplos (Amostra, linha do arquivo)']
    for _, linha in amostra.iterrows():
        campo, descricao, qtd, exemplos = (linha.get(c, '') for c in campos)
        texto = (f"- O campo '{campo}' apresentou o seguinte erro: {descricao}. "
                 f'Ocorreu em {qtd} registro(s). Exemplos: {exemplos}.')
        _escrever(pdf, texto)
        pdf.ln(2)
    pdf.ln(4)
    _escrever(pdf, f"Finalizado em {datetime.today():%d/%m/%Y}, tabela {tabela}.", negrito=True)


def imprime(FATOR, df_IMPR, cd_EMP, tbl_avl, path, tipo_erro, st=None, IA=False):

    if not isinstance(df_IMPR, pd.DataFrame):
        raise TypeError('df_IMPR deve ser um pandas.DataFrame.')
    destino = Path(path) / 'RELATORIOS' / f'erros_{datetime.today():%Y%m%d}.pdf'
    destino.parent.mkdir(parents=True, exist_ok=True)
    pdf = _PDFValidador(cd_EMP)
    revisor = _criar_revisor(IA, st=st)
    resumidor = None
    barra = None
    try:
        abertura = ('Este relatório apresenta os resultados da validação estrutural dos arquivos enviados. '
                    'As inconsistências devem ser corrigidas ou justificadas antes da análise subsequente.')
        pdf.capa(_revisar(revisor, abertura, 'Se necessário, complemente em até três parágrafos.'))
        pdf.add_page()
        _escrever(pdf, 'Introdução', tamanho=14, negrito=True)
        _escrever(pdf, 'O validador verifica integridade e qualidade dos dados. As principais categorias incluem:')
        categorias = [
            'Dependência: validade de um campo condicionada a outro.',
            'Valores possíveis: valor fora do conjunto permitido.',
            'Tipo: incompatibilidade com o tipo esperado.',
            'Formato: informação fora do padrão exigido.',
            'Ausência: campo obrigatório não preenchido.',
            'Cruzamento interno: inconsistência entre campos do mesmo registro.',
        ]
        _escrever(pdf, _revisar(revisor, '\n'.join(f'{i}. {x}' for i, x in enumerate(categorias, 1)),
                              'Preserve os seis itens e a numeração.'))
        pdf.ln(5)
        _escrever(pdf, 'Corrija ou justifique as ocorrências e execute novamente a validação.')
        pdf.ln(5)
        if tbl_avl and len(df_IMPR) > 5000:
            _escrever(pdf, 'Em razão do limite de ocorrências, as tabelas avaliadas incluem:')
            for tabela in tbl_avl:
                _escrever(pdf, f'- {tabela}')
        _escrever(pdf, f'Indicador relativo à média setorial: {float(FATOR):.2f} vez(es).')
        if FATOR > 3:
            avaliacao = 'Indicador crítico: a empresa merece atenção especial.'
        elif FATOR > 1:
            avaliacao = 'Indicador acima da média: recomenda-se melhorar a qualidade dos dados.'
        else:
            avaliacao = 'Indicador dentro da faixa de referência; o objetivo continua sendo zerar os erros.'
        _escrever(pdf, avaliacao)
        grafico = Path(path) / 'IMAGENS' / 'grafico_erro.png'
        if grafico.is_file():
            pdf.ln(5)
            pdf.image(str(grafico), x=Align.C, w=145)
        else:
            LOG.warning('Gráfico não encontrado em %s; PDF gerado sem imagem.', grafico)

        if df_IMPR.empty:
            pdf.add_page()
            _escrever(pdf, 'Nenhuma inconsistência registrada no conjunto informado.', tamanho=12)
        else:
            obrigatorias = {'Nm_TAB', 'Campo', 'Descrição do Erro', 'Qtd', 'Exemplos (Amostra, linha do arquivo)'}
            faltantes = obrigatorias - set(df_IMPR.columns)
            if faltantes:
                raise ValueError(f'Colunas obrigatórias ausentes: {sorted(faltantes)}')
            tabelas = df_IMPR['Nm_TAB'].dropna().drop_duplicates().tolist()
            resumidor = _criar_resumidor(IA)
            if st is not None and tabelas:
                barra = st.progress(0, text='Iniciando relatório')
            for indice, tabela in enumerate(tabelas, 1):
                dados = df_IMPR.loc[df_IMPR['Nm_TAB'] == tabela]
                _detalhar_tabela(pdf, str(tabela), dados, resumidor)
                if barra is not None:
                    barra.progress(indice / len(tabelas), text=f'Tabela {tabela}: {indice}/{len(tabelas)}')
        pdf.output(str(destino))
        LOG.info('PDF gerado: %s', destino)
        return 'OK'
    finally:
        if barra is not None:
            barra.empty()
        _fechar(resumidor)
        _fechar(revisor)