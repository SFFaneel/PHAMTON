import streamlit as st
from UTILS import (
                    cria_DBdbf,
                    bsc_dados_reg
                   )

from MANIFESTO import (
                        visual_manifesto, 
                        criar_manifesto,
                        execucao_trilha,
                        rastrear_funcao,
                        registrar_evento,
                        registrar_metrica,
                        registrar_artefato,
                        inicializa_database,
                        inicializa_detalhes,
                        inicializar_rastreamento,
                      )
from pathlib import Path
import geopandas as gpd
import fiona
import dbf
import numpy as np
import pandas as pd


imagem_fundo = "imagens/bull_bck.png"

def dataframe_to_dbf(df: pd.DataFrame, arquivo):
    df = df.copy()
    for c in df.select_dtypes(include=["datetimetz"]).columns:
        df[c] = df[c].dt.tz_localize(None)

    campos = []

    for col in df.columns:
        serie = df[col]
        if pd.api.types.is_integer_dtype(serie):
            campos.append(f"{col} N(18,0)")
        elif pd.api.types.is_float_dtype(serie):
            campos.append(f"{col} N(18,6)")
        elif pd.api.types.is_datetime64_any_dtype(serie):
            campos.append(f"{col} D")
            df[col] = serie.dt.date
        elif pd.api.types.is_bool_dtype(serie):
            campos.append(f"{col} L")
        else:
            texto = serie.fillna("").astype(str)
            tamanho = texto.str.len().max()
            if pd.isna(tamanho):
                tamanho = 1
            tamanho = int(max(1, min(254, tamanho)))
            campos.append(f"{col} C({tamanho})")
            df[col] = (
                            texto
                            .str[:254]
                            .str.encode("cp1252", errors="replace")
                            .str.decode("cp1252")
                        )

    tabela = dbf.Table(
                            str(arquivo),
                            "; ".join(campos),
                            codepage="cp1252"
                        )

    tabela.open(mode=dbf.READ_WRITE)

    for _, linha in df.iterrows():

        registro = []

        for valor in linha:

            if pd.isna(valor):
                registro.append(None)
            elif isinstance(valor, np.generic):
                registro.append(valor.item())
            else:
                registro.append(valor)

        tabela.append(tuple(registro))

    tabela.close()

def bsc_BDGD(dir_ARQ1 = None, dir_ARQ2 = None, CNT = None, FLG_CNT = True, empresa = None, ano = None, database = None):
    with execucao_trilha(
                        db_path=database, script_nome="Importação BDGD",
                        parametros={"empresa": empresa, "ano": ano, "BDGD": CNT},
                        ) as execucao_id:
    
        registrar_evento(database, execucao_id, "IMPORTACAO_INICIADA",
                             mensagem=f"Iniciando importação BDGD {CNT}")
        dbf_arq = cria_DBdbf(dir_ARQ1, dir_ARQ2, CNT, FLG_CNT, empresa, ano)

        registrar_artefato(database, execucao_id, str(dir_ARQ1), "ENTRADA")
        registrar_evento(database, execucao_id, "IMPORTACAO_FINALIZADA",
                        mensagem=f"Finalizado importação BDGD {CNT}")

    return dbf_arq

def imp_BDGD():
    if not 'tra_dir' in st.session_state:
        st.html("""
                    <p>Você deve configurar o diretório de trabalho na aba <i>Criar Pasta de Trabalho</i>, barra lateral.</p>
                """)
        return
    col1 = st.columns([1,5,1], gap='small')
    with col1[1]:

        local = st.session_state.tra_dir
        empresa = st.session_state.nm_empr
        ano = st.session_state.dt_fim.year
        css = bsc_dados_reg("estilo_001", tipo="Estilo_CSS")
        st.html(f"<style>{css}</style>")

        caminho_manifesto = Path(local) / "MANIFESTO" / "TRILHA_EXEC" / "execucoes.db"
        caminho_manifesto.parent.mkdir(parents=True, exist_ok=True)
        inicializa_database(str(caminho_manifesto))
        inicializa_detalhes(str(caminho_manifesto))
        inicializar_rastreamento(str(caminho_manifesto))
        database = str(caminho_manifesto)

        st.html("""<h1>Importação dos arquivos da BDGD</h1><br><br>
            <p   style="text-align: justify;text-indent: 40px">Nesta etapa do processo, realiza-se o carregamento dos arquivos correspondentes à 
            BDGD atual e à versão anterior na base local. Essa etapa é necessária, pois os arquivos
            da BDGD constituem base de comparação necessária para a análise do AIS.</p>

            <p  style="text-align: justify;text-indent: 40px">A BDGD é uma fonte primária de dados geoespaciais que permite realizar comparações 
            temporais e espaciais, usando bases com referências distintas, identificando mudanças e validando informações declaradas. 
            O carregamento na base local possibilita um acesso mais eficiente e rápido aos dados,
            viabilizando a aplicação de algoritmos e ferramentas analíticas diretamente sobre o 
            conjunto de informações.</p>

            <p  style="text-align: justify;text-indent: 40px">Ademais, a utilização simultânea das versões atual e anterior permite uma abordagem 
            comparativa, mutação, que auxilia na detecção de inconsistências, avaliação de padrões de 
            evolução e suporte à tomada de decisão baseada em evidências. Este processo é 
            realizado para garantir a integridade e confiabilidade dos dados, 
            elementos balizadores da análise subsequente no AIS.</p>
        """)

        dir_arq_dbf = f"{local}/BDGD_ANT"
        dir_arq_dbf1 = f"{local}/BDGD_AT"
        dir_arq_base = f"{local}/BD_LOCAL"

        with st.container(border=True):

            st.html("""<h3>Exportação de GDB para Shapefile</h3>
                    <p   style="text-align: justify;text-indent: 40px">
                    Caso habilitada, esta etapa realizará a conversão das camadas contidas na geodatabase (<b>.gdb</b>) para 
                    o formato <b>ESRI Shapefile</b>, gerando os arquivos <b>.shp</b>, <b>.dbf</b>, <b>.shx</b> e demais 
                    arquivos auxiliares correspondentes. A conversão será aplicada a todas as camadas disponíveis na 
                    geodatabase informada, gravando os arquivos resultantes no diretório de destino selecionado, preservando a 
                    estrutura de atributos e a referência espacial dos dados originais.
                    </p>
                    """)
            exportar_gdb = st.checkbox(
                                        "Exportar arquivos GDB para Shapefile",
                                        value=False
                                    )
            if exportar_gdb:
                x = fnc_gdb(database, empresa, ano)

        col2 = st.columns([1,1,2,1,2,1,1], gap='small')
        with col2[2]:
            BDGD_AT = st.button("BDGD ATUAL", key="BDGD_AT")
        with col2[4]:
            BDGD_ANT = st.button("BDGD ANTERIOR", key="BDGD_ANT")
        if BDGD_AT:
            x = bsc_BDGD(dir_arq_dbf1, dir_arq_base, "AT", True, empresa, ano, database)
            st.text(f"Arquivo da BDGD atual, {empresa}, importado.")
        if BDGD_ANT:
            x = bsc_BDGD(dir_arq_dbf, dir_arq_base, "ANT", True, empresa, ano, database)
            st.text(f"Arquivo da BDGD anterior, {empresa}, importado.")
            if st.session_state.RTE:
                dir_arq_dbf2 = f"{local}/BDGD_RTE_ANT"
                x = bsc_BDGD(dir_arq_dbf2, dir_arq_base, "RTE", True, empresa, ano, database)
                st.text(f"Arquivo da BDGD da RTE Anterior, {empresa}, importado.")

