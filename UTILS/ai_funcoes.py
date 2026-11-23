from ollama import Client
import pandas as pd, ast, gzip, pickle, os, numpy as np, requests, re
from datetime import datetime
from langchain_community.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import ollama, json, time
from langchain_community.llms import Ollama
from UTILS import monitor_completo  
import streamlit as st
import logging
from functools import lru_cache
from sklearn.neighbors import NearestNeighbors
from pathlib import Path
from typing import List, Optional

if 'LOGGER' not in st.session_state:
    st.session_state.LOGGER = logging.getLogger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_EMB_URL = f"{OLLAMA_BASE_URL}/api/embed"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"

@monitor_completo(st.session_state.LOGGER)
def ollama_disponivel(timeout: int = 3) -> bool:
    try:
        r = requests.get(OLLAMA_TAGS_URL, timeout=timeout)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False

@monitor_completo(st.session_state.LOGGER)    
def modelo_disponivel(model_name: str) -> bool:
    try:
        r = requests.get(OLLAMA_TAGS_URL, timeout=3)
        r.raise_for_status()
        modelos = [m["name"] for m in r.json().get("models", [])]
        return model_name in modelos
    except requests.exceptions.RequestException:
        return False

@monitor_completo(st.session_state.LOGGER)    
def get_embedding(texto: str, MODELO = 'nomic-embed-text') -> list | None:
    if not texto:
        return None

    try:
        resp = ollama.embeddings(
                                    model=MODELO,
                                    prompt=texto
                                )
        return resp.get("embedding")

    except Exception:
        return None

@monitor_completo(st.session_state.LOGGER)
def get_embeddings_batch(textos: list[str], modelo ="nomic-embed-text") -> List[Optional[List[float]]]:
    if not textos:
        return []


    resp = ollama.embed(
                                model=modelo,
                                input=textos
                            )
    return resp.get("embeddings", [])

@lru_cache(maxsize=100_000)
def get_embedding_cached(texto: str):
    return get_embedding(texto)

@monitor_completo(st.session_state.LOGGER)
def normaliza_descricao(series: pd.Series) -> pd.Series:
    return (
                series
                .fillna("")
                .str.lower()
                .str.replace(r"[^\w\s\-\/\.]", " ", regex=True)
                .str.replace(r"\s+", " ", regex=True)
                .str.strip()
            )

