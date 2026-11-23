
from datetime import date, datetime
from pathlib import Path
import shutil

import pandas as pd
import streamlit as st

from UTILS import (
                        cria_DB,
                        configurar_logger,
                        liberar_logger,
                        bsc_dados_reg,
                    )
from MANIFESTO import execucao_trilha


ARQUIVO_CONFIG = Path("tbl_ini.csv")

DIRETORIOS_TRABALHO = (
                        "DADOS_BRUTOS_MANUAL",
                        "LAUDO",
                        "ECD",
                        "EFD_ICMS",
                        "EFD_CONT",
                        "ECF",
                        "CBS",
                        "IBS",
                        "NFe_NFSe",
                        "BDGD_ANT",
                        "BDGD_AT",
                        "BDGD_ANLS",
                        "FCOGE",
                        "BP_ANLS",
                        "INC_ANLS",
                        "OE_ANLS",
                        "BB_ANLS",
                        "AIS_ANLS",
                        "ICMS_ANLS",
                        "RELATORIOS",
                        "BD_LOCAL",
                        "IMAGENS",
                        "PDF_SUMARIO",
                        "PDF_SDI",
                        "PDF_CONTRATOS",
                        "IMAGENS_SUMARIO",
                    )

CAMPOS_CONFIG = ("dir_trab", "nm_emp", "dt_ini", "dt_fim")

def carregar_configuracao() -> dict:
    padrao = {
                    "dir_trab": str(Path.home() / "Downloads" / "TRABALHO"),
                    "nm_emp": "",
                    "dt_ini": "",
                    "dt_fim": "",
                }

    if not ARQUIVO_CONFIG.is_file():
        return padrao

    try:
        df = pd.read_csv(
                            ARQUIVO_CONFIG,
                            sep="|",
                            encoding="Latin-1",
                            dtype=str,
                            keep_default_na=False,
                        )

        if not {"cat", "dado"}.issubset(df.columns):
            raise ValueError("Estrutura inválida de tbl_ini.csv")

        for campo in CAMPOS_CONFIG:
            valores = df.loc[df["cat"] == campo, "dado"]
            if not valores.empty:
                padrao[campo] = str(valores.iloc[-1])

    except (OSError, ValueError, pd.errors.ParserError) as erro:
        st.warning(f"Configuração anterior não carregada: {erro}")

    return padrao


def salvar_configuracao(config: dict) -> None:
    df = pd.DataFrame(
                        {
                            "cat": CAMPOS_CONFIG,
                            "dado": [
                                str(config[campo])
                                for campo in CAMPOS_CONFIG
                            ],
                        }
                    )

    df.to_csv(
                ARQUIVO_CONFIG,
                sep="|",
                encoding="Latin-1",
                index=False,
            )


def converter_data(valor: str, padrao: date) -> date:
    if not valor:
        return padrao

    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError:
        return padrao


def validar_diretorio(caminho: str) -> Path:
    if not caminho.strip():
        raise ValueError("Informe o diretório de trabalho.")

    raiz = Path(caminho.strip()).expanduser().resolve()

    if raiz == Path(raiz.anchor):
        raise ValueError("Não é permitido usar a raiz do disco.")

    if raiz == Path.home().resolve():
        raise ValueError("Não é permitido usar a pasta do usuário.")

    if raiz == Path.cwd().resolve():
        raise ValueError(
                            "O diretório de trabalho não pode ser a pasta da aplicação."
                        )

    return raiz


def criar_estrutura(raiz: Path) -> None:
    raiz.mkdir(parents=True, exist_ok=True)
    for nome in DIRETORIOS_TRABALHO:
        (raiz / nome).mkdir(parents=True, exist_ok=True)
    (raiz / "LOGS").mkdir(parents=True, exist_ok=True)
    (raiz / "MANIFESTO" / "TRILHA_EXEC").mkdir(
                                                    parents=True,
                                                    exist_ok=True,
                                                )

def aplicar_configuracao(
                            raiz: Path,
                            empresa: str,
                            data_ini: date,
                            data_fim: date,
                        ) -> None:
 
    criar_estrutura(raiz)
    pasta_execucao = raiz / "MANIFESTO" / "TRILHA_EXEC"
    with execucao_trilha(
                            db_path=str(pasta_execucao / "execucoes.db"),
                            script_nome="inicio",
                            script_versao="1.0.0",
                        ):
        
        logger = configurar_logger(nome_arquivo=empresa, diretorio_logs=str(raiz / "LOGS"),)
        config = {
                    "dir_trab": str(raiz),
                    "nm_emp": empresa,
                    "dt_ini": data_ini.isoformat(),
                    "dt_fim": data_fim.isoformat(),
                 }

        salvar_configuracao(config)
        st.session_state.update(
                                    {
                                        "tra_dir": str(raiz),
                                        "nm_empr": empresa,
                                        "dt_ini": data_ini,
                                        "dt_fim": data_fim,
                                        "RTE": False,
                                        "SIST_CONFIG": True,
                                        "LOGGER": logger,
                                        "database_MAN" : "",
                                        "execucao_id" : ""
                                    }
                                )
        logger.info(
                        "Configuração concluída: empresa=%s, diretório=%s",
                        empresa,
                        raiz,
                    )


