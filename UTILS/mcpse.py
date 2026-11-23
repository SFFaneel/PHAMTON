from __future__ import annotations
import streamlit as st
from pathlib import Path
from streamlit.components.v1 import html

import base64
import json
import mimetypes
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

PAGINAS = ('inicio.html', 'DADOS_FUNCOES.html', 'PIPELINE_PRINCIPAL.html')

def _recurso(uri: str, pasta: Path) -> str:
    if not uri or uri.startswith(('#', '//', 'data:', 'blob:', 'mailto:', 'javascript:')):
        return uri
    if urlsplit(uri).scheme:
        return uri
    partes = urlsplit(uri)
    caminho = unquote(partes.path).replace('\\', '/')
    arquivo = (pasta / caminho).resolve()
    raiz = pasta.resolve()
    if not arquivo.is_relative_to(raiz) or not arquivo.is_file():
        return uri
    mime = mimetypes.guess_type(arquivo.name)[0] or 'application/octet-stream'
    dados = base64.b64encode(arquivo.read_bytes()).decode('ascii')
    return f'data:{mime};base64,{dados}'


def _css_recursos(css: str, pasta: Path) -> str:
    def trocar(match):
        valor = match.group(2).strip()
        return f'url({match.group(1)}{_recurso(valor, pasta)}{match.group(3)})'
    return re.sub(r'url\(\s*([\'\"]?)(.*?)([\'\"]?)\s*\)', trocar, css, flags=re.I)


def _imagens(pasta: Path) -> dict[str, str]:
    extensoes = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp'}
    return {f.relative_to(pasta).as_posix(): _recurso(f.relative_to(pasta).as_posix(), pasta)
            for f in pasta.rglob('*') if f.is_file() and f.suffix.lower() in extensoes}


def _corrigir_imagens(conteudo: str, mapa: dict[str, str]) -> str:
    for caminho, uri in sorted(mapa.items(), key=lambda x: -len(x[0])):
        conteudo = conteudo.replace(caminho, uri)
        conteudo = conteudo.replace(caminho.replace('/', '\\/'), uri)

    dados = json.dumps(mapa, ensure_ascii=False).replace('<', '\\u003c')
    script = r"""<script>
        (() => {
        const mapa = __MAPA__;
        const nomes = {};
        for (const [caminho, uri] of Object.entries(mapa)) {
            const nome = caminho.split('/').pop().toLowerCase();
            if (!(nome in nomes)) nomes[nome] = uri;
            else nomes[nome] = null;
        }
        function resolver(valor) {
            if (!valor || /^(data:|blob:|https?:|#)/i.test(valor)) return null;
            let caminho = valor.split(/[?#]/)[0].replace(/\\/g, '/');
            try { caminho = decodeURIComponent(caminho); } catch (_) {}
            const partes = [];
            for (const parte of caminho.split('/')) {
            if (parte === '..') partes.pop();
            else if (parte && parte !== '.') partes.push(parte);
            }
            caminho = partes.join('/');
            return mapa[caminho] || nomes[partes[partes.length - 1]?.toLowerCase()] || null;
        }
        function corrigir(raiz) {
            const lista = [];
            if (raiz.nodeType === 1 && raiz.matches?.('img,source')) lista.push(raiz);
            raiz.querySelectorAll?.('img,source').forEach(el => lista.push(el));
            for (const el of lista) {
            const src = el.getAttribute('src');
            const novo = resolver(src);
            if (novo) el.setAttribute('src', novo);
            }
        }
        function iniciar() {
            corrigir(document);
            new MutationObserver(mudancas => {
            for (const m of mudancas) {
                if (m.type === 'attributes') corrigir(m.target);
                else for (const n of m.addedNodes) corrigir(n);
            }
            }).observe(document.documentElement, {subtree:true, childList:true, attributes:true, attributeFilter:['src']});
        }
        if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
        else iniciar();
        })();
        </script>""".replace('__MAPA__', dados)
    return re.sub(r'</head\s*>', lambda m: script + '\n' + m.group(0), conteudo, count=1, flags=re.I)

def _montar_pagina(arquivo: Path, css_global: str, pasta: Path, mapa: dict[str, str]) -> str:
    conteudo = arquivo.read_text(encoding='utf-8')
    def css_link(match):
        tag = match.group(0)
        achou = re.search(r'\bhref\s*=\s*[\'\"]([^\'\"]+)[\'\"]', tag, re.I)
        if not achou:
            return tag
        caminho = achou.group(1)
        if caminho == 'style.css':
            return '<style>' + css_global + '</style>'
        local = (arquivo.parent / caminho).resolve()
        if local.is_relative_to(pasta.resolve()) and local.is_file() and local.suffix.lower() == '.css':
            return '<style>' + _css_recursos(local.read_text(encoding='utf-8'), local.parent) + '</style>'
        return tag

    conteudo = re.sub(r'<link\b[^>]*\brel\s*=\s*[\'\"]stylesheet[\'\"][^>]*>', css_link, conteudo, flags=re.I)

    if '<style>' + css_global + '</style>' not in conteudo:
        conteudo = re.sub(r'</head\s*>', lambda m: '<style>' + css_global + '</style>\n' + m.group(0), conteudo, count=1, flags=re.I)

    def atributos(match):
        chave, aspas, valor = match.group(1), match.group(2), match.group(3)
        if chave.lower() == 'srcset':
            itens = [x.strip().split(' ', 1) for x in valor.split(',')]
            valor = ', '.join(_recurso(x[0], pasta) + (' ' + x[1] if len(x) > 1 else '') for x in itens)
        else:
            valor = _recurso(valor, pasta)
        return f'{chave}={aspas}{valor}{aspas}'
    conteudo = re.sub(r'\b(src|poster|srcset)\s*=\s*([\'\"])(.*?)\2', atributos, conteudo, flags=re.I | re.S)

    def scripts(match):
        tag = match.group(1)
        achou = re.search(r'\bsrc\s*=\s*[\'\"]([^\'\"]+)[\'\"]', tag, re.I)
        if not achou:
            return match.group(0)
        local = (pasta / achou.group(1)).resolve()
        if not local.is_relative_to(pasta.resolve()) or not local.is_file() or local.suffix.lower() != '.js':
            return match.group(0)
        codigo = local.read_text(encoding='utf-8').replace('</script', '<\\/script')
        tag = re.sub(r'\s+src\s*=\s*[\'\"][^\'\"]+[\'\"]', '', tag, flags=re.I)
        return f'<script{tag}>{codigo}</script>'
    conteudo = re.sub(r'<script([^>]*)>\s*</script>', scripts, conteudo, flags=re.I | re.S)
    return _corrigir_imagens(conteudo, mapa)