@monitor_completo(st.session_state.LOGGER)
def compara_materiais(df1: pd.DataFrame, 
                      df2: pd.DataFrame, 
                      col_df1: str = "DESC_CMP",
                      col_df2: str = "DESC_CMP",
                      top_k: int = 3,
                      st=None) -> pd.DataFrame:
    
    if col_df1 not in df1.columns or col_df2 not in df2.columns:
        return pd.DataFrame()
    
    avl = None
    df1[col_df1] = df1[col_df1].astype(str).fillna("ND")
    df2[col_df2] = df2[col_df2].astype(str).fillna("ND")
    df1[f"{col_df1}_norm"] = normaliza_descricao(df1[col_df1])
    df2[f"{col_df2}_norm"] = normaliza_descricao(df2[col_df2])

    desc_unicas = (
                    pd.concat([
                        df1[f"{col_df1}_norm"],
                        df2[f"{col_df2}_norm"]
                    ])
                    .dropna()
                    .astype(str)
                    .unique()
                )

    desc_unicas = [d for d in desc_unicas if d != ""]
    
    EMB_PATH = Path(st.session_state.tra_dir) / "BP_ANLS" / "emb_map_nomic.parquet"
    if EMB_PATH.exists():
        emb_map =  pd.read_parquet(EMB_PATH)
    else:
        emb_map =  pd.DataFrame(
                                    columns=["DESC_NORM", "EMB_DESC", "EMB_OK", "EMB_MODEL", "DT_EMB"]
                                )
    existentes = set(emb_map["DESC_NORM"].astype(str).tolist())
    novas_desc = [d for d in desc_unicas if d not in existentes]
    if len(novas_desc)>0:
        registros = []
        now = pd.Timestamp.now()
        tam_lote = 100
        avl = st.progress(0, "Gerando embeddings...")
        for i in range(0, len(novas_desc), tam_lote):
            avl.progress(min(int((i + tam_lote) / len(novas_desc) * 100), 100),f"Embeddings {i}/{len(novas_desc)}")
            lote = novas_desc[i:i + tam_lote]
            embs = get_embeddings_batch(lote)
            if len(embs) != len(lote):
                embs = (embs + [None] * len(lote))[:len(lote)]
            for desc, emb in zip(lote, embs):
                ok = isinstance(emb, list) and len(emb) == 768
                registros.append({
                    "DESC_NORM": desc,
                    "EMB_DESC": emb if ok else None,
                    "EMB_OK": bool(ok),
                    "EMB_MODEL": 'nomic-embed-text',
                    "DT_EMB": now,
                })
        novos_df = pd.DataFrame(registros)
        emb_map = pd.concat([emb_map, novos_df], ignore_index=True)
        emb_map.to_parquet(EMB_PATH, index=False)

    df1 = df1.merge(
                    emb_map,
                    left_on=f"{col_df1}_norm",
                    right_on="DESC_NORM",
                    how="left"
                   )

    df2 = df2.merge(
                    emb_map,
                    left_on=f"{col_df2}_norm",
                    right_on="DESC_NORM",
                    how="left"
                    )
    
    df1.drop(columns=["DESC_NORM"], inplace=True)
    df2.drop(columns=["DESC_NORM"], inplace=True)
    
    df1["EMB_OK"] = df1["EMB_OK"].fillna(False).astype(bool)
    df2["EMB_OK"] = df2["EMB_OK"].fillna(False).astype(bool)

    df1_ok = df1.loc[df1["EMB_OK"]].copy()
    df2_ok = df2.loc[df2["EMB_OK"]].copy()

    if df1_ok.empty or df2_ok.empty:
        df1["SCORE_SIM"] = np.nan
        df1["IDX_MATCH"] = np.nan
        df1["CLASSE_MATCH"] = "IMPROVAVEL"
        return df1

    X_ref = np.vstack(df2_ok["EMB_DESC"].values)
    X_qry = np.vstack(df1_ok["EMB_DESC"].values)

    nn = NearestNeighbors(
                            n_neighbors=top_k,
                            metric="cosine",
                            algorithm="brute"
                        )
    nn.fit(X_ref)
    distances, indices = nn.kneighbors(X_qry)
    best_idx = indices[:, 0]
    best_score = 1 - distances[:, 0]

    df1_ok["IDX_MATCH"] = df2_ok.iloc[best_idx].index.values
    df1_ok["SCORE_SIM"] = best_score

    df1_ok["CLASSE_MATCH"] = np.select(
                                            [
                                                df1_ok["SCORE_SIM"] >= 0.85,
                                                df1_ok["SCORE_SIM"] >= 0.70
                                            ],
                                            ["PROVAVEL", "NEBULOSO"],
                                            default="IMPROVAVEL"
                                        )
    df_result = df1.copy()

    df_result["IDX_MATCH"] = np.nan
    df_result["SCORE_SIM"] = np.nan
    df_result["CLASSE_MATCH"] = "IMPROVAVEL"

    df_result.loc[df1_ok.index, ["IDX_MATCH", "SCORE_SIM", "CLASSE_MATCH"]] = (
                    df1_ok[["IDX_MATCH", "SCORE_SIM", "CLASSE_MATCH"]]
                )
    if avl: avl.empty()
    return df_result

@monitor_completo(st.session_state.LOGGER)
def responder_cntr(contexto_texto, modelo = "qwen3:8b"):
    prompt = f"""
                Você é um analista técnico. Você deve fazer um resumo com 
                linguagem clara e objetiva com base no 
                conteúdo abaixo, um contrato de prestação de serviços (de investimento 
                e de manutenção) para a distribuidora. Cada
                afirmação deve ser baseada explicitamente no texto:

                {contexto_texto}

                Deve:
                - Se não houver dados, diga que não é possível dizer nada.
                - Colocar como título, destacado, o código do contrato ou as partes envolvidas
                - Deve ter no resumo o objeto do contrato a descrição do objeto, os valores, a forma de pagamento e atualização, no que for explicito.
                - Ser em formato markdown, revise para evitar erros, e deve rodar no streamlit markdown com unsafe_allow_html=True
                - Caso não exista resposta, diga que consulta foi inconclusiva
                - Linguagem técnica e explicitar parte do texto, texto integral entre aspas, se necessário, como referência para resposta
                - Não deve repetir a pergunta na resposta
                - Não deve ter títulos, seções ou afins
                - Não traduza acrônimos ou siglas
                - Ser útil para gestores ou técnicos que não lerão o documento inteiro
                """
    return ollama.chat(model=modelo, messages=[{"role": "user", "content": prompt}])["message"]["content"]

