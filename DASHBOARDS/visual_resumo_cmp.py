import streamlit as st
import sqlite3 as sl, os
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from UTILS import (
                    desenhar_grafo_hierarquico, 
                    consultar_empresa,
                    bsc_dados_reg,
                    sorteio,
                    existe_tabela,
                    carga_sqlite_cache,
                    max_arq
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

def moeda_br(x):
    try:
        return f"{float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return x

def perc_br(x):
    try:
        return f"{float(x):,.2%}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return x
    
def formatar_df(df):
    df_fmt = df.copy()

    for col in df_fmt.columns:
        col_up = col.upper()

        if col_up.startswith(("VL", "QT", "FA", "DI")):
            df_fmt[col] = df_fmt[col].apply(moeda_br)

        elif col_up.startswith(("TX_", "DEP", "PCT", "VAR")):
            df_fmt[col] = df_fmt[col].apply(perc_br)

    return df_fmt

def bloco_html(titulo, texto, cor="#111827"):
    st.html(f"""
                    <h2>
                        {titulo}
                    </h2>
                    <p style="text-align: justify;text-indent: 40px">
                        {texto}
                    </p>
                       """)

def exportar_tabela_png(df, nome_arquivo, titulo=None, max_linhas=80):
    os.makedirs(rf"{st.session_state.tra_dir}/RELATORIOS/figuras", exist_ok=True)
    caminho = rf"{st.session_state.tra_dir}/RELATORIOS/figuras/{nome_arquivo}.png"

    df_img = df.head(max_linhas).copy()

    fig_altura = max(2.5, 0.35 * len(df_img) + 1.6)
    fig_largura = max(20, 2.5 * len(df_img.columns))

    fig, ax = plt.subplots(figsize=(fig_largura, fig_altura))
    ax.axis("off")

    if titulo:
        ax.set_title(titulo, fontsize=14, fontweight="bold", pad=16)

    tabela = ax.table(
                        cellText=df_img.values,
                        colLabels=df_img.columns,
                        cellLoc="center",
                        colLoc="center",
                        loc="center"
                    )

    tabela.auto_set_font_size(False)
    tabela.set_fontsize(8)
    tabela.scale(1, 1.35)

    for (row, col), cell in tabela.get_celld().items():
        cell.set_edgecolor("#d1d5db")

        if row == 0:
            cell.set_facecolor("#111827")
            cell.set_text_props(color="white", weight="bold")
        elif row % 2 == 0:
            cell.set_facecolor("#f9fafb")
        else:
            cell.set_facecolor("white")

    plt.tight_layout()
    fig.savefig(caminho, dpi=220, bbox_inches="tight")
    plt.close(fig)

    return caminho

def mostrar_tabela(df, nome_arquivo, titulo, altura=550, column_config=None):
    df_fmt = formatar_df(df)
    cols = st.columns([1,5,1], gap='small')
    with cols[1]:
        st.dataframe(
                        df_fmt,
                        width="stretch",
                        height=altura,
                        hide_index=True,
                        column_config=column_config
                    )
    exportar_tabela_png(df_fmt, nome_arquivo, titulo)

    return df_fmt

def painel_comparativo(df_FINAL, nm):
    col_bb = f'VL_ITEM_{nm}_BB'.replace(",","x").replace(".",",").replace("x",".")
    col_avl = f'VL_ITEM_{nm}_AVL'.replace(",","x").replace(".",",").replace("x",".")
    col_sff = f'VL_ITEM_{nm}_SFF'.replace(",","x").replace(".",",").replace("x",".")
    col_total_avl = f'VL_AVL_{nm}'.replace(",","x").replace(".",",").replace("x",".")
    col_total_sff = f'VL_SFF_{nm}'.replace(",","x").replace(".",",").replace("x",".")
    col_dif = f'DIF_AVL_SFF_{nm}'.replace(",","x").replace(".",",").replace("x",".")
    col_var = f'VAR_AVL_SFF_{nm}'.replace(",","x").replace(".",",").replace("x",".")

    df_FINAL[col_total_avl] = df_FINAL[col_bb].fillna(0) + df_FINAL[col_avl].fillna(0)
    df_FINAL[col_total_sff] = df_FINAL[col_bb].fillna(0) + df_FINAL[col_sff].fillna(0)

    df_FINAL[col_dif] = df_FINAL[col_total_avl] - df_FINAL[col_total_sff]

    df_FINAL[col_var] = np.where(
                                    df_FINAL[col_total_sff].abs() > 0,
                                    df_FINAL[col_dif] / df_FINAL[col_total_sff],
                                    0
                                )

    df_PRINT = df_FINAL[
                            [
                                'Nm_Item',
                                col_bb,
                                col_avl,
                                col_sff,
                                col_total_avl,
                                col_total_sff,
                                col_dif,
                                col_var,
                            ]
                        ].copy()

    total_avl = df_PRINT[col_total_avl].iloc[0].sum()
    total_sff = df_PRINT[col_total_sff].iloc[0].sum()
    dif_total = total_avl - total_sff
    var_total = dif_total / total_sff if total_sff else np.nan
    qtd_div = (df_PRINT[col_dif].abs() > 0.01).sum()

    
    st.html(

                f"""<p style="text-align: justify;text-indent: 40px">Esta seção compara os valores apurados pela avaliadora com os valores considerados pela SFF
                para a natureza {nm}. A diferença positiva indica valor AVL superior ao SFF; a diferença negativa
                indica valor SFF superior ao AVL.</p>"""

            )
    cols = st.columns([1,10,1], gap='small')
    with cols[1]:
        c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total AVL", moeda_br(total_avl))
    c2.metric("Total SFF", moeda_br(total_sff))
    c3.metric(
                "Diferença AVL - SFF",
                moeda_br(dif_total),
                delta=f"{var_total:.2%}".replace(",","x").replace(".",",").replace("x",".") if pd.notna(var_total) else "N/A"
            )
    c4.metric("Itens divergentes", int(qtd_div))
    config = {
                    "Nm_Item": st.column_config.TextColumn("Item"),
                    col_bb: st.column_config.TextColumn("Base Blindada (R$)"),
                    col_avl: st.column_config.TextColumn("Ajuste AVL (R$)"),
                    col_sff: st.column_config.TextColumn("Ajuste SFF (R$)"),
                    col_total_avl: st.column_config.TextColumn("Total AVL (R$)"),
                    col_total_sff: st.column_config.TextColumn("Total SFF (R$)"),
                    col_dif: st.column_config.TextColumn("Diferença (R$)"),
                    col_var: st.column_config.TextColumn("Variação (%)"),
                }

    mostrar_tabela(
                        df_PRINT,
                        nome_arquivo=f"comparativo_avl_sff_{nm.lower()}",
                        titulo=f"Comparativo AVL vs SFF — {nm}",
                        altura=550,
                        column_config=config
                    )

    return df_PRINT

def visualizador_resumo_cmp(st = None):
    if not'tra_dir' in st.session_state:
        st.html("""
                    <p style="text-align: justify;text-indent: 40px">
                    Você deve configurar o diretório de trabalho, empresa e período
                    na aba <i>Criar Pasta de Trabalho</i>, barra lateral.</p>
                """)
        return

    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year
    css = bsc_dados_reg("estilo_001", tipo="Estilo_CSS")
    dds = bsc_dados_reg('TBL_EMPRESAS')
    lst_emp = dds['Nm_EMPRESA'].drop_duplicates().to_list()
    st.html(f"<style>{css}</style>")
    raiz = Path(local)
    caminho_manifesto = raiz / "MANIFESTO" / "TRILHA_EXEC" / "execucoes.db"
    caminho_manifesto.parent.mkdir(parents=True, exist_ok=True)
    inicializa_database(str(caminho_manifesto))
    inicializa_detalhes(str(caminho_manifesto))
    inicializar_rastreamento(str(caminho_manifesto))
    database = str(caminho_manifesto)
    bd_path = f'{local}/BD_LOCAL/{empresa}_{ano}.db'
    bd_BDGDAT_path = f'{local}/BD_LOCAL/BDGD_AT_{empresa}_{ano}.db'
    bd_BDGDANT_path = f'{local}/BD_LOCAL/BDGD_ANT_{empresa}_{ano}.db'
    bd_EFD_path = f'{local}\BD_LOCAL\EFD_ICMS_{empresa}_{ano}.db'

    with sl.connect(bd_path) as bd:
        ANL_LST_TUC = pd.DataFrame()
        ANL_LST_TUC13 = pd.DataFrame()
        if existe_tabela('BASE_INCR_COMP', bd):
            bloco_html(
                            "Resumo Completo",
                            """
                            A seguir apresenta-se o resultado consolidado do arquivo incremental, organizado por atividade.
                            A tabela permite verificar os valores informados, os valores simulados e a respectiva variação apurada.
                            """,
                            cor="#E82C1E"
                        )
            sSQL = "SELECT * FROM BASE_INCR_COMP"
            df_BI = pd.read_sql(sSQL, bd)

            config_bi = {
                            "Nm_Item": st.column_config.TextColumn("Item"),
                            "VL_AVAL": st.column_config.TextColumn("Avaliadora (R$)"),
                            "VL_SIM": st.column_config.TextColumn("Simulado (R$)"),
                            "PCT_VAR": st.column_config.TextColumn("Variação (%)"),
                        }

            mostrar_tabela(
                                df_BI,
                                nome_arquivo="resumo_incremental",
                                titulo="Resumo Consolidado do Arquivo Incremental",
                                altura=550,
                                column_config=config_bi
                            )
        
        if existe_tabela('RESUMO_BB', bd):
            bloco_html(
                        "Resumo da Base Blindada após Movimentação",
                        """
                        A tabela apresenta a posição consolidada da base blindada após as movimentações consideradas.
                        Os valores estão segregados por natureza: geração, distribuição, administração e comercialização.
                        A análise detalhada dos critérios de cálculo deve ser consultada no relatório técnico correspondente.
                        """,
                        cor="#E82C1E"
                    )

            sSQL = """
                        SELECT 
                            Item AS Nm_Item,
                            VL_SALDO_G AS VL_ITEM_GER_BB,
                            VL_SALDO_D AS VL_ITEM_DIST_BB,
                            VL_SALDO_A AS VL_ITEM_ADM_BB,
                            VL_SALDO_C AS VL_ITEM_COMER_BB   
                        FROM RESUMO_BB
                    """

            df_BB = pd.read_sql(sSQL, bd)

            mostrar_tabela(
                                df_BB,
                                nome_arquivo="resumo_base_blindada",
                                titulo="Resumo da Base Blindada após Movimentação",
                                altura=450
                            )

        if len(df_BI) > 0 and len(df_BB)>0:
            df_FINAL = df_BB.merge(df_BI, how="left", on="Nm_Item")

            bloco_html(
                        "Painel Comparativo de Valores — Avaliadora versus SFF",
                        """
                        Este painel consolida a comparação entre os valores calculados pela avaliadora e os valores
                        considerados pela SFF. A análise está segregada por natureza, permitindo verificar diferenças
                        absolutas, variações percentuais e itens com divergência relevante.
                        """,
                        cor="#E82C1E"
                    )

            for nm in ["GER", "DIST", "ADM", "COMER"]:
                painel_comparativo(df_FINAL, nm)