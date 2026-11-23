from pathlib import Path
from pydantic import ValidationError
import pandas as pd
import pytest
import sys, tempfile
from copy import deepcopy

import VALIDADOR.validador_funcoes as VAL_D

IS_WINDOWS = sys.platform == "win32"
DOWNLOADS = Path.home() / "Downloads"
DIRETORIO_TESTES = DOWNLOADS / "auditoria_pytest"

def duplo_positivo(campo):
    return [
                {
                    "campo": campo,
                    "valor": "0.",
                    "descricao": "Valor zero",
                },
                {
                    "campo": campo,
                    "valor": "-1.",
                    "descricao": "Valor negativo",
                },
                {
                    "campo": campo,
                    "valor": "abc",
                    "descricao": "Valor não numérico",
                },
                {
                    "campo": campo,
                    "valor": "",
                    "descricao": "Valor vazio",
                },
            ]

def inteiro_positivo(campo):
    return [
                {
                    "campo": campo,
                    "valor": "0",
                    "descricao": "Valor zero",
                },
                {
                    "campo": campo,
                    "valor": "-1",
                    "descricao": "Valor negativo",
                },
                {
                    "campo": campo,
                    "valor": "abc",
                    "descricao": "Valor não numérico",
                },
                {
                    "campo": campo,
                    "valor": "",
                    "descricao": "Valor vazio",
                },
            ]

def texto_maximo(campo, limite):
    return [
                {
                    "campo": campo,
                    "valor": "X" * (limite + 1),
                    "descricao": f"Texto acima de {limite} caracteres",
                },
            ]

def data_inc(campo):
    return [
                {
                    "campo": campo,
                    "valor": "01/01/2025",
                    "descricao": f"{campo} com formato inválido (dd/mm/yyyy).",
                },
                {
                    "campo": campo,
                    "valor": "12/21/2025",
                    "descricao": f"{campo} com formato inválido (mm/dd/yyyy).",
                },
                {
                    "campo": campo,
                    "valor": "",
                    "descricao": f"{campo} com formato inválido (vazio).",
                },
                {
                    "campo": campo,
                    "valor": "20250225",
                    "descricao": f"{campo} com formato inválido (yyyymmdd).",
                },
                {
                    "campo": campo,
                    "valor": "2025-02-25",
                    "descricao": f"{campo} com formato inválido (yyyy-mm-dd).",
                },
            ]

CASOS_MODELOS = [
                    {
                        "modelo": VAL_D.TBLDescODI,
                        "valido": {
                            "Id_ODI": "1",
                            "Cd_ODI": "COD001",
                            "Txt_DESC_ODI": "Descrição válida",
                        },
                        "invalidos": [
                            *inteiro_positivo("Id_ODI"),
                            *texto_maximo("Cd_ODI", 50),
                            *texto_maximo("Txt_DESC_ODI", 1000),
                        ],
                    },
                    {
                        "modelo": VAL_D.TBLBPfpuar,
                        "valido": {
                            "Id_BP_FP": "1",
                            "Nr_Parcela": "1",
                            "VL_Parcela": "1234,89",
                            "Dt_PMTO": "2023/10/28",
                            "Txt_OBS": "Sem observação",
                            "Id_Ext_CMP": "67",
                            "Nr_DOC_COMP": "abcCOMP001",
                        },
                        "invalidos": [
                            *inteiro_positivo("Id_BP_FP"),
                            *inteiro_positivo("Nr_Parcela"),
                            *inteiro_positivo("Id_Ext_CMP"),
                            *texto_maximo("Nr_DOC_COMP", 50),
                            *texto_maximo("Txt_OBS", 1000),
                            *duplo_positivo("VL_Parcela"),
                            *data_inc("Dt_PMTO"),
                        ],
                    },
                ]

def gerar_modelos():
    for caso in CASOS_MODELOS:
        yield pytest.param(
                                caso,
                                id=caso["modelo"].__name__,
                            )

def gerar_invalidos():
    for caso in CASOS_MODELOS:
        modelo = caso["modelo"]

        for invalido in caso["invalidos"]:
            yield pytest.param(
                                    caso,
                                    invalido,
                                    id=(
                                        f"{modelo.__name__}-"
                                        f"{invalido['campo']}-"
                                        f"{invalido['descricao']}"
                                    ),
                                )

def gerar_obrigatorios():
    for caso in CASOS_MODELOS:
        modelo = caso["modelo"]

        for campo, info in modelo.model_fields.items():
            if info.is_required():
                yield pytest.param(
                                        caso,
                                        campo,
                                        id=f"{modelo.__name__}-{campo}-obrigatorio",
                                    )

def aplicar_invalido(dados_validos, invalido):
    dados = deepcopy(dados_validos)

    operacao = invalido.get("operacao", "alterar")
    campo = invalido["campo"]

    if operacao in ("alterar", "adicionar"):
        dados[campo] = invalido["valor"]

    elif operacao == "remover":
        dados.pop(campo)

    else:
        raise ValueError(
                            f"Operação não suportada: {operacao}"
                        )

    return dados

@pytest.mark.parametrize("caso", gerar_modelos())
def test_modelo_valido(caso):
    modelo = caso["modelo"]
    dados = caso["valido"]

    instancia = modelo.model_validate(dados)

    assert isinstance(instancia, modelo)

@pytest.mark.parametrize("caso, invalido", gerar_invalidos(),)
def test_modelo_invalido(caso, invalido):
    modelo = caso["modelo"]

    dados = aplicar_invalido(
                                caso["valido"],
                                invalido,
                            )

    modelo.model_validate(caso["valido"])

    with pytest.raises(ValidationError) as exc:
        modelo.model_validate(dados)

    erros = exc.value.errors()

    campo_esperado = invalido["campo"]

    assert any(
                    erro["loc"] == (campo_esperado,)
                    for erro in erros
                ), (
                    f"Esperado erro no campo {campo_esperado}. "
                    f"Erros encontrados: {erros}"
                )

    if "tipo_erro" in invalido:
        assert any(
                        erro["loc"] == (campo_esperado,)
                        and erro["type"] == invalido["tipo_erro"]
                        for erro in erros
                    )

@pytest.mark.parametrize("caso, campo",gerar_obrigatorios(),)
def test_campos_obrigatorios(caso, campo):
    modelo = caso["modelo"]
    dados = caso["valido"].copy()

    dados.pop(campo)

    with pytest.raises(ValidationError) as exc:
        modelo.model_validate(dados)

    assert any(
                    erro["loc"] == (campo,)
                    and erro["type"] == "missing"
                    for erro in exc.value.errors()
                )

@pytest.mark.parametrize("caso", gerar_modelos())
def test_campos_extras(caso):
    modelo = caso["modelo"]
    dados = caso["valido"].copy()

    dados["campo_inexistente"] = "teste"

    with pytest.raises(ValidationError) as exc:
        modelo.model_validate(dados)

    assert any(
                erro["loc"] == ("campo_inexistente",)
                and erro["type"] == "extra_forbidden"
                for erro in exc.value.errors()
                )

if __name__ == "__main__":
    DIRETORIO_TESTES.mkdir(parents=True, exist_ok=True)
    raise SystemExit(
                        pytest.main([
                            __file__,
                            "-v",
                            "-s",
                            "--basetemp",
                            str(DIRETORIO_TESTES / "temporarios"),
                            "--junitxml",
                            str(DIRETORIO_TESTES / "resultado_validador.xml")
                        ])
                    )