@monitor_completo(st.session_state.LOGGER)
def responder(contexto_texto, pergunta, modelo = "qwen3:8b"):
    prompt = f"""
                Você é um analista técnico. Você deve responder à pergunta: \n\n
                
                {pergunta}

                \n\n A resposta deve estar em linguagem clara e objetiva com base no conteúdo abaixo:

                {contexto_texto}

                Deve:
                - Ser em formato HTML, revise para evitar erros
                - Ter no máximo 2 parágrafos
                - Caso não exista resposta, diga que consulta foi inconclusiva
                - Linguagem técnica e explicitar parte do texto, se necessário, como referência para resposta
                - Não deve repetir a pergunta na resposta
                - Não deve ter títulos, seções ou afins
                - Não traduza acrônimos ou siglas
                - Ser útil para gestores ou técnicos que não lerão o documento inteiro
                """
    return ollama.chat(model=modelo, messages=[{"role": "user", "content": prompt}])["message"]["content"]

@monitor_completo(st.session_state.LOGGER)
def extrair_insights(documentos, modelo = "qwen3:8b"):
    llm = Ollama(model=modelo)
    texto = "\n".join([doc.page_content for doc in documentos])
    prompt = (
        "Você receberá um conjunto de resumos técnicos. Extraia ao menos 10 "
        "insights ou conclusões principais. Ressalte pontos críticos e de atenção."
        "Apresente os insights como uma lista numerada clara e objetiva, com foco técnico e estratégico. "
        "Evite repetir ideias semelhantes. Não escreva um resumo contínuo. Usi emojis para destacar o insight.\n\n"
        f"{texto}"
    )
    resposta = llm(prompt)
    return Document(page_content=resposta)

@monitor_completo(st.session_state.LOGGER)
def resumir_grupo(documentos, modelo = "qwen3:8b"):
    llm = Ollama(model=modelo)
    texto = "\n".join([doc.page_content for doc in documentos])
    prompt = (
        "Você receberá um conjunto de resumos técnicos.\n\n Ignore resumos em inglês "
        "ou com poucas palavras ou partes de assinatura ou de certificação digital. \n\n Sua "
        "tarefa é gerar um novo resumo mais enxuto, em Português, "
        "combinando as ideias e mantendo apenas os pontos mais importantes para análise "
         "estratégica, usando formatação markdown, evite títulos e quando usar empregar estilo h3:\n\n" + texto
    )
    resposta = llm(prompt)
    return Document(page_content=resposta)

@monitor_completo(st.session_state.LOGGER)
def ollama_esta_ativo(url='http://localhost:11434') -> bool:
    try:
        r = requests.get(f"{url}", timeout=2)
        return r.status_code == 200
    except requests.RequestException:
        return False

