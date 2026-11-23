import streamlit as st
import sqlite3 as sl
import pandas as pd
import os, re, numpy as np
from datetime import datetime
from pandas.tseries.offsets import DateOffset
from pathlib import Path
from UTILS import (
                    busca_ipca,
                    bsc_dados_reg,
                    existe_tabela
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

imagem_fundo = "imagens/bull_bck.png"

@rastrear_funcao
def imp_ARQ(LST_ARQ=None,
            dir_arq_fcoge=None,
            colunas=None,
            ajstdo=False,
            *,
            database,
            execucao_id,):
    
    LST_ARQ = LST_ARQ or []
    meus_arq = []
    quadros = []
    nr_arq = len(LST_ARQ)
    progresso = st.progress(0, text= "Iniciando a importação COGE...")

    registrar_evento(
                        database,
                        execucao_id,
                        "INICIO_LEITURA_COGE",
                        mensagem=f"Iniciada a leitura de {nr_arq} arquivos.",
                    )
    registrar_metrica(
                        database,
                        execucao_id,
                        "arquivos_encontrados",
                        nr_arq,
                    )

    for i, arq in enumerate(LST_ARQ, start=1):
        arq_cam = Path(dir_arq_fcoge) / arq
        progresso.progress(
                                int((i - 1) / nr_arq * 100),
                                text=f"Processando {arq}..."
                            )
        registrar_evento(
                            database,
                            execucao_id,
                            "INICIO_ARQUIVO_COGE",
                            mensagem=f"Iniciada a leitura do arquivo {arq}.",
                        )
        meus_arq.append(arq_cam)

        if arq.upper()[:6] == 'CONFID':
            df = (
                    pd.read_csv(
                                    arq_cam,
                                    sep="|",
                                    decimal=".",
                                    encoding="latin-1",
                                    lineterminator="\r",
                                    dtype=str
                                )
                    .assign(
                                Cd_FOR_COGE=lambda x: x["Código"].str.strip(),
                                Nr_COGE=lambda x: pd.to_numeric(x["Variação(%)"], errors="coerce"),
                                DT_INI=lambda x: pd.to_datetime(x["DATA (ANO.MES)"], format="%Y.%m", errors="coerce"),
                                DT_FIM=lambda x: pd.to_datetime(x["Data Base"], format="%Y.%m", errors="coerce"),
                            )
                )

            df = df[['Cd_FOR_COGE','Nr_COGE','DT_INI','DT_FIM']]
            df=df[df['DT_INI'].notnull()]
        elif arq.endswith(".txt"):
            df=pd.read_csv(arq_cam,sep="|",decimal=',',on_bad_lines='skip',encoding="utf_8_sig",
                        header = None,names=colunas,lineterminator='\r', dtype=str);
            
            df[1]=df[0].str[1:9].str.strip() 
            df[2]=pd.to_numeric(df[0].str[9:],errors='coerce')
            df[3]=datetime.strptime(df.loc[0,0][0:df.loc[0,0].find(",")],'%m/%Y')
            df[4]=datetime.strptime(df.loc[0,0][df.loc[0,0].find(",") + (1 ):],'%m/%Y')
            df=df[[1,2,3,4]]
            df=df[df[1].notnull() & df[1].str.startswith("FCM")]
        elif (arq[0:6] == 'Forms_'):
            df=pd.read_csv(arq_cam,sep=";",decimal='.',on_bad_lines='skip',encoding="utf_8_sig",
                        header=0, lineterminator='\n', dtype=str);
            df[1]=df['Código']
            df[2]=pd.to_numeric(df['Variação(%)'],errors='coerce')
            df[3]=datetime.strptime(arq[17:arq.find("_to_")],'%Y-%m')
            df[4]=datetime.strptime(arq[arq.find("_to_")+4:arq.find("_",arq.find("_to_")+4)],'%Y-%m')
            df=df[[1,2,3,4]]
            df=df[df[2].notnull()]
        elif  (arq[0:12] == 'FormulasCOGE'):
            try:
                df=pd.read_csv(arq_cam,sep=";",on_bad_lines='skip',encoding="utf_8_sig",
                        header = None,lineterminator='\n', dtype=str);
            except:
                df=pd.read_csv(arq_cam,sep="|",on_bad_lines='skip',encoding="Latin-1",
                        header = None,lineterminator='\n', dtype=str);
            df[1]=df[0]
            df[2]=pd.to_numeric(df[2],errors='coerce')
            datas = re.findall(r'(\d{1,2})-(\d{4})', arq)

            df[3]=datetime.strptime(f"{datas[0][0]}-{datas[0][1]}", "%m-%Y")
            df[4]=datetime.strptime(f"{datas[1][0]}-{datas[1][1]}", "%m-%Y")
            df=df[[1,2,3,4]]
            df=df[df[2].notnull()]
        elif arq.endswith(".csv"):
            try:
                df=pd.read_csv(arq_cam,sep=";",on_bad_lines='skip',encoding="utf_8_sig",
                        header = None,lineterminator='\n', dtype=str);
            except:
                df=pd.read_csv(arq_cam,sep="|", on_bad_lines='skip',encoding="Latin-1",
                        header = None, lineterminator='\n', dtype=str);
            df1 = df.copy()
            if df.iloc[0,0] == 'Fórmula Original':
                df = df.iloc[1:][[1,4,3,5]]
                df[4]=pd.to_numeric(df[4],errors='coerce')
                df[3] = pd.to_datetime(df[3], format='%Y.%m', errors='coerce')
                df[5] = pd.to_datetime(df[5], errors='coerce')
            else:
                df[1]=df[0]
                df[2]=pd.to_numeric(df[2],errors='coerce')
                padrao_data = r"\b(\d{4}-\d{2})\b"
                match = re.search(padrao_data, arq)
                if match:
                    data_texto = match.group(1)
                    df[3] = datetime.strptime(data_texto, "%Y-%m")
                else:
                    raise UserWarning("Não foi encontrado o formato de ano-mes no arquivo")
                df[4]=datetime.strptime(arq[arq.find("_to_")+4:arq.find("_",arq.find("_to_")+4)],'%Y-%m')
                df=df[[1,2,3,4]]
                df=df[df[2].notnull()]
        quadros.append(df)
        meus_arq.append(str(arq_cam))

        registrar_artefato(database, execucao_id, str(arq_cam), "ENTRADA")

        registrar_evento(
                            database,
                            execucao_id,
                            "ARQUIVO_COGE_PROCESSADO",
                            mensagem=(
                                f"Arquivo {arq} processado: "
                                f"{len(df)} registros."
                            ),
                        )

        registrar_metrica(
                                database,
                                execucao_id,
                                f"linhas_arquivo_{i}",
                                len(df),
                            )
    progresso.progress(100, text="Leitura dos arquivos concluída.")
    if not quadros:
        raise ValueError(
                            "Nenhum arquivo COGE produziu dados para importação."
                        )

    tbl_FCOGE = pd.concat(
                            quadros,
                            ignore_index=True
                        )

    tbl_FCOGE.columns = ['Cd_FOR_COGE','Nr_COGE','DT_INI','DT_FIM']
    tbl_FCOGE = tbl_FCOGE.sort_values(by=['Cd_FOR_COGE','DT_INI'])

    tbl_FCOGE['DT_REF']=tbl_FCOGE['DT_INI']+pd.DateOffset(months=-(1-ajstdo))
    if 'Nr_COGE' in tbl_FCOGE.columns and tbl_FCOGE['Nr_COGE'].dtype in [object, "string"]:
        tbl_FCOGE['Nr_COGE'] = pd.to_numeric(tbl_FCOGE['Nr_COGE'].str.strip(), errors="coerce")

    tbl_FCOGE['FC']=tbl_FCOGE['Nr_COGE']/100 + 1
    tbl_FCOGE = tbl_FCOGE.drop_duplicates(subset=['Cd_FOR_COGE','Nr_COGE','DT_INI'])

    novas_linhas = []
    for _, grupo in tbl_FCOGE.groupby('Cd_FOR_COGE'):
        ultima = grupo.sort_values('DT_REF').iloc[-1].copy()
        nova = ultima.copy()
        nova['DT_INI'] += DateOffset(months=1)
        nova['DT_FIM'] += DateOffset(months=1)
        nova['DT_REF'] += DateOffset(months=1)
        nova['Nr_COGE'] = 0
        nova['FC'] = 1
        novas_linhas.append(nova)

    tbl_FCOGE = pd.concat([tbl_FCOGE, pd.DataFrame(novas_linhas)], ignore_index=True)
    tbl_FCOGE = tbl_FCOGE.sort_values(['Cd_FOR_COGE', 'DT_REF']).reset_index(drop=True)

    registrar_metrica(
                        database,
                        execucao_id,
                        "linhas_coge_consolidadas",
                        len(tbl_FCOGE),
                    )

    registrar_evento(
                        database,
                        execucao_id,
                        "CONSOLIDACAO_COGE",
                        mensagem=(
                            f"Consolidação concluída com "
                            f"{len(tbl_FCOGE)} registros."
                        ),
                    )
    return tbl_FCOGE, meus_arq

def imp_COGE():
    if not 'tra_dir' in st.session_state:
        st.html("""
                <p>Você deve configurar o diretório de trabalho na aba <i>Criar Pasta de Trabalho</i>, barra lateral.</p>
            """)
        return
    col1 = st.columns([1,5,1], gap='small')
    with col1[1]:
        with st.container():
            local = st.session_state.tra_dir
            empresa = st.session_state.nm_empr
            ano = st.session_state.dt_fim.year
            css = bsc_dados_reg("estilo_001", tipo="Estilo_CSS")
            st.html(f"<style>{css}</style>")

            raiz = Path(local)
            caminho_manifesto = raiz / "MANIFESTO" / "TRILHA_EXEC" / "execucoes.db"
            caminho_manifesto.parent.mkdir(parents=True, exist_ok=True)
            inicializa_database(str(caminho_manifesto))
            inicializa_detalhes(str(caminho_manifesto))
            inicializar_rastreamento(str(caminho_manifesto))
            database = str(caminho_manifesto)

            colunas = [i for i in range(0, 40)]

            st.html("""<h1>Importação dos arquivos da COGE</h1><br><br>
                <p  style="text-align: justify;text-indent: 40px">Nesta etapa do processo, 
                realiza-se o carregamento dos arquivos correspondentes aos fatores
                de atualização da COGE.</p><br>
                """)

            dir_arq_fcoge = f"{local}/FCOGE"
            dir_arq_base = f"{local}/BD_LOCAL"
            LST_ARQ = os.listdir(dir_arq_fcoge)
            cols = st.columns([1,1,1,1,1,4], gap='small')
            with cols[5]:
                ajstdo = st.checkbox("Delay ajustado nos indicadores importados?", value=False, help="Se a avaliadora fez a extração considerando o delay, colocar ativar a opção.")
            with cols[1]:
                btIMP = st.button("Importar", width='stretch')
            if btIMP and len(LST_ARQ)>0:
                caminho_bd = (
                                    Path(local)
                                    / "BD_LOCAL"
                                    / f"{empresa}_{ano}.db"
                                )

                caminho_bd.parent.mkdir(
                                            parents=True,
                                            exist_ok=True
                                        )

                with execucao_trilha(
                                        db_path=database, script_nome="Importação Indicadores Econômicos",
                                        parametros={"empresa": empresa, "ano": ano},
                                    ) as execucao_id:
                    registrar_evento(
                                        database,
                                        execucao_id,
                                        "INICIO_IMPORTACAO_COGE",
                                        mensagem=(
                                            f"Empresa: {empresa}; "
                                            f"ano: {ano}; "
                                            f"delay ajustado: {ajstdo}."
                                        ),
                                    )

                    tbl_FCOGE, meus_arq = imp_ARQ(
                                                    LST_ARQ,
                                                    dir_arq_fcoge,
                                                    colunas,
                                                    ajstdo,
                                                    database=database,
                                                    execucao_id=execucao_id,
                                                )
                    with sl.connect(caminho_bd) as bd:
                        tbl_FCOGE.to_sql('tbl_FCOGE', bd, if_exists='replace', index=False)

                    registrar_artefato(database, execucao_id, str(caminho_bd), "SAIDA")

                    registrar_metrica(
                                        database,
                                        execucao_id,
                                        "linhas_gravadas_sqlite",
                                        len(tbl_FCOGE),
                                    )

                    registrar_evento(
                                        database,
                                        execucao_id,
                                        "FIM_IMPORTACAO_COGE",
                                        mensagem=(
                                            "Tabela tbl_FCOGE gravada "
                                            "com sucesso no banco local."
                                        ),
                                    )

                    st.success("Carregado dados na database local.")

                st.html("""<p>Tabela COGE:</p>""")
                config = {
                                "Cd_FOR_COGE": st.column_config.TextColumn("Código COGE"),
                                "DT_INI": st.column_config.DateColumn("Data de Início", format="DD/MM/YYYY"),
                                "DT_FIM": st.column_config.DateColumn("Data de Fim", format="DD/MM/YYYY"),
                                "DT_REF": st.column_config.DateColumn("Data de Referência", format="DD/MM/YYYY"),
                                "FC": st.column_config.NumberColumn("FATOR ATUALIZAÇÃO"),
                            }

                st.dataframe(tbl_FCOGE, width='stretch', hide_index=True,  column_config=config)

            with sl.connect(f'{local}\BD_LOCAL\{empresa}_{ano}.db') as bd:
                if existe_tabela("tbl_FCOGE", bd):
                    tbl_FCOGE = pd.read_sql("SELECT * FROM tbl_FCOGE WHERE Cd_FOR_COGE = 'FCM0403'", bd)
                else:
                    tbl_FCOGE = pd.DataFrame()

            if not tbl_FCOGE.empty:
                ipca = busca_ipca()[['Dt_REF', 'Nr_IPCA']].rename(columns={'Dt_REF': 'DT_REF'})
                tbl_FCOGE['DT_REF'] = pd.to_datetime(tbl_FCOGE['DT_REF'])
                tbl_FCOGE['DT_FIM'] = pd.to_datetime(tbl_FCOGE['DT_FIM'])
                tbl_FCOGE['DT_INI'] = pd.to_datetime(tbl_FCOGE['DT_INI'])
                data = pd.to_datetime(tbl_FCOGE.iloc[0,-3])
                mes_anterior = (data.replace(day=1) - pd.DateOffset(months=1))
                Nr_IPCA = ipca[ipca['DT_REF'] == mes_anterior]['Nr_IPCA'].iloc[0]
                ipca = tbl_FCOGE.merge(ipca, how='left', on='DT_REF')

                ipca['IPCA_DT_BASE'] = Nr_IPCA
                ipca['FT_IPCA'] = ipca['IPCA_DT_BASE'] / ipca['Nr_IPCA']
                ipca["FLG_CONVERGE"] = np.isclose(
                                                        ipca["FC"],
                                                        ipca["FT_IPCA"],
                                                        rtol=0.001
                                                    )
                st.divider()
                perc = (len(ipca) - ipca['FLG_CONVERGE'].sum()) / len(ipca)
                erros = f"{perc:.2%}".replace(".",",")
                if perc < 0.001:
                    msg = f"está 'ok' ({erros} de divergência)"
                else:
                    msg = f"atenção: {erros} não convergiu"

                st.html(
                            f"""
                            <p style='text-align: justify; padding-left:60px;'>
                                Será realizada a comparação entre o indicador COGE equivalente ao IPCA e o dado oficial divulgado pelo IBGE, com 
                                o objetivo de verificar a consistência entre as duas métricas. Caso sejam observadas divergências entre os valores, 
                                deverá ser conduzida investigação para identificar suas possíveis causas, considerando diferenças metodológicas, 
                                de processamento ou de atualização das bases utilizadas. Ressalta-se que a metodologia do indicador COGE pode 
                                introduzir um delay temporal na apuração do resultado, o que requer atenção na análise comparativa. Nesse contexto, 
                                solicita-se confirmar se o delay previsto na metodologia COGE foi devidamente compensado no procedimento de comparação 
                                com o dado divulgado pelo IBGE, de modo a garantir a adequada correspondência entre os períodos de referência 
                                analisados. No caso, {msg}.
                            </p>
                            """
                        )
                st.dataframe(ipca, width='stretch', hide_index=True)
                ipca.to_excel(fr"{local}/BP_ANLS/teste_coge_IPCA.xlsx", index=False)
        

    
