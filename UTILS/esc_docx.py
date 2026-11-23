import os, re, pandas as pd
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_PARAGRAPH_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION_START
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from UTILS import monitor_completo  
import streamlit as st


@monitor_completo(st.session_state.LOGGER)
def exportar_texto(caminho: str, nm: str, texto: str, sobrescrever: bool = True):

    if not os.path.exists(caminho):
        os.makedirs(caminho, exist_ok=True)

    arquivo = os.path.join(caminho, nm)
    modo = "w" if sobrescrever else "a"

    if not sobrescrever:
        texto = "\n" + texto

    with open(arquivo, modo, encoding="utf-8") as f:
        f.write(texto)

    return "OK"