@monitor_completo(st.session_state.LOGGER)
def salva(cache: dict, path = None, nome = "nenhum", extensao = '.pkl.gz'):
    if path:
        with gzip.open(f"{path}{nome}{extensao}", 'wb') as f:
            pickle.dump(cache, f, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        raise UserWarning("Você deve fornecer o caminho!")

@monitor_completo(st.session_state.LOGGER)
def carrega(path= None, nome = "nenhum", extensao = '.pkl.gz'):
    if path:
        if os.path.exists(f"{path}{nome}{extensao}"):
            with gzip.open(f"{path}{nome}{extensao}", 'rb') as f:
                return pickle.load(f)
        return {}
    else:
        raise UserWarning("Você deve fornecer o caminho!")

@monitor_completo(st.session_state.LOGGER)
def literal_seg(node, default="Desconhecido"):
    try:
        return ast.literal_eval(node)
    except Exception:
        return ast.dump(node)

@monitor_completo(st.session_state.LOGGER)    
def contexto(node):
    parent = getattr(node, "parent", None)
    while parent:
        if isinstance(parent, ast.With):
            if "sidebar" in ast.dump(parent):
                return "sidebar"
        parent = getattr(parent, "parent", None)
    return "main"

@monitor_completo(st.session_state.LOGGER)
def analise_estrutura(tree):
    estrutura = {
                    "paginas": [],
                    "navegacao": [],
                    "markdown": [],
                    "acoes": [],
                    "opcoes": [],
                    "figuras": [],
                    "layout": [],
                    "estados": [],
                    "forms": []
                }

    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

    for node in ast.walk(tree):

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            atr = node.func.attr

            if atr == "Page":
                nm_arq = literal_seg(node.args[0]) if node.args else "Desconhecido"
                nm_pag = "Sem Título"

                for kw in node.keywords:
                    if kw.arg == "title":
                        nm_pag = literal_seg(kw.value)

                estrutura["paginas"].append({
                                                "Tipo_no": "pagina",
                                                "LIN_INI": node.lineno,
                                                "LIN_FIM": getattr(node, "end_lineno", node.lineno),
                                                "Nm_PAG": nm_pag,
                                                "Nm_ARQpy": nm_arq
                                            })

            elif atr in ["markdown", "title", "info", "error", "warning", "success", "head", "subhead",
                         "write", "text", "caption", "code", "latex", "html", "badge", "write_stream",
                        "dataframe", "html"] and prefixo == "st":
                bloco = {
                            "Tipo_no": atr,
                            "LIN_INI": node.lineno,
                            "LIN_FIM": getattr(node, "end_lineno", node.lineno),
                            "Texto": literal_seg(node.args[0]) if node.args else "",
                            "Contexto": contexto(node)
                        }
                if atr in ["write", "text", "markdown", "title",
                           "info", "error", "warning", "success",
                           "head", "subhead", "caption", "html"]:
                    bloco["Texto"] = literal_seg(node.args[0]) if node.args else ""

                elif atr == "code":
                    bloco["Texto"] = literal_seg(node.args[0]) if node.args else ""
                    bloco["Linguagem"] = literal_seg(node.args[1]) if len(node.args) > 1 else "texto"

                elif atr == "latex":
                    bloco["Texto"] = literal_seg(node.args[0]) if node.args else ""
                    bloco["Formato"] = "latex"

                elif atr == "badge":
                    bloco["Label"] = literal_seg(node.args[0]) if node.args else ""
                    for kw in node.keywords:
                        if kw.arg == "severity":
                            bloco["Severidade"] = literal_seg(kw.value)

                elif atr == "dataframe":
                    bloco["Tabela"] = True

                elif atr == "write_stream":
                    bloco["Stream"] = True

                estrutura["markdown"].append(bloco)

            elif atr in ["plotly_chart", "pyplot", "image"]:
                estrutura["figuras"].append({
                                                "Tipo_no": atr,
                                                "LIN_INI": node.lineno,
                                                "LIN_FIM": getattr(node, "end_lineno", node.lineno),
                                                "Contexto": contexto(node)
                                            })

            elif atr in ["columns", "container", "expander"]:
                estrutura["layout"].append({
                                                "Tipo_no": atr,
                                                "LIN_INI": node.lineno,
                                                "LIN_FIM": getattr(node, "end_lineno", node.lineno)
                                            })

        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Attribute):
                func = node.value.func
                prefixo = func.value.id if isinstance(func.value, ast.Name) else ""

                if func.attr == "navigation" and prefixo == "st":
                    estrutura["navegacao"].append({
                                                        "Tipo_no": "navegacao",
                                                        "LIN_INI": node.lineno,
                                                        "LIN_FIM": getattr(node, "end_lineno", node.lineno),
                                                        "Nm_VAR": node.targets[0].id
                                                    })

                if func.attr == "button" and prefixo == "st":
                    estrutura["acoes"].append({
                                                "Tipo_no": "acao",
                                                "LIN_INI": node.lineno,
                                                "LIN_FIM": getattr(node, "end_lineno", node.lineno),
                                                "Nm_VAR": node.targets[0].id,
                                                "Label": literal_seg(node.value.args[0]) if node.value.args else "",
                                                "Contexto": contexto(node)
                                            })

                if func.attr in ["checkbox", "text_input", "selectbox", "date_input"] and prefixo == "st":
                    estrutura["opcoes"].append({
                                                "Tipo_no": func.attr,
                                                "LIN_INI": node.lineno,
                                                "LIN_FIM": getattr(node, "end_lineno", node.lineno),
                                                "Nm_VAR": node.targets[0].id,
                                                "Label": literal_seg(node.value.args[0]) if node.value.args else "",
                                                "Contexto": contexto(node)
                                            })

        if isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Attribute):
                if ast.dump(node.value) == "Attribute(value=Name(id='st', ctx=Load()), attr='session_state', ctx=Load())":
                    estrutura["estados"].append({
                                                    "Tipo_no": "session_state",
                                                    "LIN_INI": node.lineno,
                                                    "Chave": literal_seg(node.slice)
                                                })

    return estrutura