@st.dialog("⚠️ Confirmar exclusão")
def confirmar_exclusao(
                            raiz: Path,
                            empresa: str,
                            data_ini: date,
                            data_fim: date,
                        ) -> None:
    st.warning(
                    f"Todos os arquivos de **{raiz}** serão excluídos "
                    "permanentemente. Esta ação não pode ser desfeita."
                )

    _, col_sim, _, col_nao, _  = st.columns([1,2,1,2,1])

    with col_sim:
        if st.button(
                    "Sim, apagar",
                    type="primary",
                ):
            try:
                if raiz.exists():
                    if not raiz.is_dir() or raiz.is_symlink():
                        raise ValueError(
                                            "O destino não é um diretório comum."
                                        )
                    liberar_logger(raiz)
                    shutil.rmtree(raiz)

                aplicar_configuracao(
                                        raiz, empresa, data_ini, data_fim
                                    )
            except Exception as erro:
                st.error(f"Falha na configuração: {erro}")
                return

            st.session_state["config_sucesso"] = (
                                                    f"Diretório {raiz} configurado com sucesso."
                                                )
            st.rerun()

    with col_nao:
        if st.button(
                        "Não, cancelar",
                    ):
            st.rerun()

def iniciar() -> None:
    config = carregar_configuracao()
    css = bsc_dados_reg("estilo_001",tipo="Estilo_CSS")
    if isinstance(css, str) and css:
        st.html(f"<style>{css}</style>")

    st.html(
                    """<p style="text-align: justify;text-indent: 40px; padding-top: 10px">
                    Defina um diretório de trabalho. Caso já exista, 
                    seus arquivos serão preservados, exceto quando 
                    a opção de exclusão for selecionada.</p>"""
                )

    st.caption(f"Endereço do aplicativo: {st.context.url}")
    st.divider()
    apagar = st.checkbox("Excluir diretório, se existir", value=False,)

    tra_dir = st.text_input("Diretório de trabalho", value=config["dir_trab"],)
    empresas = bsc_dados_reg("TBL_EMPRESAS")

    if (not isinstance(empresas, pd.DataFrame) or "Nm_EMPRESA" not in empresas.columns):
        st.error("Não foi possível carregar o cadastro de empresas.")
        return

    lista_empresas = (
                        empresas["Nm_EMPRESA"]
                        .dropna()
                        .astype(str)
                        .drop_duplicates()
                        .tolist()
                    )

    if not lista_empresas:
        st.error("Nenhuma empresa cadastrada.")
        return

    empresa_padrao = config["nm_emp"]

    indice = (
                lista_empresas.index(empresa_padrao)
                if empresa_padrao in lista_empresas
                else 0
            )

    hoje = date.today()

    data_ini_padrao = converter_data(config["dt_ini"], hoje)
    data_fim_padrao = converter_data(config["dt_fim"], hoje)

    data_min_ini = (
                        date(1900, 1, 1)
                        if data_ini_padrao.year == 1900
                        else date(2019, 1, 1)
                    )

    data_max = date(hoje.year + 5, 12, 31)

    col1, col2, col3 = st.columns(3)

    with col1:
        empresa = st.selectbox(
                                "Empresa:",
                                lista_empresas,
                                index=indice,
                            )

    with col2:
        data_ini = st.date_input(
                                    "Data inicial período incremental:",
                                    value=data_ini_padrao,
                                    min_value=data_min_ini,
                                    max_value=data_max,
                                )

    with col3:
        data_fim = st.date_input(
                                    "Data final período incremental:",
                                    value=data_fim_padrao,
                                    min_value=date(hoje.year - 10, 1, 1),
                                    max_value=data_max,
                                )

    st.divider()

    _, centro, _ = st.columns([2, 1, 2])

    with centro:
        configurar = st.button(
                                    "(RE)Configurar",
                                    type="primary",
                                    use_container_width=True,
                                )

    if mensagem := st.session_state.pop("config_sucesso", None):
        st.success(mensagem)

    if not configurar:
        return

    if data_fim <= data_ini:
        st.error(
                    "A data final deve ser posterior à data inicial."
                )
        return

    try:
        raiz = validar_diretorio(tra_dir)

        if apagar and raiz.exists():
            confirmar_exclusao(
                                    raiz, empresa, data_ini, data_fim
                                )
            return

        with st.spinner("Configurando ambiente de trabalho..."):
            aplicar_configuracao(raiz, empresa, data_ini, data_fim)

        st.success(f"Diretório {raiz} configurado com sucesso.")

    except Exception as erro:
        st.error(f"Erro ao configurar ambiente: {erro}")





  
    
    