def fnc_gdb(database = None, empresa= None, ano = None):
    with execucao_trilha(
                        db_path=database, script_nome="CONVERSÃO BDGD: GDB para DBF",
                        parametros={"empresa": empresa, "ano": ano},
                        ) as execucao_id:
        registrar_evento(
                            database,
                            execucao_id,
                            "ARQUIVO_GDB_CONVERSAO",
                            mensagem=(
                                f"Iniciado a configuração para processamento"
                            ),
                        )
        with st.container(border=True):
            st.html("<h4>Configuração da exportação</h4>")
            origem_gdb = st.text_input(
                                            "Pasta de origem da geodatabase (.gdb)",
                                            placeholder=r"Ex.: D:\Dados\CONSOL.gdb"
                                        )
            destino_shp = st.text_input(
                                            "Pasta de destino dos arquivos Shapefile",
                                            placeholder=r"Ex.: D:\Dados\EXPORTADOS"
                                        )
            if origem_gdb:
                origem = Path(origem_gdb)
                if not origem.exists():
                    st.error("A pasta de origem informada não existe.")
                elif origem.suffix.lower() != ".gdb":
                    st.warning("A origem informada não parece ser uma File Geodatabase (.gdb).")
                else:
                    st.success("Origem GDB válida.")

            if destino_shp:
                destino = Path(destino_shp)
                if not destino.exists():
                    st.warning("A pasta de destino ainda não existe. Ela poderá ser criada na exportação.")
                else:
                    st.success("Pasta de destino válida.")

            converter = st.button("Converter")
            a = st.empty()

            if destino_shp and origem_gdb and converter:
                registrar_evento(database, execucao_id, "CONVERSAO_GDB_DBF_INICIADA",
                                 mensagem=f"Iniciando conversão BDGD. De {origem} para {destino}.")
                gdb = origem
                saida = destino
                saida.mkdir(exist_ok=True)
                lst_arq = fiona.listlayers(gdb)

                a.progress(0, "Iniciando importação")
                for i, layer in enumerate(lst_arq):
                    a.progress(i/len(lst_arq), f"Exportando {layer}...")
                    nm_arq = Path(rf'{destino_shp}/{layer}.dbf')
                    if nm_arq.exists():
                        continue

                    gdf = gpd.read_file(
                                            gdb,
                                            layer=layer,
                                            engine="pyogrio"
                                        )
                    if isinstance(gdf, gpd.GeoDataFrame) and gdf.geometry is not None:
                        nm_arq = Path(destino_shp) / f"{layer}.shp"

                        if nm_arq.exists():
                            continue

                        gdf.to_file(
                                        nm_arq,
                                        driver="ESRI Shapefile",
                                        encoding="utf-8"
                                    )
                        registrar_artefato(database, execucao_id, str(nm_arq), "ENTRADA")
                    else:
                        nm_arq = Path(destino_shp) / f"{layer}.dbf"

                        if nm_arq.exists():
                            continue
                        dataframe_to_dbf(
                                            gdf,
                                            saida / f"{layer}.dbf"
                                        )

                        st.warning(f"{layer}: tabela sem geometria exportada como dbf.")

                registrar_evento(database, execucao_id, "CONVERSAO_GDB_DBF_FINALIZADA",
                                mensagem=f"Finalizada conversão BDGD. De {origem} para {destino}.")
                a.empty()       