@monitor_completo(st.session_state.LOGGER)
def respostas_help(perg = "", ctx = None, st = None, modelo = "qwen3:8b"):
    texto = "Contexto não detectado"
    if ctx:
        if ctx[-3:].lower() != ".py":
            texto = f"Contexto inválido: {ctx}"
            return texto
        dado = carrega(path='_rag_index/', nome = ctx[:-3])
        if dado == {}:
            with open(ctx, "r", encoding='utf-8') as f:
                arq = f.read()
            dado = analise_estrutura(ast.parse(arq))
            salva(dado, path='_rag_index/', nome = ctx[:-3])
        PROMPT_SISTEMA = """
                            Você é um assistente técnico especializado em análise estrutural de aplicações Streamlit.

                                Você recebeu uma estrutura JSON que representa, de forma estática, os componentes de uma página Streamlit, obtida por análise de código (AST).
                                Essa estrutura é a ÚNICA fonte de informação permitida para responder às perguntas.

                                REGRAS ABSOLUTAS:
                                1. Você DEVE responder apenas com base nas informações presentes na estrutura ou nos conceitos fornecidos.
                                2. Você NÃO pode inferir comportamentos, dados, regras de negócio ou fluxos que não estejam explicitamente representados.
                                3. Você NÃO pode usar conhecimento externo sobre Streamlit além do que está diretamente refletido na estrutura.
                                4. Se a pergunta não puder ser respondida exclusivamente com base nessa estrutura, responda exatamente:
                                "Não é possível responder a essa pergunta com base no contexto disponível."
                                5. Não faça suposições. Não complete lacunas. Não extrapole.

                                COMO INTERPRETAR A ESTRUTURA:
                                - "paginas": define páginas declaradas via st.Page (nome, arquivo e título).
                                - "navegacao": indica uso de navegação (ex.: st.navigation).
                                - "markdown": textos exibidos ao usuário (títulos, mensagens, avisos).
                                - "acoes": ações do usuário (ex.: botões).
                                - "opcoes": configurações ou entradas do usuário (checkbox, inputs).
                                - "figuras": elementos visuais (gráficos, imagens).
                                - "layout": organização visual (colunas, containers, expanders).
                                - "estados": uso de st.session_state.
                                - "forms": formulários (se existirem).

                            COMPORTAMENTO DE RESPOSTA:
                            - Seja direto e técnico.
                            - Não explique conceitos genéricos de Streamlit.
                            - Não utilize exemplos externos.

                            FORMATO DAS RESPOSTAS:
                            - Use linguagem clara e objetiva.
                            - Prefira listas quando houver múltiplos itens.
                            - Não cite código Python a menos que ele esteja explicitamente descrito na estrutura.
                         """

        client = Client()
        
        txt = ""
        for n in dado["markdown"]:
            txt += str(n.get("Texto", "")) + "\n"
        
        estrutura = {k : v for k,v in dado.items() if k != "markdown"}
        prompt = f"""
                 ESTRUTURA DA PÁGINA:
                {estrutura}

                CONCEITOS DA PÁGINA:
                {txt}

                PERGUNTA:
                {perg}
                 """
        response = client.chat(
                                model=modelo,
                                messages=[{'role': 'system', 'content': PROMPT_SISTEMA},
                                          {'role': 'user', 'content': prompt}]
                            )
        texto = f"{response['message']['content']}"
        #if texto.rfind("</think>"):
            #texto = texto[texto.rfind("</think>") + 7:]
        
    return texto