def construir_documentacao(pasta_html: str | Path = 'DOCUMENTACAO/HTML') -> str:
    pasta = Path(pasta_html).resolve()
    css = _css_recursos((pasta / 'style.css').read_text(encoding='utf-8'), pasta)
    portal = (pasta / 'index.html').read_text(encoding='utf-8')
    mapa = _imagens(pasta)
    paginas = {nome: _montar_pagina(pasta / nome, css, pasta, mapa) for nome in PAGINAS}

    portal, quantidade = re.subn(
        r'<link\b[^>]*\bhref\s*=\s*[\'\"]style\.css[\'\"][^>]*>',
        lambda _: '<style>\n' + css + '\n</style>', portal, count=1, flags=re.I
    )
    if quantidade != 1:
        raise ValueError('Não foi encontrada a referência a style.css no index.html')

    dados = json.dumps(paginas, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    portal = portal.replace('const DOCUMENTOS = [', 'const PAGINAS_INCORPORADAS = ' + dados + ';\n    const DOCUMENTOS = [', 1)
    original = "if (frame.getAttribute('src') !== documento.arquivo) frame.src = documento.arquivo;"
    novo = "if (frame.dataset.pagina !== documento.arquivo) { frame.srcdoc = PAGINAS_INCORPORADAS[documento.arquivo]; frame.dataset.pagina = documento.arquivo; }"
    if original not in portal:
        raise ValueError('O index.html não contém a navegação esperada (frame.src).')
    portal = portal.replace(original, novo, 1)
    portal = portal.replace('abrir.href = documento.arquivo;', '''if (abrir.dataset.blobUrl) URL.revokeObjectURL(abrir.dataset.blobUrl);
      abrir.dataset.blobUrl = URL.createObjectURL(new Blob([PAGINAS_INCORPORADAS[documento.arquivo]], {type: 'text/html;charset=utf-8'}));
      abrir.href = abrir.dataset.blobUrl;''', 1)
    return portal


def exibir_documentacao(pasta_html: str | Path = 'DOCUMENTACAO/HTML', altura: int = 850) -> None:
    import streamlit.components.v1 as components
    components.html(construir_documentacao(pasta_html), height=altura, scrolling=True)

def visualizar_docs(st=None):
    st.info("Visite regularmente o sitio da Aneel para versão mais atualizada.", icon="🚨")
    tab1, tab4, tab2, tab3, tab5, tab6 = st.tabs(["MCPSE", "PRORET 2.3", "MCSE", "ROCT", "MDFEF", "PHAMTON'S FANG"])

    with tab1:
        with open("html//MCPSE.css", encoding="utf-8", mode="r") as css_file:
            css_arq = css_file.read()
        with open("html//MCPSE.html", encoding="utf-8", mode="r") as html_file:
            html_arq = html_file.read()

        full_html = f"<style>{css_arq}</style>{html_arq}"

        with st.container(border=True):
            html(full_html, height=800, scrolling=True)

    with tab4:
        with open("html//MCPSE.css", encoding="utf-8", mode="r") as css_file:
            css_arq2 = css_file.read()
        with open("html//PRORET_2_3.html", encoding="utf-8", mode="r") as html_file:
            html_arq2 = html_file.read()

        full_html2 = f"<style>{css_arq2}</style>{html_arq2}"

        with st.container(border=True):
            html(full_html2, height=800, scrolling=True)
    with tab2:
        with open("html//MCPSE.css", encoding="utf-8", mode="r") as css_file:
            css_arq1 = css_file.read()
        with open("html//MCSE.html", encoding="utf-8", mode="r") as html_file:
            html_arq1 = html_file.read()

        full_html1 = f"<style>{css_arq1}</style>{html_arq1}"

        with st.container(border=True):
            html(full_html1, height=800, scrolling=True)
    with tab3:
        try:
            with open("html//MCPSE.css", encoding="utf-8", mode="r") as css_file:
                        css_arq1 = css_file.read()
            with open("html//ROCTax.html", encoding="utf-8", mode="r") as html_file:
                html_arq1 = html_file.read()

            full_html1 = f"<style>{css_arq1}</style>{html_arq1}"

            with st.container(border=True):
                html(full_html1, height=800, scrolling=True)
        except:
            st.info("Em desenvovlimento")
    with tab5:
        caminho = Path(r"html\Manual_Dados_SFF_Rev1.3.pdf")
        if caminho.is_file():
            st.pdf(caminho.read_bytes(), height=600)
        else:
            st.error(f"Arquivo não encontrado: {caminho}")
    with tab6:
        try:
             exibir_documentacao(pasta_html="DOCUMENTACAO/HTML",altura=850)

        except Exception as erro:
            st.error(f"Erro ao carregar a documentação: {erro}")