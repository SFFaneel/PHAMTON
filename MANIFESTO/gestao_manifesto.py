from MANIFESTO import criar_manifesto_multi
import streamlit as st
import os, re

@st.fragment
def criar_manifesto():

    local = st.session_state.tra_dir
    empresa = st.session_state.nm_empr
    ano = st.session_state.dt_fim.year

    pasta_origem = rf"{local}\DADOS_BRUTOS_MANUAL"
    diretorio_auditoria = rf"{local}\MANIFESTO\TRILHA_DADOS"
    padrao_numerico = r'_\d{5}_\d{8}'
    chave_primaria = "ID"

    arquivos = os.listdir(pasta_origem)
    arquivos_csv = sorted(
                        nome for nome in arquivos
                        if nome.lower().endswith(".csv")
                    )
    total = len(arquivos_csv)
    if total == 0:
        st.info("Nenhum arquivo CSV encontrado para processamento.")
    else:
            with st.container():
                    col1 = st.columns([1,5,1], gap='small')
                    with col1[1]:
                        st.html("<h1>Criando Manifesto Eletrônico de Dados</h1>")
                        progresso = st.progress(
                                                    0,
                                                    text=f"Preparando processamento de {total} arquivo(s)..."
                                                )

                        resultados = []
                        sucessos = 0
                        erros = 0

                        with st.status(
                                            "Gerando manifestos eletrônicos...",
                                            expanded=True
                                        ) as status:

                            for numero, nome_arquivo in enumerate(arquivos_csv, start=1):

                                caminho_completo = os.path.join(
                                                                    pasta_origem,
                                                                    nome_arquivo
                                                                )

                                id_arquivo = re.sub(
                                                        padrao_numerico,
                                                        "",
                                                        os.path.splitext(nome_arquivo)[0]
                                                    )

                                progresso.progress(
                                                        (numero - 1) / total,
                                                        text=(
                                                            f"Processando {numero}/{total}: "
                                                            f"{nome_arquivo}"
                                                        )
                                                    )

                                st.write(
                                            f"**{numero}/{total} — {nome_arquivo}**"
                                        )

                                try:
                                    resultado = criar_manifesto_multi(
                                                                        arquivo=caminho_completo,
                                                                        id_arquivo=id_arquivo,
                                                                        diretorio_auditoria=diretorio_auditoria,
                                                                        chave=chave_primaria,
                                                                        sep="|",
                                                                        encoding="latin-1",
                                                                        st=st
                                                                    )

                                    resultados.append({
                                                        "arquivo": nome_arquivo,
                                                        "id_arquivo": id_arquivo,
                                                        "status": resultado["status"],
                                                        "versao": resultado["versao"],
                                                    })

                                    sucessos += 1

                                    if resultado["status"] == "sem_alteracao":
                                        st.write(
                                                    f"Sem alterações no arquivo. "
                                                    f"Versão ativa: **{resultado['versao']}**"
                                                )

                                    else:
                                        st.write(
                                                    f"Nova versão: **{resultado['versao']}** "
                                                    f"— +{resultado['incluidos']} incluídos, "
                                                    f"-{resultado['excluidos']} excluídos, "
                                                    f"{resultado['registros_alterados']} alterados."
                                                )

                                except Exception as exc:
                                    erros += 1

                                    st.error(
                                                f"Erro ao processar {nome_arquivo}: {exc}"
                                            )

                                finally:
                                    progresso.progress(
                                                            numero / total,
                                                            text=(
                                                                f"Processamento: {numero}/{total} "
                                                                f"arquivo(s) concluído(s)"
                                                            )
                                                        )

                            if erros:
                                status.update(
                                                    label=(
                                                        f"Processamento finalizado: "
                                                        f"{sucessos} sucesso(s), {erros} erro(s)"
                                                    ),
                                                    state="error",
                                                    expanded=True
                                                )
                            else:
                                status.update(
                                                    label=f"{sucessos} manifesto(s) processado(s)",
                                                    state="complete",
                                                    expanded=False
                                                )
    return diretorio_auditoria