@monitor_completo(st.session_state.LOGGER)
def mensagens(prompt):

    client = Client()
    response = client.chat(
        model='qwen3:8b',
        messages=[{'role': 'system', 'content': 'Você é um assistente útil de contabilidade que responde perguntas de forma técnica e profissional. Uma frase curta em português.'},
                    {'role': 'user', 'content': prompt}]
    )
    texto = f"{response['message']['content']}"
    if texto.rfind("</think>"):
        texto = texto[texto.rfind("</think>") + 8:]
    return texto

@monitor_completo(st.session_state.LOGGER)
def boavinda(quem,periodo):
    # Prompt para análise
    prompt = f"""
    ###Instrução###
    Crie uma mensagem para {quem}, em português, desejando {periodo}, em único parágrafo com poucas palavras, 
    evitando símbolos e emojis, com formatação leve e no máximo 20 palavras.
    """

    # Chamada ao Ollama
    client = Client()
    response = client.chat(
        model='qwen3:8b',
        messages=[{'role': 'system', 'content': 'Você é um assistente útil que responde com bom humor as perguntas.'},
                    {'role': 'user', 'content': prompt}]
    )


    return f"{response['message']['content']}"

class ResumoValidador:
    """
    Classe para gerar e revisar resumos técnicos de DataFrames da etapa de validação.
    Executa duas passagens no LLM (geração e revisão) usando o modelo Qwen local via Ollama.
    """

    def __init__(self, model="qwen3:8b", max_linhas=10):
        self.client = Client()
        self.model = model
        self.max_linhas = max_linhas

    def close(self):
        """Marca o cliente como fechado e limpa a sessão."""
        self.client = None
        self._is_closed = True

    def __del__(self):
        """Fecha automaticamente se o objeto for destruído."""
        self.close()

    def _df_para_texto(self, df: pd.DataFrame, max_linhas=10) -> str:
        """
        Converte DataFrame em texto legível para o LLM (exibe apenas amostra).
        """
        if df.empty:
            return "DataFrame vazio, sem registros."
        texto = df.head(max_linhas).to_csv(index=False, sep="|")
        return f"Tabela de erros (primeiras {max_linhas} linhas):\n{texto}"

    def _prompt_resumo(self, texto_df: str) -> str:
        """
        Prompt base para o primeiro estágio (resumo técnico).
        """
        return f"""
        Você é um analista técnico responsável por gerar um resumo descritivo
        de um conjunto de erros detectados por um validador de dados.

        Tarefa:
        Resuma o conteúdo do DataFrame fornecido em um único parágrafo contínuo.
        Use linguagem técnica, formal e objetiva. Caracteres devem ser Unicode.
        Não utilize emojis, formatação Markdown, listas ou caracteres especiais.

        Inclua obrigatoriamente:
        1. Categorias de erro — classifique as falhas encontradas
           (ex.: inconsistências de dados, formatos inválidos, violações de regras de negócio).
        2. Frequência dos erros — destaque os tipos mais recorrentes e suas contagens relativas.

        DataFrame:
        {texto_df}
        """

    def _prompt_revisor(self, texto_inicial: str) -> str:
        """
        Prompt do revisor técnico — garante clareza e estilo unificado.
        """
        return f"""
        Você é um revisor técnico especializado em textos de análise de dados.
        Reescreva o texto abaixo mantendo estilo técnico, clareza e coesão.
        Regras:
        - Use linguagem formal, objetiva e neutra;
        - Evite repetições e redundâncias;
        - Deve usar somente caracteres Unicode;
        - Evite trazer novas informações, use apenas os dados fornecidos;
        - No máximo dois parágrafos;
        - No segundo parágrafo finalize indicando que o arquivo pode ser enviado sem correções, mas que a empresa deve sustentar os dados;
        - Não descreva acronimos, considero como conhecidos;
        - No fim de cada parágrafo, use o marcador de nova linha "\n";
        - Não utilize formatação Markdown nem emojis.

        Texto a revisar:
        {texto_inicial}
        """

    def _gerar_resposta(self, prompt: str) -> str:
        """
        Chama o modelo Qwen e retorna a resposta textual.
        """
        resposta = self.client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return resposta["message"]["content"].strip()

    def gerar_resumo(self, df: pd.DataFrame, max_linhas=10) -> str:
        """
        Executa as duas etapas: resumo inicial + revisão.
        """
        texto_df = self._df_para_texto(df,max_linhas=max_linhas)
        prompt1 = self._prompt_resumo(texto_df)
        resumo_inicial = self._gerar_resposta(prompt1)

        prompt2 = self._prompt_revisor(resumo_inicial)
        resumo_final = self._gerar_resposta(prompt2)

        return resumo_final

class RevisorLLM:
    """
    Classe de revisão textual usando modelo Qwen local via Ollama.
    Mantém o cliente ativo para múltiplas chamadas.
    """
    def __init__(self, modelo: str = "qwen3:8b", temperatura: float = 0.3):
        self.client = Client()
        self.modelo = modelo
        self.temperatura = temperatura
        self.instrucao_base = (
            "Você é um revisor técnico e deve usar português. Corrija o texto com foco em gramática, "
            "coesão e clareza, adaptando para linguagem técnica e formal. "
            "Inclua elementos faltantes para deixar o texto completo, "
            "mas sem alterar o sentido. "
            "Caso seja fornecida tabela, seja analítico."
            "Deve somente usar fonte Unicode."
            "Evite conclusões sem consistência com os dados, lembre-se que esta falando de resultados de um validador pydantic."
            "Se houver acrônimos, matenha-os, não os explique."
            "Coloque ao final de cada parágrafo o símbolo de novo parágrafo: '\n.'"
        )
        self.instrucao_base_cx = (
            "Você é um revisor técnico e deve usar português. Corrija o texto com foco em análise do fluxo de caixa, "
            "coesão e clareza, adaptando para linguagem técnica e formal. "
            "Inclua elementos faltantes para deixar o texto completo, "
            "mas sem alterar o sentido. "
            "Caso seja fornecida tabela, seja analítico."
            "Deve somente usar fonte Unicode."
            "Evite conclusões sem consistência com os dados."
            "Se houver acrônimos, matenha-os, não os explique."
            "Coloque ao final de cada parágrafo o símbolo de novo parágrafo: '\n.'"
        )
    
    def close(self):
        """Marca o cliente como fechado e limpa a sessão."""
        self.client = None
        self._is_closed = True

    def __del__(self):
        """Fecha automaticamente se o objeto for destruído."""
        self.close()

    def revisar(self, texto: str, instrucao_extra: str = "", tipo = None) -> str:
        """
        Revisa um texto com base na instrução padrão e opcionalmente em uma instrução extra.

        Args:
            texto (str): Texto a ser revisado.
            instrucao_extra (str): Instrução adicional (opcional).

        Returns:
            str: Texto revisado.
        """
        if tipo == None:
            mensagens = [
                {"role": "system", "content": f"{self.instrucao_base} {instrucao_extra}".strip()},
                {"role": "user", "content": texto},
            ]
        else:
            mensagens = [
                {"role": "system", "content": f"{self.instrucao_base_cx} {instrucao_extra}".strip()},
                {"role": "user", "content": texto},
            ]

        resposta = self.client.chat(model=self.modelo, messages=mensagens)
        conteudo = resposta.get("message", {}).get("content", "").strip()

        # Remove bloco de raciocínio (<think>) se houver
        if "</think>" in conteudo:
            conteudo = conteudo.split("</think>", 1)[-1].strip()

        return conteudo

    def revisar_lote(self, lista_textos, instrucao_extra: str = "", barra: bool = True):
        """
        Revisa vários textos em sequência.

        Args:
            lista_textos (list[str]): Lista de textos a revisar.
            instrucao_extra (str): Instrução adicional.
            barra (bool): Exibe barra de progresso se True.

        Returns:
            list[str]: Lista de textos revisados.
        """
        resultados = []
        if barra:
            from tqdm import tqdm
            iterador = tqdm(lista_textos, desc="Revisando textos", ncols=80)
        else:
            iterador = lista_textos

        for texto in iterador:
            resultados.append(self.revisar(texto, instrucao_extra))

        return resultados

@monitor_completo(st.session_state.LOGGER)
def resumo(texto, modelo = "qwen3:8b"):
        PROMPT_SYSTEM = """Você é um assistente especializado em resumir textos em português claro e objetivo.
                            Produza um único parágrafo contínuo, sem listas ou quebras de linha.
                            Não utilize expressões em inglês e não traduza siglas ou acrônimos.
                            Exclua informações de segurança, como assinaturas eletrônicas, certificados ou dados similares.
                            O resumo deve preservar o sentido essencial do texto, com linguagem formal e acessível.
                            Se parecer haver quebra, devido ao chunk, indique no resumo."""
        response = ollama.chat(
                                model = modelo,
                                messages=[{'role': 'system', 'content': PROMPT_SYSTEM},
                                          {'role': 'user', 'content': f'Resuma: {texto}'}]
                                )
        texto = response['message']['content']
        
        return texto[texto.rfind("</think>") + 8:]

@monitor_completo(st.session_state.LOGGER)
def indexar_pdf(caminho_pdf, st=None, salvar_em="faiss_paginas"):
    embedding_model = HuggingFaceEmbeddings(
                                                model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
                                            )

    arq = os.path.basename(caminho_pdf)
    loader = PyPDFLoader(caminho_pdf)
    docs = loader.load()

    base = []
    docs_para_faiss = []
    total = len(docs)
    av = st.progress(0, "Iniciando leitura")
    for i, doc in enumerate(docs):
        av.progress(int(i/total * 100), f"""Lendo página {doc.metadata["page"]}/{total}.""")
        resumo1 = resumo(doc.page_content, modelo = "deepseek-r1:1.5b")
        registro = {
                        "pagina": doc.metadata["page"],
                        "resumo": resumo1,
                        "conteudo": doc.page_content,
                        "fonte": arq
                    }
        base.append(registro)
        docs_para_faiss.append(Document(page_content=resumo1, metadata={"pagina": doc.metadata["page"], "arquivo" : arq}))

    if os.path.exists(f"{salvar_em}/index.faiss"):
        index = FAISS.load_local(salvar_em, embedding_model, allow_dangerous_deserialization=True)
        index.add_documents(docs_para_faiss)
    else:
        index = FAISS.from_documents(docs_para_faiss, embedding_model)

    index.save_local(salvar_em)
    arquivo = f"{salvar_em}/base_pagina_completa.json"
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            dados_existentes = json.load(f)
    except FileNotFoundError:
        dados_existentes = []
    dados_existentes += base

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados_existentes, f, ensure_ascii=False, indent=2)

@monitor_completo(st.session_state.LOGGER)
def avaliar_frase(i, frase, vectorstore = None, id_to_label = None):
    if vectorstore == None:
        return i, "erro", 0
    try:
        resultados = vectorstore.similarity_search_with_score(frase, 1)
        vizinhos = []
        scores = []
        
        for doc, score in resultados:
            idx = str(doc.metadata["index"])
            try:
                if idx in id_to_label:
                    vizinhos.append(id_to_label[idx])
                    scores.append(score)
            except:
                pass
        
        if vizinhos:
            classe_predita = max(set(vizinhos), key=vizinhos.count)
        else:
            classe_predita = "desconhecido"
        
        classe_predita = classe_predita[0] if isinstance(classe_predita, (list, tuple, np.ndarray)) else classe_predita
        score = np.mean(scores) if isinstance(scores, (list, tuple, np.ndarray)) else scores

        if (classe_predita is None) or (classe_predita == ""):
            classe_predita = "desconhecido"
        return i, classe_predita.replace("C:", ""), score
    except:
        return i, "erro", 0