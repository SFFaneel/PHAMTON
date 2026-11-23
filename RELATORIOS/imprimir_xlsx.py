import xlsxwriter, os
import pandas as pd, streamlit as st
from pathlib import Path
import numpy as np
from UTILS import (
                        ams_lcmto,
                        bsc_cd_TODOS, 
                        imp_tbl_forma_000,
                        imp_tbl_forma_003,
                        existe_tabela,
                        max_arq
                    )
from dateutil.relativedelta import relativedelta
from datetime import datetime
import datetime as diadt
from pandas.tseries.offsets import DateOffset
from xlsxwriter.utility import xl_col_to_name

def ax_escreve_excel_md2(
                            worksheet, df, linhasAMAIS,
                            formatos=None, colunas_largura=None,
                            texto=None, titulo=None,
                            rows=[[], []], formato=None, st=None
                        ):
    if st:
        bar = st.progress(0, f"Construindo aba {worksheet.get_name()}...")

    max_larguras = {col: len(str(col_name)) for col, col_name in enumerate(df)}
    total_linhas = len(df)
    for row in range(total_linhas):
        if st and total_linhas > 0:
            bar.progress(row / total_linhas, f"Construindo aba {worksheet.get_name()}, linha {row + 1}/{total_linhas}...")

        for col, col_name in enumerate(df):
            cell_value = df.iloc[row, col]
            cell_format = texto
            if formatos:
                cell_format = next(
                    (fmt for cols, fmt in formatos.items() if col in cols),
                    texto
                )
            if row == 0:
                worksheet.write(row + linhasAMAIS, col + 2, col_name, titulo)
            if row in rows[0] and col not in rows[1]:
                worksheet.write(row + linhasAMAIS + 1, col + 2, cell_value, formato)
            else:
                worksheet.write(row + linhasAMAIS + 1, col + 2, cell_value, cell_format)
            valor_len = len(str(cell_value)) if cell_value is not None else 0
            if valor_len > max_larguras[col]:
                max_larguras[col] = valor_len

    for col, largura in max_larguras.items():
        worksheet.set_column(col + 2, col + 2, min(largura + 2, 50))

    if colunas_largura:
        for cols, width in colunas_largura.items():
            worksheet.set_column(*cols, width)

    if st:
        bar.empty()

    worksheet.hide_gridlines(2)
    return "Ok"

def ax_escreve_excel(worksheet, df, linhasAMAIS, formatos, colunas_largura, texto, titulo, rows = [[],[]], formato = None, st = None):
    if st: bar = st.progress(0, f"Construindo aba {worksheet.get_name()}...")
    for row in range(len(df)):
        bar.progress(row/int(len(df)), f"Construindo aba {worksheet.get_name()}...")
        for col, col_name in enumerate(df):
            cell_value = df.iloc[row, col]
            cell_format = next((fmt for cols, fmt in formatos.items() if col in cols), texto)

            if row == 0:
                worksheet.write(row + linhasAMAIS, col + 2, col_name, titulo)

            if row in rows[0] and col not in rows[1]:
                worksheet.write(row + linhasAMAIS + 1, col + 2, cell_value, formato)
            else:
                worksheet.write(row + linhasAMAIS + 1, col + 2, cell_value, cell_format)

    for cols, width in colunas_largura.items():
        worksheet.set_column(*cols, width)
    bar.empty()
    worksheet.hide_gridlines(2)
    return "Ok"

def imprime_icms(dir_arq_saida, Empresa, WACC_POND, WACC_MES,
                 VL_ICMS_NCRED, VL_ICMS_CRED, VP, BL_G125cmp1, BL_UN,
                 BL_G125, BL_G126, bd_EFD, st = None):
    if st:
        progresso = st.progress(0, text= 'Criando planilha...')
    workbook = xlsxwriter.Workbook(dir_arq_saida+'/Saida_ICMS_VF_' + Empresa + '.xlsx')
    

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 16,  'align':'center','bold': True})
    if st:
        progresso.progress(10, text= 'Criando planilha Resumo...')
    #Aba 1
    tabelas = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", con=bd_EFD)
    tabelas = tabelas['name'].tolist()
    cnpjs = [t.split('_')[-1] for t in tabelas if t.startswith('BLF_G110_')]
    cnpjs = sorted(set(cnpjs))

    for i, cnpj in enumerate(cnpjs):
        nome = "NI"
        if existe_tabela(f"BL_Z", bd_EFD):
            sSQL = f'SELECT "6" AS Nome FROM BL_Z WHERE "7" = "{cnpj}" LIMIT 1'
            df_NM = pd.read_sql(sSQL, con=bd_EFD)
            nome = df_NM.iloc[0]['Nome'] if not df_NM.empty else 'NI'
        progresso.progress(20, text="Buscando dados de cálculo...")
        if existe_tabela(f"BLF_G126_{cnpj}", bd_EFD):
            sSQL = f"SELECT * FROM BLF_G126_{cnpj}"
            BL_G126 = pd.read_sql(sSQL, con=bd_EFD)
        else:
            BL_G126 = pd.DataFrame()
        sSQL = f"SELECT * FROM tbl_icms_fin_{cnpj}"
        df = pd.read_sql(sSQL, con=bd_EFD)
        progresso.progress(40, text="Buscando dados G110...")
        sSQL = f"SELECT * FROM BLF_G110_{cnpj}"
        BL_G110 = pd.read_sql(sSQL, con=bd_EFD)
        progresso.progress(40, text="Buscando dados G125...")
        sSQL = f"SELECT * FROM BLF_G125_{cnpj}"
        BL_G125 = pd.read_sql(sSQL, con=bd_EFD)
        progresso.progress(60, text="Buscando dados memorial cálculo...")
        sSQL = f"SELECT * FROM BLF_G125cmp_{cnpj}"
        BL_G125cmp1 = pd.read_sql(sSQL, con=bd_EFD)
        progresso.progress(80, text="Buscando dados individuais...")
        sSQL = f"SELECT * FROM BLF_UN_{cnpj}"
        BL_UN = pd.read_sql(sSQL, con=bd_EFD)

        WACC_POND = df[df['Item']=='WACC Ponderado (%)'].iloc[-1,-1]/100
        WACC_MES = df[df['Item']=='i (%)'].iloc[-1,-1]/100,
        VL_ICMS_NCRED = df[df['Item']=='Cicms(NR) (R$)'].iloc[-1,-1]
        VL_ICMS_CRED = df[df['Item']=='Cicms(R) (R$)'].iloc[-1,-1]
        VP = df[df['Item']=='VP (R$)'].iloc[-1,-1]

        worksheet1 = workbook.add_worksheet(f'CALC_ICMS_NREC_{cnpj}'[-31:])
        worksheet2 = workbook.add_worksheet(f'DADOS_ABA_CALC_ICMS_NREC_{cnpj}'[-31:])
        worksheet3 = workbook.add_worksheet(f'REL_G110_{cnpj}'[-31:])
        worksheet4 = workbook.add_worksheet(f'REL_G125_{cnpj}'[-31:])
        if len(BL_G126)>0:
            worksheet5 = workbook.add_worksheet(f'REL_G126_{cnpj}'[-31:])

        worksheet1.merge_range('C5:D5', f'CÁLCULO PROVISÓRIO {Empresa} - {cnpj}, {nome}', tituloP)
        worksheet1.write(6, 2,'ITEM',titulo)
        worksheet1.write(6, 3,'VALOR',titulo)
        worksheet1.write(7, 2,'WACC',texto)
        worksheet1.write(7, 3, WACC_POND,percentual_format)
        worksheet1.write(8, 2,'i',texto)
        worksheet1.write(8, 3, WACC_MES[0],percentual_format)
        worksheet1.write(9, 2,'Cicms(NR)',texto)
        worksheet1.write(9, 3, VL_ICMS_NCRED,currency_format)
        worksheet1.write(10, 2,'Cicms(R)',texto)
        worksheet1.write(10, 3, VL_ICMS_CRED,currency_format)
        worksheet1.write(11, 2,'VP (Cicms(NR)+(Cicms(R)/(n*i))*(1/((1+i)))+n*/i-1)',texto)
        worksheet1.write(11, 3, VP,currency_format)

        worksheet1.set_column(2,2, 38)
        worksheet1.set_column(3,3, 18)
        worksheet1.hide_gridlines(2)

        #Aba 2
        if st:
            progresso.progress(30, text= 'Criando planilha Memorial de Cálculo...')
        lst_nomes=['CD_TB_ICMS', 'DT_INI', 'COEF_CRED_EST', 'Tx_WACC',
            'VL_SALDO_AMT', 'VL_SALDO_RED', 'VL_SALDO_ACUMULADO','VL_ICMS_CREDIT',
            'VL_ICMS_CRED', 'VL_ICMS_NCRED']

        BL_DFimp=BL_G125cmp1[lst_nomes].copy()

        #Cálculo do valor do ICMC.columns.values.tolist()
        BL_DFimp = BL_DFimp.fillna(0)
        linhasAMAIS=6
        worksheet2.merge_range('C5:L5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)

        # Mapeamento de formatos para colunas específicas
        formatos = {
            range(4, len(lst_nomes)): currency_format,  # Colunas > 3
            (3,): percentual_format,  # Coluna 3
            (1,): data_format  # Coluna 1
        }
        # Configuração otimizada de largura de colunas
        colunas_largura = {
            (6, 11): 20, (5, 5): 7.5, (2, 4): 12.5
        }
        
        x2 = ax_escreve_excel(worksheet2, BL_DFimp, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
        
        #Aba 3
        if st:
            progresso.progress(50, text= 'Criando planilha com dados G110...')
        
        BL_UN = BL_UN.fillna(0)
        BL_UN.sort_values(by=['DT_INI','DT_FIM'],inplace=True)
        worksheet3.merge_range('C5:P5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
        # Mapeamento de formatos para colunas específicas
        formatos = {
            (3, 4, 5, 6, 8, 9, 10, 11, 12, 13): currency_format,
            (7,): percentual_format,
            (1, 2): data_format
        }
        # Configuração otimizada de largura de colunas
        colunas_largura = {
            (2, 2): 4, (3, 4): 8.5, (5, 8): 15, (9, 9): 10, (10, 15): 20
        }
        x3 = ax_escreve_excel(worksheet3, BL_UN, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)

        #Aba 4
        if st:
            progresso.progress(70, text= 'Criando planilha com dados G125...')

        BL_G125 = BL_G125.fillna(0)
        BL_G125.sort_values(by=['DT_INI','DT_MOV'],inplace=True)
        worksheet4.merge_range('C5:O5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)

        # Definição de formatos para colunas específicas
        formatos = {
            (4, 5, 6, 7, 9): currency_format,
            (2, 10): data_format
        }
        # Configuração otimizada de largura de colunas
        colunas_largura = {
            (2, 2): 4, (3, 5): 11, (6, 12): 15, (13, 13): 21, (14, 14): 60
        }

        x4 = ax_escreve_excel(worksheet4, BL_G125, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
        
        #Aba 5
        if len(BL_G126) !=0:
            BL_G126=BL_G126.fillna(0)
            worksheet5.merge_range('C5:O5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
            # Definição de formatos para colunas específicas
            formatos = {
                (4, 5, 6, 7, 9): currency_format,
                (2, 10): data_format
            }

            # Configuração otimizada de largura de colunas
            colunas_largura = {
                (2, 2): 4, (3, 5): 11, (6, 12): 15, (13, 13): 21, (14, 14): 60
            }

            x5 = ax_escreve_excel(worksheet5, BL_G126, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
        
    if st:
        progresso.progress(100, text= f"Finalizada a exportação para: {dir_arq_saida}/Saida_ICMS_VF_{Empresa}.xlsx!")
    workbook.close()
    return None

def imprime_lado_AvsB(dir_arq_saida, Empresa, df1p1, con, st=None):
    """
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    Usa a biblioteca xlsxwriter para criar um arquivo Excel. um objeto Workbook é criado usando a classe
    xlsxwriter.Workbook. Ele recebe um argumento que é o caminho do arquivo de saída. 
    O dicionário {'nan_inf_to_errors': True} é opcional e define um comportamento específico para lidar
    com valores NaN (não é um número) e infinitos durante a gravação do arquivo.
    O método use_zip64() é chamado no objeto workbook. Ele é usado para habilitar o suporte a arquivos 
    ZIP64, que é necessário quando o arquivo Excel a ser criado é grande demais para ser armazenado em
    um arquivo ZIP tradicional.

    São criadas planilhas para escrita dos resultados
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    """
    file_name = f'{dir_arq_saida}/LADO_A_vs_B_{Empresa}.xlsx'
    workbook = xlsxwriter.Workbook(file_name, {'nan_inf_to_errors': True})
    workbook.use_zip64()

    worksheet1 = workbook.add_worksheet('ANL_LADO_A_vs_B')
    wb2 = workbook.add_worksheet('ANL_LADO_A_vs_B_SUN')
    wb3 = workbook.add_worksheet('ROA_UC_ABC')
    

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})

    formato1 = workbook.add_format({'bg_color': '#FFC7CE',
                                   'font_color': '#9C0006'})

    formato2 = workbook.add_format({'bg_color': '#C6EFCE',
                                   'font_color': '#006100'})


    def formato_def(df):
        formatos = {}
        lst_txt = []
        lst_moe = []
        lst_num = []
        lst_dt = []
        lst_pct = []
        for col, n in enumerate(df.columns):
            if n[:3].upper() in ['COD','TXT', 'CD_', 'FLG', 'TIP', 'CHV', 'CNP','DESC','UNI','NM_']:
                lst_txt.append(col)
            elif n[:3].upper() in ['VL_','FC','FC_', 'DEL', 'DIF']:
                lst_moe.append(col)
            elif n[:3].upper() in ['QTD', 'CST', 'IND', 'NUM', 'ID_', 'SER']:
                lst_num.append(col)
            elif n[:3].upper() in ['DT_']:
                lst_dt.append(col)
            elif n[:3].upper() in ['ALI','PCT']:
                lst_pct.append(col)
        if len(lst_txt)>0:
            formatos[tuple(lst_txt)] = texto
        if len(lst_moe)>0:
            formatos[tuple(lst_moe)] = currency_format
        if len(lst_num)>0:
            formatos[tuple(lst_num)] = number_format
        if len(lst_dt)>0:
            formatos[tuple(lst_dt)] = data_format
        if len(lst_pct)>0:
            formatos[tuple(lst_pct)] = percentual_format
        return formatos
    
    def realce_col(worksheet = None, lista = [], df = None, colunas = []):
        tam = 9 + len(df)
        for l, lst in enumerate(lista):
            worksheet.write(l,70,lst)
        int_val = f"$BS$1:$BS${len(lista)}"
    
        for letra in colunas:
            intervalo = f'{letra}10:{letra}{tam}'
            base = f'MATCH({letra}10, {int_val}, 0)'
            worksheet.conditional_format( intervalo, {
                'type':     'formula',
                'criteria': f'=ISNUMBER({base})',
                'format':   formato2
            })
            worksheet.conditional_format( intervalo, {
                'type':     'formula',
                'criteria': f'=ISNA({base})',
                'format':   formato1
            })

    linhasAMAIS=8
    
    
    worksheet1.merge_range('C5:AA5', 'CÁLCULO PROVISÓRIO ' + Empresa, tituloP)
    lst_nomes = ['Nr_TUC', 'UNID_AIS', 'QTD_AIC_ANT', 'QTD_ALM_ANT', 'QTD_REF', 'QTD_CMP', 'QTD_TURN', 
                   'QTD_REAP', 'QTD_INC', 'QTD_DOA', 'QTD_AIC_AT', 'QTD_ALM_AT', 'QTD_INCR', 'UNID_INCR', 
                   'QTD_ROA', 'UNID_ROA', 'QTD_AO', 'UNID_AO', 'QTD_INCRinc', 'UNID_INCRinc', 'QTD_INCRdoa', 
                   'UNID_INCRdoa', 'QTD_REFa', 'UNID_REF', 'QTD_EC', 'UNID_EC', 'QTD_ROA_AIC_ANT', 
                   'UNID_AIC_ANT', 'QTD_ROA_AIC_AT', 'UNID_AIC_AT', 'QTD_LADO_A', 'QTD_LADO_B', 'DELTA', 
                   'OBS_SFF_ORI_vs_ROA', 'OBS_SFF_ORI_vs_ROA_QTD', 'OBS_SFF_ORI_vs_INC_QTD', 'OBS_SFF_ORI_vs_AO_QTD', 
                   'OBS_SFF', 'OBS_SFF_ORI_vs_INCRinc_QTD', 'OBS_SFF_incorp', 'OBS_SFF_ORI_vs_INCRdoa_QTD', 'OBS_SFF_doa', 
                   'OBS_SFF_ORI_vs_REF_QTD', 'OBS_SFF_ref', 'OBS_SFF_ORI_vs_EC_QTD', 'OBS_SFF_ec', 
                   'OBS_SFF_ORI_vs_AIC_ANT_QTD', 'OBS_SFF_AIC_ANT', 'OBS_SFF_ORI_vs_AIC_AT_QTD', 'OBS_SFF_AIC_AT']
    df1p1 = df1p1[lst_nomes]
    
    linhasAMAIS=8
    worksheet1.write(linhasAMAIS-1, 2,'Análise Lado A vs Lado B', titulo2)
    for row in range(len(df1p1)):
        for col in range(len(lst_nomes)):
            if row==0:
                worksheet1.write(row+linhasAMAIS, col+2,lst_nomes[col],titulo)
            if col in [2,3,4,5,6,7,8,9,10,11,12,14,16,18,20,22,24,26,28,30,31,32]:
                worksheet1.write(row+linhasAMAIS+1, col+2,df1p1.iloc[row,col],number_format)
            else:
                worksheet1.write(row+linhasAMAIS+1, col+2,df1p1.iloc[row,col],texto)
        worksheet1.write_formula(row+linhasAMAIS+1, 34,'=AG' + str(row+linhasAMAIS+2) + '-AH' + str(row+linhasAMAIS+2),number_format)
        worksheet1.write_formula(row+linhasAMAIS+1, 32,'=sum(E' + str(row+linhasAMAIS+2) + ':L' + str(row+linhasAMAIS+2) + ')',number_format)
        worksheet1.write_formula(row+linhasAMAIS+1, 33,'=M' + str(row+linhasAMAIS+2) + '+N' + str(row+linhasAMAIS+2) + '+O' + str(row+linhasAMAIS+2),number_format)
    worksheet1.set_column(2,34, 15)
    worksheet1.set_column(3,3, 41)
    worksheet1.set_column(35,51, 70)
    worksheet1.hide_gridlines(2)

    worksheet1.conditional_format('AI10:AI'+str(9+len(df1p1)), {'type': 'cell',
                                             'criteria': '<=',
                                             'value': 0,
                                             'format': formato1})

    worksheet1.conditional_format('AI10:AI'+str(9+len(df1p1)), {'type': 'cell',
                                             'criteria': '>',
                                             'value': 0,
                                             'format': formato2})         

    df1 = df1p1.groupby(by='Nr_TUC')[['QTD_AIC_ANT', 'QTD_ALM_ANT', 'QTD_REF', 'QTD_CMP', 'QTD_TURN', 
                   'QTD_REAP', 'QTD_INC', 'QTD_DOA', 'QTD_AIC_AT', 'QTD_ALM_AT', 'QTD_INCR',
                   'QTD_LADO_A', 'QTD_LADO_B', 'DELTA']].sum().reset_index()
    lst_nomes = df1.columns.to_list()

    wb2.write(linhasAMAIS-1, 2,'Análise Lado A vs Lado B, SEM UNIDADE', titulo2)
    for row in range(len(df1)):
        for col in range(len(lst_nomes)):
            if row==0:
                wb2.write(row+linhasAMAIS, col+2,lst_nomes[col],titulo)
            if col in [1,2,3,4,5,6,7,8,9,10,11,12,13,14]:
                wb2.write(row+linhasAMAIS+1, col+2,df1.iloc[row,col],number_format)
            else:
                wb2.write(row+linhasAMAIS+1, col+2,df1.iloc[row,col],texto)
        wb2.write_formula(row+linhasAMAIS+1, 16,'=P' + str(row+linhasAMAIS+2) + '-O' + str(row+linhasAMAIS+2),number_format)
        wb2.write_formula(row+linhasAMAIS+1, 14,'=sum(D' + str(row+linhasAMAIS+2) + ':K' + str(row+linhasAMAIS+2) + ')',number_format)
        wb2.write_formula(row+linhasAMAIS+1, 15,'=M' + str(row+linhasAMAIS+2) + '+N' + str(row+linhasAMAIS+2) + '+L' + str(row+linhasAMAIS+2),number_format)
    wb2.set_column(2,34, 15)
    wb2.hide_gridlines(2)

    wb2.conditional_format('Q10:Q'+str(9+len(df1)), {'type': 'cell',
                                             'criteria': '<=',
                                             'value': 0,
                                             'format': formato2})

    wb2.conditional_format('Q10:Q'+str(9+len(df1)), {'type': 'cell',
                                             'criteria': '>',
                                             'value': 0,
                                             'format': formato1})

    df1 = pd.read_sql("SELECT * FROM Tst_ABC_ROA", con)
    lst_nomes = df1.columns.to_list()

    wb3.write(linhasAMAIS-1, 2,'Sumário ROA', titulo2)
    for row in range(len(df1)):
        for col in range(len(lst_nomes)):
            if row==0:
                wb3.write(row+linhasAMAIS, col+2,lst_nomes[col],titulo)
            if col in [1,2,3,5]:
                wb3.write(row+linhasAMAIS+1, col+2,df1.iloc[row,col],number_format)
            else:
                wb3.write(row+linhasAMAIS+1, col+2,df1.iloc[row,col],texto)
    
    wb3.set_column(2,34, 15)
    wb3.hide_gridlines(2)

    for nm_tbl in ["TB_INCR_RESUMO_LADO_A", "TB_AO_LADO_A", "TB_ROA_LADO_A", "TB_REF_LADO_A", "TB_EC_LADO_A",
                       "TB_ROAaicANT_RESUMO_LADO_A", "TB_ROAaicAT_RESUMO_LADO_A"]:
        nm_AX = nm_tbl.split("_")[1]
        TX_DES = imp_tbl_forma_000(nm_tbl=nm_tbl, con=con, st=st, lst_cnv=[], workbook = workbook)
        if not TX_DES.empty:
            wb4 = workbook.add_worksheet(f'EXT_{nm_AX}')
            wb4.merge_range('C5:G5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
            wb4.write(linhasAMAIS-1, 2, f'Tabela com o extrato do arquivo {nm_AX}',titulo2)
            formatos = formato_def(TX_DES)
            x1 = ax_escreve_excel_md2(wb4, TX_DES, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

    workbook.close()
    return "OK"

def excel_style(row, col):
    result = [] 
    LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    while col:
        col, rem = divmod(col-1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row)


def excel_col(col):
    result = []
    LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    while col:
        col, rem = divmod(col-1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result)

def imprimi_F0_BP(dir_arq_saida, con, Empresa, st=None):
    if st:
        avl = st.progress(0, "Iniciando exportação para excel...")

    dir_temp = Path(rf'{dir_arq_saida}/temp_excel')
    dir_temp.mkdir(parents=True, exist_ok=True)
    workbook = xlsxwriter.Workbook(
                                    rf'{dir_arq_saida}/Saida_BP_F0.xlsx',
                                    {"nan_inf_to_errors": True,
                                        "tmpdir": str(dir_temp)})
    
    worksheet1 = workbook.add_worksheet('NFe_SINTETICA')
    worksheet2 = workbook.add_worksheet('NFe_SINTETICA_CFOP')
    

    workbook.set_calc_mode('auto')
    workbook.use_zip64()

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'right'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 16,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})

    linhasAMAIS=8
    if st: avl.progress(40, "Criando aba com resultado da conciliação, perspectiva ERP...")

    if existe_tabela('TBL_BP_EC_CONC', con):
        SQLq = f"""
                    SELECT *
                    FROM TBL_BP_EC_CONC;   
                """
        TBL_BP_EC_CONC = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo TBL_BP_EC_CONC da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo TBL_BP_EC_CONC da base local.')

    lst_CNTn=['QTD','ALI','VL_']
    for n in TBL_BP_EC_CONC.columns:
        if TBL_BP_EC_CONC[n].dtype == 'object' and n[:3] in lst_CNTn:
            TBL_BP_EC_CONC[n] = pd.to_numeric(TBL_BP_EC_CONC[n].astype(str).str.replace(',','.'), 
                                                        errors='coerce',
                                                        downcast='float')

    
    worksheet2.merge_range('C5:O5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)

    ERP = (TBL_BP_EC_CONC[TBL_BP_EC_CONC['CHV_NFE'].notnull()]
           .groupby(['CHV_NFE','Cd_CFOP'])[['QTD','VL_TOT_ICMS','VL_TOT_IPI','VL_ST','VL_ITEM']]
           .sum()
           .reset_index()
           )
    ERP['VL_ITEM_TOTAL'] = (ERP['VL_TOT_ICMS'] +
                            ERP['VL_TOT_IPI'] +
                            ERP['VL_ST'] +
                            ERP['VL_ITEM'])
    EFD = (TBL_BP_EC_CONC[TBL_BP_EC_CONC['CHV_NFE_EFD'].notnull()]
           .groupby(['CHV_NFE_EFD', 'Cd_CFOP_EFD'])[['QTD_EFD','VL_ITEM_EFD']]
           .sum()
           .reset_index()
           .rename(columns={'CHV_NFE_EFD':'CHV_NFE', 'Cd_CFOP_EFD':'Cd_CFOP'})
           )
    
    compE = ERP.merge(EFD, how='outer', suffixes = ("_ERP","_EFD"), indicator=True, on = ['CHV_NFE','Cd_CFOP'])

    map_res = {
                    'both' : 'NO',
                    'left_only' : 'Pelos dados infomados no ERP, não foi possível encontrar candidatos no EFD, verifique',
                    'right_only' : 'Pelos dados infomados no EFD, não foi possível encontrar candidatos no ERP, verifique',
                }
    compE['IND_CONC'] = compE['_merge'].replace(map_res)
    compE = compE.drop(columns='_merge')
    compE['FLG_CRIT'] = compE['Cd_CFOP'].str[1:].isin(['406', '551', '553', '555'])
    compE['OBS_SFF'] = np.where(
                                    compE['IND_CONC'] == "NO",
                                    np.where(
                                        np.isclose(
                                                        compE['VL_ITEM_EFD'],
                                                        compE['VL_ITEM_TOTAL'],
                                                        rtol=0.0001
                                                    ),
                                        "NO",
                                        "Justificar porque não conciliou em valor"
                                    ),
                                    "Verificar Extrato de Compras"
                                )
    for n in ['QTD','VL_TOT_ICMS','VL_TOT_IPI','VL_ST','VL_ITEM','VL_ITEM_TOTAL','QTD_EFD','VL_ITEM_EFD']:
        compE[n] = compE[n].fillna(0)

    formatos = {}
    lst_txt = []
    lst_moe = []
    lst_num = []
    lst_dt = []
    lst_pct = []
    for col, n in enumerate(compE.columns):
        if n[:3].upper() in ['COD','TXT', 'CD_', 'FLG', 'TIP', 'CHV', 'CNP','DESC','UNI','NM_']:
            lst_txt.append(col)
        elif n[:3].upper() in ['VL_']:
            lst_moe.append(col)
        elif n[:3].upper() in ['QTD', 'CST', 'IND', 'NUM', 'ID_', 'SER']:
            lst_num.append(col)
        elif n[:3].upper() in ['DT_']:
            lst_dt.append(col)
        elif n[:3].upper() in ['ALI']:
            lst_pct.append(col)
        
    if len(lst_txt)>0:
        formatos[tuple(lst_txt)] = texto
    if len(lst_moe)>0:
        formatos[tuple(lst_moe)] = currency_format
    if len(lst_num)>0:
        formatos[tuple(lst_num)] = number_format
    if len(lst_dt)>0:
        formatos[tuple(lst_dt)] = data_format
    if len(lst_pct)>0:
        formatos[tuple(lst_pct)] = percentual_format

    x1 = ax_escreve_excel_md2(worksheet2, compE, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

    worksheet1.merge_range('C5:O5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    ERP = (TBL_BP_EC_CONC[TBL_BP_EC_CONC['CHV_NFE'].notnull()]
           .groupby('CHV_NFE')[['QTD','VL_TOT_ICMS','VL_TOT_IPI','VL_ST','VL_ITEM']]
           .sum()
           .reset_index()
           )
    ERP['VL_ITEM_TOTAL'] = (ERP['VL_TOT_ICMS'] +
                            ERP['VL_TOT_IPI'] +
                            ERP['VL_ST'] +
                            ERP['VL_ITEM'])
    EFD = (TBL_BP_EC_CONC[TBL_BP_EC_CONC['CHV_NFE_EFD'].notnull()]
           .groupby('CHV_NFE_EFD')[['QTD_EFD','VL_ITEM_EFD']]
           .sum()
           .reset_index()
           .rename(columns={'CHV_NFE_EFD':'CHV_NFE'})
           )
    
    compE = ERP.merge(EFD, how='outer', suffixes = ("_ERP","_EFD"), indicator=True, on = 'CHV_NFE')

    map_res = {
                    'both' : 'NO',
                    'left_only' : 'Pelos dados infomados no ERP, não foi possível encontrar candidatos no EFD, verifique',
                    'right_only' : 'Pelos dados infomados no EFD, não foi possível encontrar candidatos no ERP, verifique',
                }
    compE['IND_CONC'] = compE['_merge'].replace(map_res)
    compE = compE.drop(columns='_merge')
    compE['OBS_SFF'] = np.where(
                                    compE['IND_CONC'] == "NO",
                                    np.where(
                                        np.isclose(
                                            compE['VL_ITEM_EFD'],
                                            compE['VL_ITEM_TOTAL'],
                                            rtol=0.0001
                                        ),
                                        "NO",
                                        "Justificar porque não conciliou em valor"
                                    ),
                                    "Verificar extração de dados"
                                )
    for n in ['QTD','VL_TOT_ICMS','VL_TOT_IPI','VL_ST','VL_ITEM','VL_ITEM_TOTAL','QTD_EFD','VL_ITEM_EFD']:
        compE[n] = compE[n].fillna(0)

    formatos = {}
    lst_txt = []
    lst_moe = []
    lst_num = []
    lst_dt = []
    lst_pct = []
    for col, n in enumerate(compE.columns):
        if n[:3].upper() in ['COD','TXT', 'CD_', 'FLG', 'TIP', 'CHV', 'CNP','DESC','UNI','NM_']:
            lst_txt.append(col)
        elif n[:3].upper() in ['VL_']:
            lst_moe.append(col)
        elif n[:3].upper() in ['QTD', 'CST', 'IND', 'NUM', 'ID_', 'SER']:
            lst_num.append(col)
        elif n[:3].upper() in ['DT_']:
            lst_dt.append(col)
        elif n[:3].upper() in ['ALI']:
            lst_pct.append(col)
        
    if len(lst_txt)>0:
        formatos[tuple(lst_txt)] = texto
    if len(lst_moe)>0:
        formatos[tuple(lst_moe)] = currency_format
    if len(lst_num)>0:
        formatos[tuple(lst_num)] = number_format
    if len(lst_dt)>0:
        formatos[tuple(lst_dt)] = data_format
    if len(lst_pct)>0:
        formatos[tuple(lst_pct)] = percentual_format

    x1 = ax_escreve_excel_md2(worksheet1, compE, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

    TBL_BP_EC_CONC = TBL_BP_EC_CONC.fillna(0)
    TBL_BP_EC_CONC['DT_AX'] = pd.to_datetime(TBL_BP_EC_CONC['DT_DOC'].astype(str), format="%Y-%m-%d", errors='coerce')
    TBL_BP_EC_CONC['DT_AX1'] = pd.to_datetime(TBL_BP_EC_CONC['Dt_NF'].astype(str), format="%Y-%m-%d", errors='coerce')

    crt = TBL_BP_EC_CONC['DT_AX1'].dt.date.between(st.session_state.dt_ini,st.session_state.dt_fim) | TBL_BP_EC_CONC['DT_AX'].dt.date.between(st.session_state.dt_ini,st.session_state.dt_fim)
    TBL_BP_EC_CONC = TBL_BP_EC_CONC[crt]
    TBL_BP_EC_CONC = TBL_BP_EC_CONC.drop(columns=['DT_AX','DT_AX1'])

    formatos = {}
    lst_txt = []
    lst_moe = []
    lst_num = []
    lst_dt = []
    lst_pct = []
    for col, n in enumerate(TBL_BP_EC_CONC.columns):
        if n[:3].upper() in ['COD','TXT', 'CD_', 'FLG', 'TIP', 'CHV', 'CNP','DESC','UNI','NM_']:
            lst_txt.append(col)
        elif n[:3].upper() in ['VL_']:
            lst_moe.append(col)
        elif n[:3].upper() in ['QTD', 'CST', 'IND', 'NUM', 'ID_', 'SER']:
            lst_num.append(col)
        elif n[:3].upper() in ['DT_']:
            lst_dt.append(col)
        elif n[:3].upper() in ['ALI']:
            lst_pct.append(col)
        
    if len(lst_txt)>0:
        formatos[tuple(lst_txt)] = texto
    if len(lst_moe)>0:
        formatos[tuple(lst_moe)] = currency_format
    if len(lst_num)>0:
        formatos[tuple(lst_num)] = number_format
    if len(lst_dt)>0:
        formatos[tuple(lst_dt)] = data_format
    if len(lst_pct)>0:
        formatos[tuple(lst_pct)] = percentual_format

    batch_size = 750000
    for i, start in enumerate(range(0, len(TBL_BP_EC_CONC), batch_size)):
        df_batch = TBL_BP_EC_CONC.iloc[start : start + batch_size]
        ws = workbook.add_worksheet(f'EC_AVAL_P{i+1}')
        ws.merge_range('C5:O5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
        
        x1 = ax_escreve_excel_md2(ws, df_batch, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

    
    
    if st: avl.progress(98, "Salvando...")
    workbook.close()
    if st: avl.progress(100, f"Finalizado e salvo em {dir_arq_saida}/Saida_BP_F0.xlsx!")
    return "OK"

def imprimi_F1_BP(dir_arq_saida, con, bd_EFD, Empresa, D1, D2, FLG_ARQ, st=None):
    if st: avl = st.progress(0, "Iniciando exportação para excel...")

    dir_temp = Path(rf'{dir_arq_saida}/temp_excel')
    dir_temp.mkdir(parents=True, exist_ok=True)
    workbook = xlsxwriter.Workbook(
                                    rf'{dir_arq_saida}/Saida_BP_F1.xlsx',
                                    {"nan_inf_to_errors": True,
                                        "tmpdir": str(dir_temp)})

    workbook.use_zip64()
    worksheet2 = workbook.add_worksheet('EC')
    worksheet8 = workbook.add_worksheet('EC_OUTLIERS')
    worksheet3 = workbook.add_worksheet('EC_UC_UAR_BASE')
    worksheet4 = workbook.add_worksheet('VF_DESCR_ITEM')
    worksheet7 = workbook.add_worksheet('BC_VF_UC')
    worksheet6 = workbook.add_worksheet('BC_VF_ITEM')
    worksheet5 = workbook.add_worksheet('tbl_FCOGE')
    workbook.set_calc_mode('auto')

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    number2_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8,  'align':'center', 'bottom':1})
    currency2_format = workbook.add_format({'bg_color':'#D9D9D9','num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})

    formato1 = workbook.add_format({'bg_color': '#FFC7CE',
                                   'font_color': '#9C0006'})
    formato2 = workbook.add_format({'bg_color': '#C6EFCE',
                                   'font_color': '#006100'})
    linhasAMAIS=8
    if st: avl.progress(25, "Criando aba com análise de outliers...")

    def formato_def(df):
        formatos = {}
        lst_txt = []
        lst_moe = []
        lst_num = []
        lst_dt = []
        lst_pct = []
        for col, n in enumerate(df.columns):
            if n[:3].upper() in ['COD','TXT', 'CD_', 'FLG', 'TIP', 'CHV', 'CNP','DESC','UNI','NM_']:
                lst_txt.append(col)
            elif n[:3].upper() in ['VL_','FC','FC_', 'DEL']:
                lst_moe.append(col)
            elif n[:3].upper() in ['QTD', 'CST', 'IND', 'NUM', 'ID_', 'SER']:
                lst_num.append(col)
            elif n[:3].upper() in ['DT_']:
                lst_dt.append(col)
            elif n[:3].upper() in ['ALI']:
                lst_pct.append(col)
            
        if len(lst_txt)>0:
            formatos[tuple(lst_txt)] = texto
        if len(lst_moe)>0:
            formatos[tuple(lst_moe)] = currency_format
        if len(lst_num)>0:
            formatos[tuple(lst_num)] = number_format
        if len(lst_dt)>0:
            formatos[tuple(lst_dt)] = data_format
        if len(lst_pct)>0:
            formatos[tuple(lst_pct)] = percentual_format
        return formatos
    
    worksheet8.merge_range('C5:AC5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet8.write(linhasAMAIS-1, 2,'Tabela do Extrato de Compras - OUTLIERS',titulo2)
    TAB_OUTLIERS =  imp_tbl_forma_000('TAB_OUTLIERS', con=con, st=st, 
                                      lst_cnv=['VL_IPI','VL_TOT_LIQ','VL_ICMS','QTD'], workbook=workbook) 

    TAB_OUTLIERS = TAB_OUTLIERS.fillna('ND')
    TAB_OUTLIERS = TAB_OUTLIERS.replace([np.inf, -np.inf], 0)
    formatos = formato_def(TAB_OUTLIERS)
    x1 = ax_escreve_excel_md2(worksheet8, TAB_OUTLIERS, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

    worksheet8.conditional_format('AB10:AB'+str(9+len(TAB_OUTLIERS)), {'type': 'cell',
                                             'criteria': 'between',
                                             'minimum': -((1.05**(D2.year-D1.year))-1),
                                             'maximum': ((1.05**(D2.year-D1.year))-1),
                                             'format': formato2})

    worksheet8.conditional_format('AB10:AB'+str(9+len(TAB_OUTLIERS)), {'type': 'cell',
                                             'criteria': 'not between',
                                             'minimum': -((1.05**(D2.year-D1.year))-1),
                                             'maximum': ((1.05**(D2.year-D1.year))-1),
                                             'format': formato1})
    if st: avl.progress(25, "Criando aba com EC...")
    
    BP_EC_AVALc =  imp_tbl_forma_000('BP_EC_AVALc', con=con, st=st,
                                     lst_cnv= ['VL_TOT_IPI','VL_TOT_LIQ','VL_TOT_ICMS','VL_ODC','VL_ICMS_FIN',
                                                'VL_ITEM','VL_DESC_NF','VL_ABAT_NT','Qtd','ALIQ_ICMS_EC','ALIQ_IPI_EC',
                                                'FLG_BPR','FLG_TP','FLG_TPNF','Cd_NG_ROA','Cd_NG_EC'],
                                     workbook = workbook)


    worksheet2.merge_range('C5:CE5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet2.write(linhasAMAIS-1, 2, 'Tabela do Extrato de Compras', titulo2)
    BP_EC_AVALc = BP_EC_AVALc.astype({col: 'float' for col in BP_EC_AVALc.select_dtypes(include=['float32']).columns})
    
    if len(BP_EC_AVALc) > 600000:
        BP_EC_AVALc = BP_EC_AVALc[BP_EC_AVALc['Cd_CFOP'].astype(str).str[1:].str.contains(r'406|551|553|555', na=False)]

    formatos = formato_def(BP_EC_AVALc)

    x2 = ax_escreve_excel_md2(worksheet2, BP_EC_AVALc, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)
    if st: avl.progress(50, "Criando aba com dados base do EC para cálculo do BP...")

    TAB_CALC_BP =  imp_tbl_forma_000('TAB_CALC_BP', con=con, st=st, workbook = workbook)
    worksheet3.merge_range('C5:AL5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet3.write(linhasAMAIS - 1, 2, 'Tabela do Extrato de Compras UC/UAR atualizado', titulo2)
    TAB_CALC_BP = TAB_CALC_BP.fillna('ND')
    formatos = formato_def(TAB_CALC_BP)
    x3 = ax_escreve_excel_md2(worksheet3, TAB_CALC_BP, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)
    if st:  avl.progress(75, "Criando aba com EC UC/UAR atualizado...")

    TAB_FIM =  imp_tbl_forma_000('TAB_FIM', con=con, st=st, workbook = workbook)
    worksheet4.merge_range('C5:R5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet4.write(linhasAMAIS - 1, 2, 'Tabela Resumo', titulo2)
    TAB_FIM = TAB_FIM.fillna(0)
    TAB_FIM = TAB_FIM.replace([np.inf, -np.inf], 0)
    formatos = formato_def(TAB_FIM)
    
    x4 = ax_escreve_excel_md2(worksheet4, TAB_FIM, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)
    worksheet4.conditional_format('R10:R'+str(9+len(TAB_FIM)), {'type': 'cell',
                                             'criteria': 'between',
                                             'minimum': -0.25,
                                             'maximum': 0.25,
                                             'format': formato2})

    worksheet4.conditional_format('R10:R'+str(9+len(TAB_FIM)), {'type': 'cell',
                                             'criteria': 'not between',
                                             'minimum': -0.25,
                                             'maximum': 0.25,
                                             'format': formato1})

    if st: avl.progress(85, "Criando aba com  itens do EC...")

    worksheet6.merge_range('C5:N5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet6.write(linhasAMAIS - 1, 2, 'Tabela Resumo', titulo2)
    TAB_COR_ITEM =  imp_tbl_forma_000('TAB_COR_ITEM', con=con, st=st, workbook = workbook)
    TAB_COR_ITEM = TAB_COR_ITEM.fillna('ND')
    TAB_COR_ITEM = TAB_COR_ITEM.replace([np.inf, -np.inf], 0)
    formatos = formato_def(TAB_COR_ITEM)
    x5 = ax_escreve_excel_md2(worksheet6, TAB_COR_ITEM, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

    if st: avl.progress(90, "Criando aba com  itens do EC por UC...")
    worksheet7.merge_range('C5:M5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet7.write(linhasAMAIS - 1, 2, 'Tabela Resumo', titulo2)
    TAB_FIM_BPC =  imp_tbl_forma_000('TAB_FIM_BPC', con=con, st=st, workbook = workbook)
    TAB_FIM_BPC = TAB_FIM_BPC.fillna('ND')
    TAB_FIM_BPC = TAB_FIM_BPC.replace([np.inf, -np.inf], 0)
    formatos = formato_def(TAB_FIM_BPC)
    x6 = ax_escreve_excel_md2(worksheet7, TAB_FIM_BPC, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

    if st: avl.progress(90, "Criando aba com indicadores FCOGE...")
    worksheet5.merge_range('C5:H5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet5.write(linhasAMAIS - 1, 2, 'Tabela Indicadores COGE', titulo2)
    tbl_FCOGE =  imp_tbl_forma_000('tbl_FCOGE', con=con, st=st, workbook = workbook)
    tbl_FCOGE = tbl_FCOGE.fillna('ND')
    formatos = formato_def(tbl_FCOGE)
    x7 = ax_escreve_excel_md2(worksheet5, tbl_FCOGE, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

    # Dados de apuração CIAP
    if st: avl.progress(91, "Criando abas com dados CIAP...")

    tabelas = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", con=bd_EFD)
    tabelas = tabelas['name'].tolist()
    cnpjs = [t.split('_')[-1] for t in tabelas if t.startswith('BLF_G110_')]
    cnpjs = sorted(set(cnpjs))

    for i, cnpj in enumerate(cnpjs):
        nome = "NI"
        if existe_tabela(f"BL_Z", bd_EFD):
            sSQL = f'SELECT "6" AS Nome FROM BL_Z WHERE "7" = "{cnpj}" LIMIT 1'
            df_NM = pd.read_sql(sSQL, con=bd_EFD)
            nome = df_NM.iloc[0]['Nome'] if not df_NM.empty else 'NI'
        avl.progress(90, text="Buscando dados de cálculo...")
        if existe_tabela(f"BLF_G126_{cnpj}", bd_EFD):
            sSQL = f"SELECT * FROM BLF_G126_{cnpj}"
            BL_G126 = pd.read_sql(sSQL, con=bd_EFD)
        else:
            BL_G126 = pd.DataFrame()
        sSQL = f"SELECT * FROM tbl_icms_fin_{cnpj}"
        df = pd.read_sql(sSQL, con=bd_EFD)

        avl.progress(91, text="Buscando dados do CIAP...")
        sSQL = f"SELECT * FROM BLF_G125_{cnpj}"
        BL_G125 = pd.read_sql(sSQL, con=bd_EFD)

        WACC_POND = df[df['Item']=='WACC Ponderado (%)'].iloc[-1,-1]/100
        WACC_MES = df[df['Item']=='i (%)'].iloc[-1,-1]/100,
        VL_ICMS_NCRED = df[df['Item']=='Cicms(NR) (R$)'].iloc[-1,-1]
        VL_ICMS_CRED = df[df['Item']=='Cicms(R) (R$)'].iloc[-1,-1]
        VP = df[df['Item']=='VP (R$)'].iloc[-1,-1]

        worksheetn1 = workbook.add_worksheet(f'CALC_ICMS_NREC_{cnpj}'[-31:])
        worksheetn4 = workbook.add_worksheet(f'REL_G125_{cnpj}'[-31:])
        if len(BL_G126)>0:
            worksheetn5 = workbook.add_worksheet(f'REL_G126_{cnpj}'[-31:])

        worksheetn1.merge_range('C5:D5', f'CÁLCULO PROVISÓRIO {Empresa} - {cnpj}, {nome}', tituloP)
        worksheetn1.write(6, 2,'ITEM',titulo)
        worksheetn1.write(6, 3,'VALOR',titulo)
        worksheetn1.write(7, 2,'WACC',texto)
        worksheetn1.write(7, 3, WACC_POND,percentual_format)
        worksheetn1.write(8, 2,'i',texto)
        worksheetn1.write(8, 3, WACC_MES[0],percentual_format)
        worksheetn1.write(9, 2,'Cicms(NR)',texto)
        worksheetn1.write(9, 3, VL_ICMS_NCRED,currency_format)
        worksheetn1.write(10, 2,'Cicms(R)',texto)
        worksheetn1.write(10, 3, VL_ICMS_CRED,currency_format)
        worksheetn1.write(11, 2,'VP (Cicms(NR)+(Cicms(R)/(n*i))*(1/((1+i)))+n*/i-1)',texto)
        worksheetn1.write(11, 3, VP,currency_format)

        worksheetn1.set_column(2,2, 38)
        worksheetn1.set_column(3,3, 18)
        worksheetn1.hide_gridlines(2)

        if st: avl.progress(92, text= 'Criando planilha com dados G125...')

        BL_G125 = BL_G125.fillna(0)
        BL_G125.sort_values(by=['DT_INI','DT_MOV'],inplace=True)
        worksheetn4.merge_range('C5:O5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
        formatos = formato_def(BL_G125)
        x6 = ax_escreve_excel_md2(worksheetn4, BL_G125, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

        if len(BL_G126) !=0:
            BL_G126=BL_G126.fillna(0)
            worksheetn5.merge_range('C5:O5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
            formatos = formato_def(BL_G126)
            x6 = ax_escreve_excel_md2(worksheetn5, BL_G126, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

    if st: avl.progress(100, f"Finalizado e guardado em {dir_arq_saida}/Saida_BP_F1.xlsx!")
    workbook.close()
    return "OK"

def imprimi_F2_BP(dir_arq_saida, con, Empresa, D1, D2, FLG_ARQ, st=None):
    if st:
        avl = st.progress(0, "Iniciando exportação para excel...")

    workbook = xlsxwriter.Workbook(f'{dir_arq_saida}/Saida_BP_F2.xlsx', {'nan_inf_to_errors': True})

    worksheet1 = workbook.add_worksheet('SÍNTESE')
    workbook.set_calc_mode('auto')
    workbook.use_zip64()

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    number2_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8,  'align':'center', 'bottom':1})
    currency2_format = workbook.add_format({'bg_color':'#D9D9D9','num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    # Vermelho claro com texto escuro.
    formato1 = workbook.add_format({'bg_color': '#FFC7CE',
                                   'font_color': '#9C0006'})

    # Fundo verde com texto escuro.
    formato2 = workbook.add_format({'bg_color': '#C6EFCE',
                                   'font_color': '#006100'})
    linhasAMAIS=8

    def formato_def(df):
        formatos = {}
        lst_txt = []
        lst_moe = []
        lst_num = []
        lst_dt = []
        lst_pct = []
        for col, n in enumerate(df.columns):
            if n[:3].upper() in ['COD','TXT', 'CD_', 'FLG', 'TIP', 'CHV', 'CNP','DESC','UNI','NM_']:
                lst_txt.append(col)
            elif n[:3].upper() in ['VL_','FC','FC_', 'DEL']:
                lst_moe.append(col)
            elif n[:3].upper() in ['QTD', 'CST', 'IND', 'NUM', 'ID_', 'SER']:
                lst_num.append(col)
            elif n[:3].upper() in ['DT_']:
                lst_dt.append(col)
            elif n[:3].upper() in ['ALI']:
                lst_pct.append(col)
            
        if len(lst_txt)>0:
            formatos[tuple(lst_txt)] = texto
        if len(lst_moe)>0:
            formatos[tuple(lst_moe)] = currency_format
        if len(lst_num)>0:
            formatos[tuple(lst_num)] = number_format
        if len(lst_dt)>0:
            formatos[tuple(lst_dt)] = data_format
        if len(lst_pct)>0:
            formatos[tuple(lst_pct)] = percentual_format
        return formatos
    
    if st: avl.progress(25, "Criando aba comparativa...")
    worksheet1.merge_range('C5:AC5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet1.write(linhasAMAIS-1, 2,'Tabela Resumo',titulo2)

    BP_COMP =  imp_tbl_forma_000('BP_COMP', con=con, st=st, workbook = workbook)
    BP_COMP = BP_COMP.fillna('ND')
    formatos = formato_def(BP_COMP)
    x1 = ax_escreve_excel_md2(worksheet1, BP_COMP, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

    worksheet1.conditional_format('AL10:AL' + str(len(BP_COMP) + linhasAMAIS + 1), {'type': 'cell',
                                             'criteria': '>=',
                                             'value': 0.2,
                                             'format': formato1})

    worksheet1.conditional_format('AL10:AL' + str(len(BP_COMP) + linhasAMAIS + 1), {'type': 'cell',
                                             'criteria': 'between',
                                             'minimum': -10,
                                             'maximum': 0.2,
                                             'format': formato2})

    worksheet1.conditional_format('AL10:AL' + str(len(BP_COMP) + linhasAMAIS + 1), {'type': 'cell',
                                             'criteria': 'not between',
                                             'minimum': -10,
                                             'maximum':0.2,
                                             'format': formato1})
    workbook.close()
    if st: avl.progress(100, f"Finalizado e guardado em {dir_arq_saida}/Saida_BP_F2.xlsx!")
    return "OK"

def imprimi_F3_BP(dir_arq_saida, con, Empresa, D1, D2, FLG_ARQ, st=None):
    if st:
        avl = st.progress(0, "Iniciando exportação para excel...")

    workbook = xlsxwriter.Workbook(f'{dir_arq_saida}/Saida_BP_F3.xlsx')

    worksheet1 = workbook.add_worksheet('TESTE_QTD')
    worksheet2 = workbook.add_worksheet('TESTE_QTD_UC')
    workbook.set_calc_mode('auto')
    workbook.use_zip64()

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    number2_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8,  'align':'center', 'bottom':1})
    currency2_format = workbook.add_format({'bg_color':'#D9D9D9','num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    # Vermelho claro com texto escuro.
    formato1 = workbook.add_format({'bg_color': '#FFC7CE',
                                   'font_color': '#9C0006'})

    # Fundo verde com texto escuro.
    formato2 = workbook.add_format({'bg_color': '#C6EFCE',
                                   'font_color': '#006100'})
    
    def formato_def(df):
        formatos = {}
        lst_txt = []
        lst_moe = []
        lst_num = []
        lst_dt = []
        lst_pct = []
        for col, n in enumerate(df.columns):
            if n[:3].upper() in ['COD','TXT', 'CD_', 'FLG', 'TIP', 'CHV', 'CNP','DESC','UNI','NM_']:
                lst_txt.append(col)
            elif n[:3].upper() in ['VL_','FC','FC_', 'DEL', 'DIF']:
                lst_moe.append(col)
            elif n[:3].upper() in ['QTD', 'CST', 'IND', 'NUM', 'ID_', 'SER']:
                lst_num.append(col)
            elif n[:3].upper() in ['DT_']:
                lst_dt.append(col)
            elif n[:3].upper() in ['ALI']:
                lst_pct.append(col)
            
        if len(lst_txt)>0:
            formatos[tuple(lst_txt)] = texto
        if len(lst_moe)>0:
            formatos[tuple(lst_moe)] = currency_format
        if len(lst_num)>0:
            formatos[tuple(lst_num)] = number_format
        if len(lst_dt)>0:
            formatos[tuple(lst_dt)] = data_format
        if len(lst_pct)>0:
            formatos[tuple(lst_pct)] = percentual_format
        return formatos
    
    linhasAMAIS=8
    if st: avl.progress(25, "Criando aba comparativa...")
    worksheet1.merge_range('C5:L5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet1.write(linhasAMAIS-1, 2,'Tabela com teste de quantidades (ROA vs EC vs SPED)',titulo2)
    CONSOL_TOT =  imp_tbl_forma_000('CONSOL_TOT_QTD_EC', con=con, st=st, workbook = workbook)
    CONSOL_TOT = CONSOL_TOT.fillna('ND')
    formatos = formato_def(CONSOL_TOT)
    x1 = ax_escreve_excel_md2(worksheet1, CONSOL_TOT, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

    for n in ['QTD_FIS','QTD_ERP']:
        if n in CONSOL_TOT and CONSOL_TOT[n].dtype == 'object':
            CONSOL_TOT[n] = pd.to_numeric(CONSOL_TOT[n].astype(str).str.replace(',','.'), 
                                                        errors='coerce',
                                                        downcast='float')
      
    CONSOL_TOTwb = CONSOL_TOT.groupby('Nr_TUC')[['QTD_FIS','QTD_ERP']].sum().reset_index()
    CONSOL_TOTwb = CONSOL_TOTwb[CONSOL_TOTwb['Nr_TUC']!=0]
    CONSOL_TOTwb['DIF'] = CONSOL_TOTwb['QTD_FIS']-CONSOL_TOTwb['QTD_ERP']
    CONSOL_TOTwb['TESTE'] = 'AVALIAR'
    CONSOL_TOTwb.loc[CONSOL_TOTwb['DIF'] < 1, 'TESTE'] = 'OK'

    if st: avl.progress(75, f"Exportando dados agrupados por UC...")

    worksheet2.merge_range('C5:G5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet2.write(linhasAMAIS-1, 2,'Tabela com teste de quantidades (ROA vs EC)',titulo2)
    formatos = formato_def(CONSOL_TOTwb)
    x2 = ax_escreve_excel_md2(worksheet2, CONSOL_TOTwb, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)
    workbook.close()
    if st: avl.progress(100, f"Finalizado e guardado em {dir_arq_saida}/Saida_BP_F3.xlsx!")

    return "OK"

def imprimi_F0_INCR(dir_arq_saida, con, Empresa, st=None):
    if st:
        avl = st.progress(0, "Iniciando exportação para excel...")

    dir_temp = Path(rf'{dir_arq_saida}/temp_excel')
    dir_temp.mkdir(parents=True, exist_ok=True)
    workbook = xlsxwriter.Workbook(
                                    rf'{dir_arq_saida}/Saida_INCR_F0.xlsx',
                                    {"nan_inf_to_errors": True,
                                    "tmpdir": str(dir_temp)})

    worksheet1 = workbook.add_worksheet('TST_VLR_INC_VS_ROS_VAL')
    worksheet2 = workbook.add_worksheet('TST_QTD_INC_VS_ROA_ITEM')
    worksheet3 = workbook.add_worksheet('TST_QTD_INC_AIS_ROA_UC_A1')
    worksheet4 = workbook.add_worksheet('TST_QTD_INC_AIS_ROA_PROJ_ITEM')
    workbook.set_calc_mode('auto')
    workbook.use_zip64()

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    number2_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8,  'align':'center', 'bottom':1})
    currency2_format = workbook.add_format({'bg_color':'#D9D9D9','num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})

    formato1 = workbook.add_format({'bg_color': '#FFC7CE',
                                   'font_color': '#9C0006'})

    formato2 = workbook.add_format({'bg_color': '#C6EFCE',
                                   'font_color': '#006100'})
    def formato_def(df):
        formatos = {}
        lst_txt = []
        lst_moe = []
        lst_num = []
        lst_dt = []
        lst_pct = []
        for col, n in enumerate(df.columns):
            if n[:3].upper() in ['COD','TXT', 'CD_', 'FLG', 'TIP', 'CHV', 'CNP','DESC','UNI','NM_']:
                lst_txt.append(col)
            elif n[:3].upper() in ['VL_','FC','FC_', 'DEL', 'DIF']:
                lst_moe.append(col)
            elif n[:3].upper() in ['QTD', 'CST', 'IND', 'NUM', 'ID_', 'SER']:
                lst_num.append(col)
            elif n[:3].upper() in ['DT_']:
                lst_dt.append(col)
            elif n[:3].upper() in ['ALI','PCT']:
                lst_pct.append(col)
        if len(lst_txt)>0:
            formatos[tuple(lst_txt)] = texto
        if len(lst_moe)>0:
            formatos[tuple(lst_moe)] = currency_format
        if len(lst_num)>0:
            formatos[tuple(lst_num)] = number_format
        if len(lst_dt)>0:
            formatos[tuple(lst_dt)] = data_format
        if len(lst_pct)>0:
            formatos[tuple(lst_pct)] = percentual_format
        return formatos
    
    def realce_col(worksheet = None, lista = [], df = None, colunas = []):
        tam = 9 + len(df)
        for l, lst in enumerate(lista):
            worksheet.write(l,70,lst)
        int_val = f"$BS$1:$BS${len(lista)}"
  
        for letra in colunas:
            intervalo = f'{letra}10:{letra}{tam}'
            base = f'MATCH({letra}10, {int_val}, 0)'
            worksheet.conditional_format( intervalo, {
                'type':     'formula',
                'criteria': f'=ISNUMBER({base})',
                'format':   formato2
            })
            worksheet.conditional_format( intervalo, {
                'type':     'formula',
                'criteria': f'=ISNA({base})',
                'format':   formato1
            })

    linhasAMAIS=8
    if st: avl.progress(25, "Criando aba comparativa de valores...")

    TST_CMP2 = imp_tbl_forma_000(nm_tbl="TST_CMP2_INCR", con=con, st=st, lst_cnv=[], workbook = workbook)
    worksheet1.merge_range('C5:X5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet1.write(linhasAMAIS-1, 2,'Tabela comparativa entre ROA consolidado e arquivo INCREMENTAL',titulo2)
    formatos = formato_def(TST_CMP2)
    x1 = ax_escreve_excel_md2(worksheet1, TST_CMP2, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

    realce_col(worksheet1, 
               ['NO', 'TOTAL AVAL = CONS','TOTAL  TOT = TOT_ROA', 'Valores consistentes'], 
               TST_CMP2,
               ['R','W','Z','AC','AD','AI','AN','AS'])
    
    if st: avl.progress(25, f"Exportando dados do teste de comparação de quantidade ROA e INCR consolidado por código de material...")

    TST_CMP3 = imp_tbl_forma_000(nm_tbl="TST_CMP3_INCR", con=con, st=st, lst_cnv=[], workbook = workbook)
    worksheet2.merge_range('C5:G5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet2.write(linhasAMAIS-1, 2,'Tabela comparativa de quantidade ROA e INCR consolidado por código de material',titulo2)
    formatos = formato_def(TST_CMP3)
    x2 = ax_escreve_excel_md2(worksheet2, TST_CMP3, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)
    
    realce_col(worksheet2, 
               ['NO', 'Ambos'], 
               TST_CMP3,
               ['I','M'])
    
    if st: avl.progress(50, f"Exportando dados do teste de comparação de quantidade ROA, AIS e INCR consolidado por UC-A1'...")
    
    TST_CMP4 = imp_tbl_forma_000(nm_tbl="TST_CMP4_INCR", con=con, st=st, lst_cnv=[], workbook = workbook)
    worksheet3.merge_range('C5:I5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet3.write(linhasAMAIS-1, 2,'Tabela comparativa de quantidade ROA, AIS e INCR consolidado por UC-A1',titulo2)
    formatos = formato_def(TST_CMP4)
    x3 = ax_escreve_excel_md2(worksheet3, TST_CMP4, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)
    realce_col(worksheet3, 
               ['NO', 'Ambos'], 
               TST_CMP4,
               ['L','M', 'N', 'O'])
    if st: avl.progress(75, f"Exportando dados do teste de comparação de quantidade ROA, AIS e INCR consolidado por item'...")
    
    TST_CMP5 = imp_tbl_forma_000(nm_tbl="TST_CMP5_INCR", con=con, st=st, lst_cnv=[], workbook = workbook)
    worksheet4.merge_range('C5:J5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet4.write(linhasAMAIS-1, 2,'Tabela comparativa de quantidade ROA, AIS e INCR consolidado por Projeto-UC-A1',titulo2)
    formatos = formato_def(TST_CMP5)
    x4 = ax_escreve_excel_md2(worksheet4, TST_CMP5, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)
    realce_col(worksheet4, 
               ['NO', 'Ambos'], 
               TST_CMP5,
               ['M', 'N', 'O', 'P'])

    workbook.close()
    if st: avl.progress(100, f"Finalizado e guardado em {dir_arq_saida}/Saida_INCR_F0.xlsx!")
    return "OK"

def imprimi_F1_INCR(dir_arq_saida, con, Empresa, st=None):
    if st:
        avl = st.progress(0, "Iniciando exportação para excel...")

    dir_temp = Path(rf'{dir_arq_saida}/temp_excel')
    dir_temp.mkdir(parents=True, exist_ok=True)
    workbook = xlsxwriter.Workbook(
                                    rf'{dir_arq_saida}/Saida_INCR_F1.xlsx',
                                    {"nan_inf_to_errors": True,
                                    "tmpdir": str(dir_temp)})

    worksheet1 = workbook.add_worksheet('TBL_MEMORIAL_JOA')
    worksheet2 = workbook.add_worksheet('TBL_JOA')
    worksheet3 = workbook.add_worksheet('TBL_INCREMENTAL')
    worksheet4 = workbook.add_worksheet('Teste_CdSisbase')
    worksheet5 = workbook.add_worksheet('Limitador_BPR')
    worksheet6 = workbook.add_worksheet('RESUMO')
    worksheet7 = workbook.add_worksheet('ALMOX_RESUMO')
    worksheet8 = workbook.add_worksheet('ALMOX')
    workbook.set_calc_mode('auto')
    workbook.use_zip64()

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    number2_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8,  'align':'center', 'bottom':1})
    currency2_format = workbook.add_format({'bg_color':'#D9D9D9','num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})

    formato1 = workbook.add_format({'bg_color': '#FFC7CE',
                                   'font_color': '#9C0006'})
    formato2 = workbook.add_format({'bg_color': '#C6EFCE',
                                   'font_color': '#006100'})
    
    def formato_def(df):
        formatos = {}
        lst_txt = []
        lst_moe = []
        lst_num = []
        lst_dt = []
        lst_pct = []
        for col, n in enumerate(df.columns):
            if n[:3].upper() in ['COD','TXT', 'CD_', 'FLG', 'TIP', 'CHV', 'CNP','DESC','UNI','NM_']:
                lst_txt.append(col)
            elif n[:3].upper() in ['VL_','FC','FC_', 'DEL', 'DIF']:
                lst_moe.append(col)
            elif n[:3].upper() in ['QTD', 'CST', 'IND', 'NUM', 'ID_', 'SER']:
                lst_num.append(col)
            elif n[:3].upper() in ['DT_']:
                lst_dt.append(col)
            elif n[:3].upper() in ['ALI','PCT']:
                lst_pct.append(col)
        if len(lst_txt)>0:
            formatos[tuple(lst_txt)] = texto
        if len(lst_moe)>0:
            formatos[tuple(lst_moe)] = currency_format
        if len(lst_num)>0:
            formatos[tuple(lst_num)] = number_format
        if len(lst_dt)>0:
            formatos[tuple(lst_dt)] = data_format
        if len(lst_pct)>0:
            formatos[tuple(lst_pct)] = percentual_format
        return formatos
    
    def realce_col(worksheet = None, lista = [], df = None, colunas = []):
        tam = 9 + len(df)
        for l, lst in enumerate(lista):
            worksheet.write(l,70,lst)
        int_val = f"$BS$1:$BS${len(lista)}"
  
        for letra in colunas:
            intervalo = f'{letra}10:{letra}{tam}'
            base = f'MATCH({letra}10, {int_val}, 0)'
            worksheet.conditional_format( intervalo, {
                'type':     'formula',
                'criteria': f'=ISNUMBER({base})',
                'format':   formato2
            })
            worksheet.conditional_format( intervalo, {
                'type':     'formula',
                'criteria': f'=ISNA({base})',
                'format':   formato1
            })

    linhasAMAIS=8
    if st: avl.progress(3, "Criando aba com os dados empregados para cálculo do JOA...")

    TX_DES = imp_tbl_forma_000(nm_tbl="TX_DES", con=con, st=st, lst_cnv=[], workbook = workbook)
    worksheet1.merge_range('C5:U5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet1.write(linhasAMAIS-1, 2,'Tabela com o cálculo do JOA por tipologia',titulo2)
    formatos = formato_def(TX_DES)
    x1 = ax_escreve_excel_md2(worksheet1, TX_DES, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)
    
    if st: avl.progress(5, f"Criando aba com dados do JOA por Tipologia...")
    
    TX_JOA_APL = imp_tbl_forma_000(nm_tbl="TX_JOA_APL", con=con, st=st, lst_cnv=[], workbook = workbook)
    worksheet2.merge_range('C5:D5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet2.write(linhasAMAIS-1, 2,'Tabela com o resumo do JOA por Tipologia',titulo2)
    formatos = formato_def(TX_JOA_APL)
    x2 = ax_escreve_excel_md2(worksheet2, TX_JOA_APL, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)
    if st: avl.progress(8, f"Criando aba com dados da simulação...")
    
    ANL_INCREMENTAL = imp_tbl_forma_000(nm_tbl="ANL_INCREMENTAL", con=con, st=st, lst_cnv=[], workbook = workbook)
    worksheet3.merge_range('C5:I5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet3.write(linhasAMAIS-1, 2,'AIS INCREMENTAL - VALORAÇÃO',titulo2)
    formatos = formato_def(ANL_INCREMENTAL)
    ANL_INCREMENTAL = ANL_INCREMENTAL.fillna(0)
    x3 = ax_escreve_excel_md2(worksheet3, ANL_INCREMENTAL, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)
    if st: avl.progress(80, f"Exportando dados comparativos dos códigos SISBASE, Avaliadora vs SFF'...")
    
    TST_CD_SISBASE = imp_tbl_forma_000(nm_tbl="TST_CD_SISBASE", con=con, st=st, lst_cnv=[], workbook = workbook)
    worksheet4.merge_range('C5:O5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet4.write(linhasAMAIS-1, 2,'Tabela comparativa dos códigos SISBASE, Avaliadora vs SFF',titulo2)
    formatos = formato_def(TST_CD_SISBASE)
    x4 = ax_escreve_excel_md2(worksheet4, TST_CD_SISBASE, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)
    if st: avl.progress(85, f"Exportando dados do teste de comparação de quantidade ROA, AIS e INCR consolidado por item'...")
    
    ANL_LIMITES_VOC = imp_tbl_forma_000(nm_tbl="ANL_LIMITES_VOC", con=con, st=st, lst_cnv=[], workbook = workbook)
    worksheet5.merge_range('C5:I5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet5.write(linhasAMAIS-1, 2,'Teste de aplicação limite BPR',titulo2)
    formatos = formato_def(ANL_LIMITES_VOC)
    x5 = ax_escreve_excel_md2(worksheet5, ANL_LIMITES_VOC, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

    if st:  avl.progress(90, f"Exportando dados da análise do almoxarifado...")
    
    if existe_tabela('ANL_ALMOX', con):
        ANL_ALMOX = imp_tbl_forma_000(nm_tbl="ANL_ALMOX", con=con, st=st, lst_cnv=[], workbook = workbook)
        worksheet8.merge_range('C5:L5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
        worksheet8.write(linhasAMAIS-1, 2,'Avaliação almoxarifado',titulo2)
        formatos = formato_def(ANL_ALMOX)
        x8 = ax_escreve_excel_md2(worksheet8, ANL_ALMOX, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)
        worksheet8.data_validation('L8:L' + str(len(ANL_ALMOX) + linhasAMAIS-1), {'validate': 'list',
                                                                    'source': [0,1]})

        if st: avl.progress(95, f"Preparando aba com o cálculo da média mensal do almoxarifado...")
        ANL_VL_MENSAL = imp_tbl_forma_000(nm_tbl="ANL_VL_MENSAL", con=con, st=st, lst_cnv=[], workbook = workbook)
        worksheet7.merge_range('C5:D5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
        worksheet7.write(linhasAMAIS-1, 2,'Avaliação almoxarifado, média mensal',titulo2)

        lst_nomes = ANL_VL_MENSAL.columns.to_list()
        for col, nome in enumerate(lst_nomes):
            worksheet7.write(linhasAMAIS, col + 2, nome, titulo)

        for row, data in enumerate(ANL_VL_MENSAL.itertuples(index=False), start=1):
            for col in range(len(lst_nomes)):
                cell_row = row + linhasAMAIS 
                cell_ref = f"C{cell_row + 1}"
                if col == 1:  
                    worksheet7.write_formula(cell_row, col + 2, f"=IFERROR(SUMIFS('ALMOX'!G:G,'ALMOX'!F:F,{cell_ref},'ALMOX'!L:L,0),0)", number_format)
                else:
                    worksheet7.write(cell_row, col + 2, getattr(data, lst_nomes[col]), data_format if col == 0 else texto)
        
        worksheet7.hide_gridlines(2)
        worksheet7.set_column(2,2,15)
        worksheet7.set_column(3,3,55)
    else:
        if st.session_state.dt_fim < diadt.date.today():
            workbook.close()
            if st:
                st.error('Falha ao importar o arquivo ANL_ALMOX da base local.')
            else:
                raise UserWarning('Falha ao importar o arquivo ANL_ALMOX da base local.')

    def ax1_excel(df, worksheet, linha_inicio, col_inicio,number_format,texto):       
        df = df.reset_index(drop=True)
        df.columns = ['Item', 'Valor (R$)']
        df.fillna(0, inplace=True)
        for col, nome in enumerate(df.columns):
            worksheet.write(linha_inicio, col + col_inicio, nome, titulo)
        for row in range(len(df)):
            for col in range(len(df.columns.to_list())):
                if col in [1]:
                    worksheet.write(row+1+linha_inicio, col+col_inicio,df.iloc[row,col],number_format)
                else:
                    worksheet.write(row+1+linha_inicio, col+col_inicio,df.iloc[row,col],texto)
        worksheet.hide_gridlines(2)
        worksheet.set_column(col_inicio, col_inicio, 55)  
        worksheet.set_column(col_inicio + 1, col_inicio + 1, 15)  


    if st: avl.progress(98, f"Preparando aba com resumos...")
    
    SQLq = f"""
            SELECT 
                t1."index",
                COALESCE(t2.Valor, 0) AS VL_AVAL,
                COALESCE(t1.Valor, 0) AS VL_SIM  
            FROM 
                RES_INCR_QDTAR_SFF t1 LEFT JOIN RES_INCR_QDTAR t2 ON t1."index"=t2."index"
            """
    df1 = imp_tbl_forma_000(nm_tbl="RES_INCR_QDTAR_SFF", SQLq = SQLq, con=con, st=st, lst_cnv=[], workbook = workbook)

    df1 = df1.sort_values(
                            by='index',
                            key=lambda x: x.str.extract(r'^\((\d+)\)')[0].astype(int)
                        ).reset_index(drop=True)
    
    linhasAMAIS = 6
    worksheet6.merge_range('C3:G3', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
    worksheet6.merge_range('C5:D5', f'CÁLCULO AVALIADORA {Empresa}', titulo)
    worksheet6.merge_range('F5:G5', f'CÁLCULO SIMULADO {Empresa}', titulo)

    ax1_excel(df1.iloc[:, [0, 1]], worksheet6, linhasAMAIS, 2,number_format,texto)
    ax1_excel(df1.iloc[:, [0, 2]], worksheet6, linhasAMAIS, 5,number_format,texto)

    worksheet6.hide_gridlines(2)
    worksheet6.set_column(5,5,55)
    worksheet6.set_column(6,6,15)
    rfim = 9 + len(ANL_INCREMENTAL)

    worksheet6.write_formula(
                            'D10',
                            (
                                f"=SUM("
                                f"TBL_INCREMENTAL!$EW$10:$EW${rfim})"
                            ),
                            number_format
                        )
    worksheet6.write_formula('G10','= D10',number_format)

    worksheet6.write_formula('D12','=D8-D9-D10-D11',number_format)
    worksheet6.write_formula('G12','=G8-G9-G10-G11',number_format)
    
    worksheet6.write_formula('D14','=D8-D13',number_format)
    worksheet6.write_formula('G14','=G8-G13',number_format)
    
    worksheet6.write_formula('D16','=D14-D15',number_format)
    worksheet6.write_formula('G16','=G14-G15',number_format)
    
    worksheet6.write_formula('D17',"=IFERROR(AVERAGE('ALMOX_RESUMO'!D8:D19),0)",number_format)
    worksheet6.write_formula('G17',"=IFERROR(AVERAGE('ALMOX_RESUMO'!D8:D19),0)",number_format)

    
    worksheet6.write_formula(
                            'D19',
                            (
                                f"=SUM("
                                f"TBL_INCREMENTAL!$EX$10:$EX${rfim})"
                            ),
                            number_format
                        )
    worksheet6.write_formula('G19','= D19',number_format)
    
    worksheet6.write_formula('D21','=D8-D13-D15+D17+D18-D19+D20',number_format)
    worksheet6.write_formula('G21','=G8-G13-G15+G17+G18-G19+G20',number_format)

    worksheet6.write('I7', 'DELTA (%)',titulo)
    for i in range(8, 22):
        worksheet6.write_formula("I" + str(i), '=if(D' + str(i) + '<>0,D' + str(i) + '/G' + str(i) + '-1,0)', percentual_format)

    workbook.close()
    if st: avl.progress(100, f"Finalizado e guardado em {dir_arq_saida}/Saida_INCR_F1.xlsx!")
    return "OK"

def imprimi_F0_OE(dir_arq_saida, con, Empresa, st=None):
    if st:
        avl = st.progress(0, "Iniciando exportação para excel...")

    workbook = xlsxwriter.Workbook(f'{dir_arq_saida}/Saida_OE_F0.xlsx', {"nan_inf_to_errors": True})

    worksheet6 = workbook.add_worksheet('BMP_MANUAL')
    worksheet2 = workbook.add_worksheet('OE5b')
    worksheet1 = workbook.add_worksheet('OE5a')
    worksheet4 = workbook.add_worksheet('TESTE_TX_AMT_CNTB')
    worksheet5 = workbook.add_worksheet('LISTA_AJUSTES')
    worksheet3 = workbook.add_worksheet('Tabela IPCA')
    workbook.set_calc_mode('auto')

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    linhasAMAIS=8
    if st:
        avl.progress(25, "Criando aba com os dados da análise analítica da OE...")

    #Primeiro vamos imprimir os resultados dos itens conciliados
    if existe_tabela('ANL_OE_UN', con):
        SQLq = f"""
                    SELECT *
                    FROM ANL_OE_UN  
            """
        ANL_OE_UN = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo ANL_OE_UN da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo ANL_OE_UN da base local.')
        
    if existe_tabela('ANL_OE_FIM', con):
        SQLq = f"""
                    SELECT *
                    FROM ANL_OE_FIM
            """
        OE5a_fim = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo ANL_OE_FIM da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo ANL_OE_FIM da base local.')

    dt_ARQ = max_arq("OE_AJS", con, Empresa)
    if dt_ARQ:
        SQLq = f"""
                    SELECT *
                    FROM OE_AJS WHERE dt_ARQ = {dt_ARQ}
            """
        OE_AJST = pd.read_sql(SQLq, con)
    else:
        OE_AJST = pd.DataFrame()
    
    #Aba n
    PLPT = existe_tabela("OE_PLPTMOV", con)
    CCC = existe_tabela("OE_CCCMOV", con)
    IR = existe_tabela("OE_IRMOV", con)
    VAR = PLPT+CCC+IR
    linhasAMAIS = 8
    worksheet1.merge_range('C5:D5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
    worksheet1.write(linhasAMAIS-1, 2,'Tabela com a movimentação no período incremental',titulo2)
    formatos = {
                    tuple(range(1, len(ANL_OE_UN.columns)+1)): currency_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {
                        (2, 2): 65
                      }

    x1 = ax_escreve_excel(worksheet1, ANL_OE_UN, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    
    linhasAMAIS = linhasAMAIS+4+len(ANL_OE_UN)
    worksheet1.write(linhasAMAIS-1, 2,'Tabela resumo',titulo2)

    formatos = {
                    tuple(range(1, len(OE5a_fim.columns)+1)): currency_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {}
    for i, col in enumerate(OE5a_fim.columns):
        max_len = max(
                        OE5a_fim[col].astype(str).map(len).max(),
                        len(col)                              
                        ) + 2  
        colunas_largura[(i+2, i+2)] = max_len

    x2 = ax_escreve_excel(worksheet1, OE5a_fim, linhasAMAIS, formatos, colunas_largura, texto, titulo, rows = [[VAR+4, VAR+5], [0]], formato = percentual_format, st=st)
    
    if st:
        avl.progress(25, f"Exportando dados do teste da taxa de amortização da OE...")
    
    if existe_tabela('ANL_TX_AMT_OE', con):
        SQLq = f"""
                    SELECT *
                    FROM ANL_TX_AMT_OE
            """
        ANL_TX_AMT_OE = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo ANL_TX_AMT_OE da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo ANL_TX_AMT_OE da base local.')
        
    worksheet4.merge_range('C5:G5', 'TESTE DA TAXA DE AMORTIZAÇÃO CONTÁBIL', tituloP)
    linhasAMAIS=8
    formatos = {
                    (0,1,2,3,4): percentual_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {}
    for i, col in enumerate(ANL_TX_AMT_OE.columns):
        max_len = max(
                        ANL_TX_AMT_OE[col].astype(str).map(len).max(),
                        len(col)                              
                        ) + 2  
        colunas_largura[(i+2, i+2)] = max_len
    x3 = ax_escreve_excel(worksheet4, ANL_TX_AMT_OE, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    
    if st:
        avl.progress(45, f"Exportando dados do IPCA...")
    if existe_tabela('ANL_IPCA_OE', con):
        SQLq = f"""
                    SELECT *
                    FROM ANL_IPCA_OE
            """
        ANL_IPCA_OE = pd.read_sql(SQLq, con)
        ANL_IPCA_OE['DT_CMPT'] = pd.to_datetime(ANL_IPCA_OE['DT_CMPT'], errors = 'coerce')
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo ANL_IPCA_OE_OE da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo ANL_IPCA_OE da base local.')
        
    worksheet3.merge_range('C5:D5', 'DADOS IBGE', tituloP)
    worksheet3.write(linhasAMAIS-1, 2,'Tabela IPCA - Número Índice',titulo2)
    formatos = {
                    (0,): data_format,
                    tuple(range(1, len(ANL_IPCA_OE.columns)+1)): number_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {}
    for i, col in enumerate(ANL_IPCA_OE.columns):
        max_len = max(
                        ANL_IPCA_OE[col].astype(str).map(len).max(),
                        len(col)                              
                        ) + 2  
        colunas_largura[(i+2, i+2)] = max_len

    x4 = ax_escreve_excel(worksheet3, ANL_IPCA_OE, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    
    if st:
        avl.progress(90, f"Exportando resultado do blindado...")

    if existe_tabela('ANL_OE_BB', con):
        SQLq = f"""
                    SELECT *
                    FROM ANL_OE_BB
            """
        df_BB = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo df_BB da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo df_BB da base local.')
        
    if existe_tabela('ANL_OE_BI', con):
        SQLq = f"""
                    SELECT *
                    FROM ANL_OE_BI
            """
        df_BI = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo df_BI da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo df_BI da base local.')
        
    worksheet2.merge_range('C3:G3', 'RELATÓRIO SINTÉTICO', tituloP)
    worksheet2.write(linhasAMAIS-1, 2,'Resumo OE Blindada',titulo2)
    formatos = {
                    (1,): number_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {}
    for i, col in enumerate(df_BI.columns):
        max_len = max(
                        df_BI[col].astype(str).map(len).max(),
                        len(col)                              
                        ) + 2  
        colunas_largura[(i+2, i+2)] = max_len

    x5 = ax_escreve_excel(worksheet2, df_BB, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)

    if existe_tabela('ANL_BMP_MANUAL', con):
        SQLq = f"""
                    SELECT *
                    FROM ANL_BMP_MANUAL
            """
        df_BMP = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo df_BI da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo df_BI da base local.')
        
    worksheet6.merge_range('C3:G3', 'RELATÓRIO BMP vs MANUAL DE DADOS', tituloP)
    worksheet6.write(linhasAMAIS-1, 2, 'Resumo', titulo2)
    formatos = {
                    (2,4,5,6,8): number_format,
                }
    
    colunas_largura = {}
    for i, col in enumerate(df_BMP.columns):
        max_len = max(
                        df_BMP[col].astype(str).map(len).max(),
                        len(col)                              
                        ) + 2  
        colunas_largura[(i+2, i+2)] = max_len

    x6 = ax_escreve_excel(worksheet6, df_BMP, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)

    if st:
        avl.progress(95, f"Exportando resumo incremental...")
    linhasAMAIS = linhasAMAIS + 4 + len(df_BI)
    worksheet2.write(linhasAMAIS-1, 2,'Resumo OE Incremental',titulo2)
    formatos = {
                    (1,2,3,4,5): number_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {
                        (2, 6): 15, (2, 2): 32,
                      }

    x6 = ax_escreve_excel(worksheet2, df_BI, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)

    if st:
        avl.progress(98, f"Exportando dados de ajustes...")

    

    worksheet5.merge_range('C5:H5', 'LISTA DE AJUSTES EFETUADOS', tituloP)
    formatos = {
                    (0,): number_format,
                    (2,): currency_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {}
    for i, col in enumerate(OE_AJST.columns):
        max_len = max(
                        OE_AJST[col].astype(str).map(len).max(),
                        len(col)                              
                        ) + 2  
        colunas_largura[(i+2, i+2)] = max_len
    if not OE_AJST.empty:
        x7 = ax_escreve_excel(worksheet5, OE_AJST, 8, formatos, colunas_largura, texto, titulo, st=st)
    else:
        worksheet5.hide_gridlines(2)


    workbook.close()
    if st:
        avl.progress(100, f"Finalizado e guardado em {dir_arq_saida}/Saida_OE_F0.xlsx!")
    return "OK"

def imprimi_F1_OE(dir_arq_saida, con, Empresa, st=None):
    if st:
        avl = st.progress(0, "Iniciando exportação para excel...")

    workbook = xlsxwriter.Workbook(f'{dir_arq_saida}/Saida_OE_F1.xlsx', {"nan_inf_to_errors": True})

    worksheet1 = workbook.add_worksheet('TX_MED_ATIVID')
    worksheet2 = workbook.add_worksheet('RESUMO_UC')
    workbook.set_calc_mode('auto')

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    linhasAMAIS=8
    if st:
        avl.progress(25, "Criando aba com os dados da taxa de depreciação por atividade...")

    #Primeiro vamos imprimir os resultados dos itens conciliados
    if existe_tabela('AIS_TX_ATV', con):
        SQLq = f"""
                    SELECT *
                    FROM AIS_TX_ATV  
            """
        AIS_TX_ATV = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo AIS_TX_ATV da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo AIS_TX_ATV da base local.')
        
    if existe_tabela('AIS_TX_UC', con):
        SQLq = f"""
                    SELECT *
                    FROM AIS_TX_UC
            """
        AIS_TX_UC = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo AIS_TX_UC da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo AIS_TX_UC da base local.')

    linhasAMAIS = 8
    worksheet1.merge_range('C5:I5', f'CÁLCULO TAXA DE DEPRECIAÇÃO {Empresa}', tituloP)
    worksheet1.write(linhasAMAIS-1, 2,'Tabela com a taxa de depreciação por atividade',titulo2)
    formatos = {
                    (2,3,4,5): currency_format,
                    (6,) : percentual_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {
                        (2, 2): 13, (3, 3): 9, (4,7): 16, (8,8): 6.5
                      }

    x1 = ax_escreve_excel(worksheet1, AIS_TX_ATV, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    
    if st:
        avl.progress(75, f"Exportando dados de depreciação por UC...")
    
        
    worksheet2.merge_range('C5:I5', 'CÁLCULO TAXA DE DEPRECIAÇÃO', tituloP)
    worksheet2.write(linhasAMAIS-1, 2,'Tabela com a taxa de depreciação por UC',titulo2)
    formatos = {
                    tuple(range(4, len(AIS_TX_UC.columns)+1)): currency_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {
                        (2, 9): 15
                      }

    x3 = ax_escreve_excel(worksheet2, AIS_TX_UC, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    
    workbook.close()
    if st:
        avl.progress(100, f"Finalizado e guardado em {dir_arq_saida}/Saida_BP_F1.xlsx!")
    return "OK"

def imprimi_F0_BB(dir_arq_saida, con, Empresa, st=None):
    if st:
        avl = st.progress(0, "Iniciando exportação para excel...")
    
    dir_temp = Path(rf'{dir_arq_saida}/temp_excel')
    dir_temp.mkdir(parents=True, exist_ok=True)
    workbook = xlsxwriter.Workbook(
                                    rf'{dir_arq_saida}/Saida_BB_F0.xlsx',
                                    {"nan_inf_to_errors": True,
                                     "tmpdir": str(dir_temp)})

    worksheet1 = workbook.add_worksheet('TESTE_PP')
    worksheet3 = workbook.add_worksheet('TESTE_BAIXAS')
    worksheet5 = workbook.add_worksheet('TESTE_BAIXAS_UC')
    worksheet4 = workbook.add_worksheet('RESUMO')
    workbook.set_calc_mode('auto')
    workbook.use_zip64()

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    linhasAMAIS=8
    if st:
        avl.progress(5, "Criando aba com a análise do ponto de partida...")

    #Primeiro vamos imprimir os resultados dos itens conciliados
    if existe_tabela('ANL_PP', con):
        SQLq = f"""
                    SELECT *
                    FROM ANL_PP  
            """
        df_PP = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo ANL_PP da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo ANL_PP da base local.')
        
    linhasAMAIS = 6
    worksheet1.merge_range('C5:F5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
    formatos = {
                    (1,2,3,4,5,6): currency_format,
                    (7,): data_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {
                        (3, 8): 16, (2, 2): 55
                      }

    x1 = ax_escreve_excel(worksheet1, df_PP, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    
    if st:
        avl.progress(10, "Criando abas com a avaliação analítica...")

    #Primeiro vamos imprimir os resultados dos itens conciliados
    if existe_tabela('ANL_BB_CMP', con):
        SQLq = f"""
                    SELECT *
                    FROM ANL_BB_CMP
            """
        df = pd.read_sql(SQLq, con)
        try:
            df = df.drop(columns=['Cd_Emp_x','dt_ARQ_x','Cd_Emp_y','dt_ARQ_y'])
        except:
            pass
        tmn = 500000
        n = 0
        formatos = {
                        (21,23,24,34,28,29,30,31,32,33,47,39,40,41,42,43,44,45,46,49,50,
                         57,51,52,53,54,55,56,58,59,62,66): number_format,
                        (25,37,48): data_format,
                        (63,64,65,68,67,69,70): percentual_format,
                    }
        
        #Configuração otimizada de largura de colunas
        colunas_largura = {
                            (5,79): 15, (22,22): 50, (60,60): 25, (73,74): 60,
                            (62,62): 25,
                        }
        df['Id_SEQ_PP']=pd.to_numeric(df['Id_SEQ_PP'].str.replace(',','.'),errors='coerce')
        while n*tmn <= (len(df) + 1):
            BL_DFimp = df.iloc[n*tmn : (n+1)*tmn].copy()
            wb = workbook.add_worksheet(f'TESTE_VNR{n}')
            wb.merge_range('C5:L5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
            xn = ax_escreve_excel(wb, BL_DFimp, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
            n += 1
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo ANL_BB_CMP da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo ANL_BB_CMP da base local.')
        
    if st:
        avl.progress(95, "Criando aba com a análise do ponto de partida...")

    #Primeiro vamos imprimir os resultados dos itens conciliados
    if existe_tabela('ANL_TST_BX', con):
        SQLq = f"""
                    SELECT *
                    FROM ANL_TST_BX  
            """
        tst_bx = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo ANL_TST_BX da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo ANL_TST_BX da base local.')
        
    worksheet3.merge_range('C5:N5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
    formatos = {
                    (2,3,4,5,6,7,9,10,11): number_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {
                        (2, 14): 12, (10, 10): 60
                      }

    x2 = ax_escreve_excel(worksheet3, tst_bx, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    
    #Avaliação das baixas por UC
    BL_DFimp = tst_bx.groupby(['Nr_TUC'],
                              dropna=False)[['QTD_AIS_PP','QTD_AIS_PC','QTD_BXS_APL',
                                             'QTD_INI_BXS','QTD_FIM_BXS','QTD_BXS_CTB',
                                             'Qtd_INI_INC','Qtd_FIM_INC', 
                                             'QTD_BXS_CTB_INC']].sum().reset_index()
    BL_DFimp['TST_BXS_BL']='OK'
    BL_DFimp.loc[((-abs(BL_DFimp['QTD_BXS_APL']) + abs(BL_DFimp['QTD_BXS_CTB'])) / 
                  abs(BL_DFimp['QTD_BXS_CTB'])) > 0.1, 
                  'TST_BXS_BL'] = 'DIVERGÊNCIA ENTRE ARQUIVO BAIXAS E PCBB/PPBB'

    worksheet5.merge_range('C5:M5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
    formatos = {
                    (1,2,3,4,5,6,7,8,9,10,11): number_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {
                        (2, 14): 12, (12, 12): 60
                      }

    x3 = ax_escreve_excel(worksheet5, BL_DFimp, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    
    if st:
        avl.progress(97, "Criando aba com o resumo da blindada...")

    #Primeiro vamos imprimir os resultados dos itens conciliados
    if existe_tabela('RESUMO_BB', con):
        SQLq = f"""
                    SELECT *
                    FROM RESUMO_BB  
            """
        RESUMO_BB = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo RESUMO_BB da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo RESUMO_BB da base local.')
        
    worksheet4.merge_range('C5:P5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
    formatos = {
                    (1,2,3,4,5,6,7,8,9,10,11,12,13): number_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {}
    for i, col in enumerate(RESUMO_BB.columns):
        max_len = max(
                        RESUMO_BB[col].astype(str).map(len).max(),
                        len(col)                              
                        ) + 2  
        colunas_largura[(i+2, i+2)] = max_len

    x4 = ax_escreve_excel(worksheet4, RESUMO_BB, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    
    workbook.close()
    if st:
        avl.progress(100, f"Finalizado e guardado em {dir_arq_saida}/Saida_BB_F0.xlsx!")
    return "OK"


def imprimi_F1_OE(dir_arq_saida, con, Empresa, st=None):
    if st:
        avl = st.progress(0, "Iniciando exportação para excel...")

    workbook = xlsxwriter.Workbook(f'{dir_arq_saida}/Saida_OE_F1.xlsx')

    worksheet1 = workbook.add_worksheet('TX_MED_ATIVID')
    worksheet2 = workbook.add_worksheet('RESUMO_UC')
    worksheet4 = workbook.add_worksheet('RESUMO_UC_TI_BAR')
    worksheet3 = workbook.add_worksheet('RESUMO_UC_REDES')
    workbook.set_calc_mode('auto')

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    linhasAMAIS=8
    if st:
        avl.progress(25, "Criando aba com os dados da taxa de depreciação por atividade...")

    #Primeiro vamos imprimir os resultados dos itens conciliados
    if existe_tabela('AIS_TX_ATV', con):
        SQLq = f"""
                    SELECT *
                    FROM AIS_TX_ATV  
            """
        AIS_TX_ATV = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo AIS_TX_ATV da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo AIS_TX_ATV da base local.')
        
    if existe_tabela('AIS_TX_ATV_PLPT', con):
        SQLq = f"""
                    SELECT *
                    FROM AIS_TX_ATV_PLPT  
            """
        AIS_TX_ATV_PLPT = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo AIS_TX_ATV_PLPT da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo AIS_TX_ATV_PLPT da base local.')
        
    if existe_tabela('AIS_TX_ATV_TI_BAR', con):
        SQLq = f"""
                    SELECT *
                    FROM AIS_TX_ATV_TI_BAR  
            """
        AIS_TX_ATV_TI_BAR = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo AIS_TX_ATV_TI_BAR da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo AIS_TX_ATV_TI_BAR da base local.')
        
    if existe_tabela('AIS_TX_UC', con):
        SQLq = f"""
                    SELECT *
                    FROM AIS_TX_UC
            """
        AIS_TX_UC = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo AIS_TX_UC da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo AIS_TX_UC da base local.')
        
    if existe_tabela('AIS_TX_UC_PLPT', con):
        SQLq = f"""
                    SELECT *
                    FROM AIS_TX_UC_PLPT
            """
        AIS_TX_UC_PLPT = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo AIS_TX_UC_PLPT da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo AIS_TX_UC_PLPT da base local.')
        
    if existe_tabela('AIS_TX_UC_TI_BAR', con):
        SQLq = f"""
                    SELECT *
                    FROM AIS_TX_UC_TI_BAR
            """
        AIS_TX_UC_TI_BAR = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo AIS_TX_UC_TI_BAR da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo AIS_TX_UC_TI_BAR da base local.')

    linhasAMAIS = 8
    worksheet1.merge_range('C5:I5', f'CÁLCULO TAXA DE DEPRECIAÇÃO {Empresa}', tituloP)
    worksheet1.write(linhasAMAIS-1, 2,'Tabela com a taxa de depreciação por atividade, SEM TI de BAR',titulo2)
    worksheet1.write(14, 2,'Tabela com a taxa de depreciação por atividade, COM TI de BAR',titulo2)
    worksheet1.write(21, 2,'Tabela com a taxa de depreciação por atividade, redes',titulo2)
    formatos = {
                    (2,3,4,5): currency_format,
                    (6,) : percentual_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {
                        (2, 2): 13, (3, 3): 9, (4,7): 16, (8,8): 6.5
                      }

    x1 = ax_escreve_excel(worksheet1, AIS_TX_ATV, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    x4 = ax_escreve_excel(worksheet1, AIS_TX_ATV_PLPT, 22, formatos, colunas_largura, texto, titulo, st=st)
    x5 = ax_escreve_excel(worksheet1, AIS_TX_ATV_TI_BAR, 15, formatos, colunas_largura, texto, titulo, st=st)
    
    if st:
        avl.progress(75, f"Exportando dados de depreciação por UC...")
    
        
    worksheet2.merge_range('C5:I5', 'CÁLCULO TAXA DE DEPRECIAÇÃO', tituloP)
    worksheet2.write(linhasAMAIS-1, 2,'Tabela com a taxa de depreciação por UC',titulo2)
    formatos = {
                    tuple(range(4, len(AIS_TX_UC.columns)+1)): currency_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {
                        (2, 9): 15
                      }

    x3 = ax_escreve_excel(worksheet2, AIS_TX_UC, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)

    worksheet3.merge_range('C5:I5', 'CÁLCULO TAXA DE DEPRECIAÇÃO PLPT', tituloP)
    worksheet3.write(linhasAMAIS-1, 2,'Tabela com a taxa de depreciação por UC',titulo2)
    formatos = {
                    tuple(range(4, len(AIS_TX_UC_PLPT.columns)+1)): currency_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {
                        (2, 9): 15
                      }

    x3 = ax_escreve_excel(worksheet3, AIS_TX_UC_PLPT, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)

    worksheet4.merge_range('C5:I5', 'CÁLCULO TAXA DE DEPRECIAÇÃO ATIVOS BAR POR TI', tituloP)
    worksheet4.write(linhasAMAIS-1, 2,'Tabela com a taxa de depreciação por UC',titulo2)
    formatos = {
                    tuple(range(4, len(AIS_TX_UC_TI_BAR.columns)+1)): currency_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {
                        (2, 9): 15
                      }

    x3 = ax_escreve_excel(worksheet4, AIS_TX_UC_TI_BAR, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    
    workbook.close()
    if st:
        avl.progress(100, f"Finalizado e guardado em {dir_arq_saida}/Saida_OE_F2.xlsx!")


    workbook = xlsxwriter.Workbook(f'{dir_arq_saida}/Saida_OE_F2.xlsx')

    worksheet1 = workbook.add_worksheet('TX_MED_ATIVID')
    worksheet2 = workbook.add_worksheet('RESUMO_UC_VNR')
    workbook.set_calc_mode('auto')

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    linhasAMAIS=8
    if st:
        avl.progress(25, "Criando aba com os dados da taxa de depreciação por atividade...")

    #Primeiro vamos imprimir os resultados dos itens conciliados
    if existe_tabela('AIS_TX_ATV_VNR', con):
        SQLq = f"""
                    SELECT *
                    FROM AIS_TX_ATV_VNR  
            """
        AIS_TX_ATV = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo AIS_TX_ATV_VNR da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo AIS_TX_ATV_VNR da base local.')
        
            
    if existe_tabela('AIS_TX_UC_VNR', con):
        SQLq = f"""
                    SELECT *
                    FROM AIS_TX_UC_VNR
            """
        AIS_TX_UC = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo AIS_TX_UC_VNR da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo AIS_TX_UC_VNR da base local.')
        
    linhasAMAIS = 8
    worksheet1.merge_range('C5:I5', f'CÁLCULO TAXA DE DEPRECIAÇÃO {Empresa}', tituloP)
    worksheet1.write(linhasAMAIS-1, 2,'Tabela com a taxa de depreciação por atividade, VNR',titulo2)

    formatos = {
                    (2,3,4,5): currency_format,
                    (6,) : percentual_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {
                        (2, 2): 13, (3, 3): 9, (4,7): 16, (8,8): 6.5
                      }

    x1 = ax_escreve_excel(worksheet1, AIS_TX_ATV, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    
    if st:
        avl.progress(75, f"Exportando dados de depreciação por UC...")
    
        
    worksheet2.merge_range('C5:I5', 'CÁLCULO TAXA DE DEPRECIAÇÃO', tituloP)
    worksheet2.write(linhasAMAIS-1, 2,'Tabela com a taxa de depreciação por UC',titulo2)
    formatos = {
                    tuple(range(4, len(AIS_TX_UC.columns)+1)): currency_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {
                        (2, 9): 15
                      }

    x3 = ax_escreve_excel(worksheet2, AIS_TX_UC, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    
    workbook.close()
    if st:
        avl.progress(100, f"Finalizado e guardado em {dir_arq_saida}/Saida_BP_F2.xlsx!")

    return "OK"

def imprimi_F0_AMS(dir_arq_saida, con, Empresa, st=None, MA=10000000, MR = 9500000):
    if st:
        avl = st.progress(0, "Iniciando exportação para excel...")

    workbook = xlsxwriter.Workbook(f'{dir_arq_saida}/Saida_AMS_F0.xlsx', {"nan_inf_to_errors": True})

    worksheet3 = workbook.add_worksheet('ANL_RES')
    worksheet1 = workbook.add_worksheet('RESUMO_SORTEIO')
    worksheet2 = workbook.add_worksheet('DADOS_ROA')
    ws1 = workbook.add_worksheet('ANALISE_CA_ROA')
    worksheet4 = workbook.add_worksheet('DADOS_ROD')
    workbook.set_calc_mode('auto')

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    linhasAMAIS=8
    if st:
        avl.progress(5, "Criando aba com as amostras...")

    #Primeiro vamos imprimir os resultados dos itens conciliados
    if existe_tabela('tbl_AMOSTRAS', con):
        SQLq = f"""
                    SELECT *
                    FROM tbl_AMOSTRAS  
            """
        df_PP = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo tbl_AMOSTRAS da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo tbl_AMOSTRAS da base local.')
        
    linhasAMAIS = 6
    worksheet1.merge_range('C5:N5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
    formatos = {
                    (2,3,4,5,6,7): number_format,

                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {
                        (2, 37): 16, (2, 2): 20, (3, 3): 10,
                      }

    x1 = ax_escreve_excel(worksheet1, df_PP, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    
    if st: avl.progress(25, "Criando aba com os registros do ROA das Amostras...")
    lst_PRJ = tuple(df_PP['Cd_SubODI'].drop_duplicates().to_list())

    try:
        SQLq = f"""
                    WITH 
                    ROA_BASE AS (
                        SELECT
                            t1.*,
                            CASE 
                                WHEN t1.Cd_NG IN (1,2) THEN t2.DESCR_ITEM
                                WHEN t1.Cd_NG IN (4) THEN t3.DESCR_ITEM 
                                ELSE NULL 
                            END AS DESC_COD_ITEM,
                            t4.Txt_Cls_Custo AS DESC_CLS_CUSTO
                        FROM
                            ROA t1
                        LEFT JOIN LST_MAT t2 ON t1.COD_ITEM = t2.COD_ITEM 
                            AND t2.dt_ARQ = ? 
                        LEFT JOIN LST_SERV t3 ON t1.COD_ITEM = t3.COD_ITEM 
                            AND t3.dt_ARQ = ?
                        LEFT JOIN DSC_CLS_CUSTO t4 ON t1.Cd_Cls_Custo = t4.Cd_Cls_Custo 
                            AND t4.dt_ARQ = ?
                        WHERE 
                            t1.Cd_SubODI IN {lst_PRJ}
                            AND t1.dt_ARQ = ?
                    )

                    SELECT 
                        rb.Ide_RO_Analitico, rb.Cd_ODI, rb.Cd_SubODI, rb.Cd_Cls_Custo, rb.DESC_CLS_CUSTO, 
                        rb.COD_ITEM, rb.DESC_COD_ITEM, rb.Cd_NG, 
                        CASE 
                            WHEN rb.Cd_NG IN (1) THEN 'UC/UAR'
                            WHEN rb.Cd_NG IN (2) THEN 'COM'
                            WHEN rb.Cd_NG IN (3) THEN 'MOP'
                            WHEN rb.Cd_NG IN (4) THEN 'ST'
                            WHEN rb.Cd_NG IN (5) THEN 'JOA'
                            WHEN rb.Cd_NG IN (6) THEN 'Outros' 
                            ELSE NULL 
                        END AS DESC_NG,
                        rb.Cd_CA, 
                        CASE 
                            WHEN rb.Cd_CA IN (1) THEN 'Frete/Transporte'
                            WHEN rb.Cd_CA IN (2) THEN 'Projeto'
                            WHEN rb.Cd_CA IN (3) THEN 'Gerenciamento'
                            WHEN rb.Cd_CA IN (4) THEN 'Fiscalização'
                            WHEN rb.Cd_CA IN (5) THEN 'Montagem'
                            WHEN rb.Cd_CA IN (6) THEN 'Custo de Suporte' 
                            ELSE NULL 
                        END AS DESC_CA,
                        rb.FLG_PLPT, rb.Qtd, rb.Unidade, 
                        rb.VL_tot, rb.Dt_Lcmto, rb.Cd_Pedido, rb.Txt_Doc, rb.Nr_TI, rb.Nr_TUC,
                        rb.Nr_A1, rb.Nr_A2, rb.Nr_A3, rb.Nr_A4, rb.Nr_A5, rb.Nr_A6, 
                        rb.Txt_Nom_Forn, rb.Nr_NF, rb.Nr_ItemNF, rb.Nr_SerieNF, rb.CNPJ_Forn, 
                        rb.FLG_DOA_OE, rb.FLG_INCOR_OE, rb.FLG_OAT, rb.Cd_ATIP, 
                        CASE 
                            WHEN rb.Cd_ATIP IN (1) THEN 'Expansão em linha viva'
                            WHEN rb.Cd_ATIP IN (2) THEN 'Recondutoramento de circuitos'
                            WHEN rb.Cd_ATIP IN (3) THEN 'Recapacitação de linhas'
                            WHEN rb.Cd_ATIP IN (4) THEN 'Instalação ou substituição de UAR que não seja a própria UC'
                            WHEN rb.Cd_ATIP IN (5) THEN 'Redes e linhas de distribuição subterrâneas ou submersas (todas as TUC associadas)'
                            WHEN rb.Cd_ATIP IN (6) THEN 'Estruturas tipo torre (TUC 255.02)' 
                            WHEN rb.Cd_ATIP IN (7) THEN 'Estruturas tipo poste em Linhas de Distribuição (TUC 255.01)'
                            WHEN rb.Cd_ATIP IN (8) THEN 'Sistemas especiais de medição'
                            WHEN rb.Cd_ATIP IN (9) THEN 'Novas tecnologias, ainda não modularizadas'
                            WHEN rb.Cd_ATIP IN (10) THEN 'Outros'
                            ELSE NULL 
                        END AS DESC_ATIP,
                        rb.Cd_AJST, rb.Cd_SubODI_MUT, rs.Txt_Desc_PRJ, rs.Cd_Tipo_Obra,
                        CASE 
                            WHEN rs.Cd_Tipo_Obra IN (1) THEN 'Ampliação/Expansão'
                            WHEN rs.Cd_Tipo_Obra IN (2) THEN 'Construção'
                            WHEN rs.Cd_Tipo_Obra IN (3,10) THEN 'Manutenção'
                            WHEN rs.Cd_Tipo_Obra IN (4) THEN 'Melhoria/Reforma'
                            WHEN rs.Cd_Tipo_Obra IN (5,6) THEN 'Administrativo'
                            WHEN rs.Cd_Tipo_Obra IN (7) THEN 'Incorporação'
                            WHEN rs.Cd_Tipo_Obra IN (8) THEN 'PEE'
                            WHEN rs.Cd_Tipo_Obra IN (9) THEN 'PeD'
                            WHEN rs.Cd_Tipo_Obra IN (11,12) THEN 'Medição'
                            ELSE NULL 
                        END AS Txt_TP_OBRA,
                        CASE 
                            WHEN rs.Cd_Tipo_Obra IN (1,2,4,5,7,8,9,10,11) THEN 'Investimento'
                            WHEN rs.Cd_Tipo_Obra IN (3,6,12) THEN 'Manutenção'
                            ELSE NULL 
                        END AS Txt_CLS_OBRA, 
                        rs.Dt_Inic_Proj, rs.Dt_Energ, rs.Dt_Uniti, rs.Pct_OE, 
                        rs.Nr_Fases, rs.VL_TEN, rs.Cd_ODD, rs.Txt_JUST_ODD, rs.Cd_Tipo_OE,
                        CASE 
                            WHEN rs.Cd_Tipo_OE IN (1) THEN 'NO'
                            WHEN rs.Cd_Tipo_OE IN (2) THEN 'PlPT'
                            WHEN rs.Cd_Tipo_OE IN (3) THEN 'MLA'
                            WHEN rs.Cd_Tipo_OE IN (4) THEN 'Subvenção de CCC'
                            WHEN rs.Cd_Tipo_OE IN (5) THEN 'Doações'
                            WHEN rs.Cd_Tipo_OE IN (6) THEN 'Participação Financeira do Consumidor' 
                            WHEN rs.Cd_Tipo_OE IN (7) THEN 'Repasses de Recursos dos Governos Federal, Estadual, Distrital e Municipal'
                            WHEN rs.Cd_Tipo_OE IN (8) THEN 'Incorporações'
                            WHEN rs.Cd_Tipo_OE IN (9) THEN 'Outros'
                            ELSE NULL 
                        END AS DESC_OE
                    FROM 
                        ROA_BASE rb
                    LEFT JOIN 
                        ROS rs ON rb.Cd_SubODI = rs.Cd_SubODI 
                        AND rs.dt_ARQ = ?
                """
        params = [
                    'LST_MAT',
                    'LST_SERV',
                    'DSC_CLS_CUSTO',
                    'ROA',
                    'ROS'     
                ]
        ROA = imp_tbl_forma_003(params, SQLq, con = con, st=st, Empresa=Empresa)
    except:
        try:
            SQLq = f"""
                        WITH 
                        ROA_BASE AS (
                            SELECT
                                t1.*,
                                CASE 
                                    WHEN t1.Cd_NG IN (1,2) THEN t2.DESCR_ITEM
                                    WHEN t1.Cd_NG IN (4) THEN t3.DESCR_ITEM 
                                    ELSE NULL 
                                END AS DESC_COD_ITEM,
                                t4.Txt_Cls_Custo AS DESC_CLS_CUSTO
                            FROM
                                ROA t1
                            LEFT JOIN LST_MAT t2 ON t1.COD_ITEM = t2.COD_ITEM 
                                AND t2.dt_ARQ = ? 
                            LEFT JOIN LST_SERV t3 ON t1.COD_ITEM = t3.COD_ITEM 
                                AND t3.dt_ARQ = ?
                            LEFT JOIN DSC_CLS_CUSTO t4 ON t1.Cd_Cls_Custo = t4.Cd_Cls_Custo 
                                AND t4.dt_ARQ = ?
                            WHERE 
                                t1.Cd_SubODI IN {lst_PRJ}
                                AND t1.dt_ARQ = ?
                        )

                        SELECT 
                            rb.Ide_RO_Analitico, rb.Cd_ODI, rb.Cd_SubODI, rb.Cd_Cls_Custo, rb.DESC_CLS_CUSTO, 
                            rb.COD_ITEM, rb.DESC_COD_ITEM, rb.Cd_NG, 
                            CASE 
                                WHEN rb.Cd_NG IN (1) THEN 'UC/UAR'
                                WHEN rb.Cd_NG IN (2) THEN 'COM'
                                WHEN rb.Cd_NG IN (3) THEN 'MOP'
                                WHEN rb.Cd_NG IN (4) THEN 'ST'
                                WHEN rb.Cd_NG IN (5) THEN 'JOA'
                                WHEN rb.Cd_NG IN (6) THEN 'Outros' 
                                ELSE NULL 
                            END AS DESC_NG,
                            rb.Cd_CA, 
                            CASE 
                                WHEN rb.Cd_CA IN (1) THEN 'Frete/Transporte'
                                WHEN rb.Cd_CA IN (2) THEN 'Projeto'
                                WHEN rb.Cd_CA IN (3) THEN 'Gerenciamento'
                                WHEN rb.Cd_CA IN (4) THEN 'Fiscalização'
                                WHEN rb.Cd_CA IN (5) THEN 'Montagem'
                                WHEN rb.Cd_CA IN (6) THEN 'Custo de Suporte' 
                                ELSE NULL 
                            END AS DESC_CA,
                            rb.FLG_PLPT, rb.Qtd, rb.Unidade, 
                            rb.VL_tot, rb.Dt_Lcmto, rb.Cd_Pedido, rb.Txt_Doc, rb.Nr_TI, rb.Nr_TUC,
                            rb.Nr_A1, rb.Nr_A2, rb.Nr_A3, rb.Nr_A4, rb.Nr_A5, rb.Nr_A6, 
                            rb.Txt_Nom_Forn, rb.Txt_NF as Nr_NF, rb.Txt_ItemNF as Nr_ItemNF, rb.Nr_SerieNF, rb.CNPJ_Forn, 
                            rb.FLG_DOA_OE, rb.FLG_INCOR_OE, rb.FLG_OAT, rb.Cd_ATIP, 
                            CASE 
                                WHEN rb.Cd_ATIP IN (1) THEN 'Expansão em linha viva'
                                WHEN rb.Cd_ATIP IN (2) THEN 'Recondutoramento de circuitos'
                                WHEN rb.Cd_ATIP IN (3) THEN 'Recapacitação de linhas'
                                WHEN rb.Cd_ATIP IN (4) THEN 'Instalação ou substituição de UAR que não seja a própria UC'
                                WHEN rb.Cd_ATIP IN (5) THEN 'Redes e linhas de distribuição subterrâneas ou submersas (todas as TUC associadas)'
                                WHEN rb.Cd_ATIP IN (6) THEN 'Estruturas tipo torre (TUC 255.02)' 
                                WHEN rb.Cd_ATIP IN (7) THEN 'Estruturas tipo poste em Linhas de Distribuição (TUC 255.01)'
                                WHEN rb.Cd_ATIP IN (8) THEN 'Sistemas especiais de medição'
                                WHEN rb.Cd_ATIP IN (9) THEN 'Novas tecnologias, ainda não modularizadas'
                                WHEN rb.Cd_ATIP IN (10) THEN 'Outros'
                                ELSE NULL 
                            END AS DESC_ATIP,
                            rb.Cd_AJST, rb.Cd_SubODI_MUT, rs.Txt_Desc_PRJ, rs.Cd_Tipo_Obra,
                            CASE 
                                WHEN rs.Cd_Tipo_Obra IN (1) THEN 'Ampliação/Expansão'
                                WHEN rs.Cd_Tipo_Obra IN (2) THEN 'Construção'
                                WHEN rs.Cd_Tipo_Obra IN (3,10) THEN 'Manutenção'
                                WHEN rs.Cd_Tipo_Obra IN (4) THEN 'Melhoria/Reforma'
                                WHEN rs.Cd_Tipo_Obra IN (5,6) THEN 'Administrativo'
                                WHEN rs.Cd_Tipo_Obra IN (7) THEN 'Incorporação'
                                WHEN rs.Cd_Tipo_Obra IN (8) THEN 'PEE'
                                WHEN rs.Cd_Tipo_Obra IN (9) THEN 'PeD'
                                WHEN rs.Cd_Tipo_Obra IN (11,12) THEN 'Medição'
                                ELSE NULL 
                            END AS Txt_TP_OBRA,
                            CASE 
                                WHEN rs.Cd_Tipo_Obra IN (1,2,4,5,7,8,9,10,11) THEN 'Investimento'
                                WHEN rs.Cd_Tipo_Obra IN (3,6,12) THEN 'Manutenção'
                                ELSE NULL 
                            END AS Txt_CLS_OBRA, 
                            rs.Dt_Inic_Proj, rs.Dt_Energ, rs.Dt_Uniti, rs.Pct_OE, 
                            rs.Nr_Fases, rs.VL_TEN, rs.Cd_ODD, rs.Txt_JUST_ODD, rs.Cd_Tipo_OE,
                            CASE 
                                WHEN rs.Cd_Tipo_OE IN (1) THEN 'NO'
                                WHEN rs.Cd_Tipo_OE IN (2) THEN 'PlPT'
                                WHEN rs.Cd_Tipo_OE IN (3) THEN 'MLA'
                                WHEN rs.Cd_Tipo_OE IN (4) THEN 'Subvenção de CCC'
                                WHEN rs.Cd_Tipo_OE IN (5) THEN 'Doações'
                                WHEN rs.Cd_Tipo_OE IN (6) THEN 'Participação Financeira do Consumidor' 
                                WHEN rs.Cd_Tipo_OE IN (7) THEN 'Repasses de Recursos dos Governos Federal, Estadual, Distrital e Municipal'
                                WHEN rs.Cd_Tipo_OE IN (8) THEN 'Incorporações'
                                WHEN rs.Cd_Tipo_OE IN (9) THEN 'Outros'
                                ELSE NULL 
                            END AS DESC_OE
                        FROM 
                            ROA_BASE rb
                        LEFT JOIN 
                            ROS rs ON rb.Cd_SubODI = rs.Cd_SubODI 
                            AND rs.dt_ARQ = ?
                    """
            params = [
                        'LST_MAT',
                        'LST_SERV',
                        'DSC_CLS_CUSTO',
                        'ROA',
                        'ROS'     
                    ]
            
            ROA = imp_tbl_forma_003(params, SQLq, con = con, st=st, Empresa=Empresa)
        except:
            try:
                SQLq = f"""
                            WITH 
                            ROA_BASE AS (
                                SELECT
                                    t1.*,
                                    CASE 
                                        WHEN t1.Cd_NG IN (1,2) THEN t2.DESCR_ITEM
                                        WHEN t1.Cd_NG IN (4) THEN t3.DESCR_ITEM 
                                        ELSE NULL 
                                    END AS DESC_COD_ITEM,
                                    '' AS DESC_CLS_CUSTO
                                FROM
                                    ROA t1
                                LEFT JOIN LST_MAT t2 ON t1.COD_ITEM = t2.COD_ITEM 
                                    AND t2.dt_ARQ = ? 
                                LEFT JOIN LST_SERV t3 ON t1.COD_ITEM = t3.COD_ITEM 
                                    AND t3.dt_ARQ = ?
                                WHERE 
                                    t1.Cd_SubODI IN {lst_PRJ}
                                    AND t1.dt_ARQ = ?
                            )

                            SELECT 
                                rb.Ide_RO_Analitico, rb.Cd_ODI, rb.Cd_SubODI, rb.Cd_Cls_Custo, rb.DESC_CLS_CUSTO, 
                                rb.COD_ITEM, rb.DESC_COD_ITEM, rb.Cd_NG, 
                                CASE 
                                    WHEN rb.Cd_NG IN (1) THEN 'UC/UAR'
                                    WHEN rb.Cd_NG IN (2) THEN 'COM'
                                    WHEN rb.Cd_NG IN (3) THEN 'MOP'
                                    WHEN rb.Cd_NG IN (4) THEN 'ST'
                                    WHEN rb.Cd_NG IN (5) THEN 'JOA'
                                    WHEN rb.Cd_NG IN (6) THEN 'Outros' 
                                    ELSE NULL 
                                END AS DESC_NG,
                                rb.Cd_CA, 
                                CASE 
                                    WHEN rb.Cd_CA IN (1) THEN 'Frete/Transporte'
                                    WHEN rb.Cd_CA IN (2) THEN 'Projeto'
                                    WHEN rb.Cd_CA IN (3) THEN 'Gerenciamento'
                                    WHEN rb.Cd_CA IN (4) THEN 'Fiscalização'
                                    WHEN rb.Cd_CA IN (5) THEN 'Montagem'
                                    WHEN rb.Cd_CA IN (6) THEN 'Custo de Suporte' 
                                    ELSE NULL 
                                END AS DESC_CA,
                                rb.FLG_PLPT, rb.Qtd, rb.Unidade, 
                                rb.VL_tot, rb.Dt_Lcmto, rb.Cd_Pedido, rb.Txt_Doc, rb.Nr_TI, rb.Nr_TUC,
                                rb.Nr_A1, rb.Nr_A2, rb.Nr_A3, rb.Nr_A4, rb.Nr_A5, rb.Nr_A6, 
                                rb.Txt_Nom_Forn, rb.Nr_NF, rb.Nr_ItemNF, rb.Nr_SerieNF, rb.CNPJ_Forn, 
                                rb.FLG_DOA_OE, rb.FLG_INCOR_OE, rb.FLG_OAT, rb.Cd_ATIP, 
                                CASE 
                                    WHEN rb.Cd_ATIP IN (1) THEN 'Expansão em linha viva'
                                    WHEN rb.Cd_ATIP IN (2) THEN 'Recondutoramento de circuitos'
                                    WHEN rb.Cd_ATIP IN (3) THEN 'Recapacitação de linhas'
                                    WHEN rb.Cd_ATIP IN (4) THEN 'Instalação ou substituição de UAR que não seja a própria UC'
                                    WHEN rb.Cd_ATIP IN (5) THEN 'Redes e linhas de distribuição subterrâneas ou submersas (todas as TUC associadas)'
                                    WHEN rb.Cd_ATIP IN (6) THEN 'Estruturas tipo torre (TUC 255.02)' 
                                    WHEN rb.Cd_ATIP IN (7) THEN 'Estruturas tipo poste em Linhas de Distribuição (TUC 255.01)'
                                    WHEN rb.Cd_ATIP IN (8) THEN 'Sistemas especiais de medição'
                                    WHEN rb.Cd_ATIP IN (9) THEN 'Novas tecnologias, ainda não modularizadas'
                                    WHEN rb.Cd_ATIP IN (10) THEN 'Outros'
                                    ELSE NULL 
                                END AS DESC_ATIP,
                                rb.Cd_AJST, rb.Cd_SubODI_MUT, rs.Txt_Desc_PRJ, rs.Cd_Tipo_Obra,
                                CASE 
                                    WHEN rs.Cd_Tipo_Obra IN (1) THEN 'Ampliação/Expansão'
                                    WHEN rs.Cd_Tipo_Obra IN (2) THEN 'Construção'
                                    WHEN rs.Cd_Tipo_Obra IN (3,10) THEN 'Manutenção'
                                    WHEN rs.Cd_Tipo_Obra IN (4) THEN 'Melhoria/Reforma'
                                    WHEN rs.Cd_Tipo_Obra IN (5,6) THEN 'Administrativo'
                                    WHEN rs.Cd_Tipo_Obra IN (7) THEN 'Incorporação'
                                    WHEN rs.Cd_Tipo_Obra IN (8) THEN 'PEE'
                                    WHEN rs.Cd_Tipo_Obra IN (9) THEN 'PeD'
                                    WHEN rs.Cd_Tipo_Obra IN (11,12) THEN 'Medição'
                                    ELSE NULL 
                                END AS Txt_TP_OBRA,
                                CASE 
                                    WHEN rs.Cd_Tipo_Obra IN (1,2,4,5,7,8,9,10,11) THEN 'Investimento'
                                    WHEN rs.Cd_Tipo_Obra IN (3,6,12) THEN 'Manutenção'
                                    ELSE NULL 
                                END AS Txt_CLS_OBRA, 
                                rs.Dt_Inic_Proj, rs.Dt_Energ, rs.Dt_Uniti, rs.Pct_OE, 
                                rs.Nr_Fases, rs.VL_TEN, rs.Cd_ODD, rs.Txt_JUST_ODD, rs.Cd_Tipo_OE,
                                CASE 
                                    WHEN rs.Cd_Tipo_OE IN (1) THEN 'NO'
                                    WHEN rs.Cd_Tipo_OE IN (2) THEN 'PlPT'
                                    WHEN rs.Cd_Tipo_OE IN (3) THEN 'MLA'
                                    WHEN rs.Cd_Tipo_OE IN (4) THEN 'Subvenção de CCC'
                                    WHEN rs.Cd_Tipo_OE IN (5) THEN 'Doações'
                                    WHEN rs.Cd_Tipo_OE IN (6) THEN 'Participação Financeira do Consumidor' 
                                    WHEN rs.Cd_Tipo_OE IN (7) THEN 'Repasses de Recursos dos Governos Federal, Estadual, Distrital e Municipal'
                                    WHEN rs.Cd_Tipo_OE IN (8) THEN 'Incorporações'
                                    WHEN rs.Cd_Tipo_OE IN (9) THEN 'Outros'
                                    ELSE NULL 
                                END AS DESC_OE
                            FROM 
                                ROA_BASE rb
                            LEFT JOIN 
                                ROS rs ON rb.Cd_SubODI = rs.Cd_SubODI 
                                AND rs.dt_ARQ = ?
                        """
                params = [
                            'LST_MAT',
                            'LST_SERV',
                            'ROA',
                            'ROS'     
                        ]
                ROA = imp_tbl_forma_003(params, SQLq, con = con, st=st, Empresa=Empresa)
            except Exception as e:
                raise UserWarning(e)

    for col in ['VL_tot','Qtd','VL_CA_ST_ODD','VL_CA_MOP_ODD','Pct_OE','VL_TEN']:
        if col in ROA.columns:
            ROA[col] = pd.to_numeric(ROA[col].astype(str).str.replace(',','.'), 
                                                        errors='coerce',
                                                        downcast='float')


    ROA_IMP = []
    progresso = st.progress(0, "Iniciando escolha de lançamentos..")
    lst_PRJ = list(lst_PRJ)
    tot_proj = len(lst_PRJ)
    for ip, PROJ in enumerate(lst_PRJ):
        progresso.progress(int(100*(ip+1)/tot_proj), f"Avaliando {PROJ}, {ip+1}/{tot_proj}")
        df_prov = ROA[ROA['Cd_SubODI']==PROJ].copy()
        df_amst = ams_lcmto(df_prov[["Ide_RO_Analitico", "Cd_NG", "COD_ITEM", "Cd_CA", "Qtd", 
                                     "Unidade", "VL_tot", "Dt_Lcmto"]], st=st)
        ROA_IMP.append(df_amst)
    progresso.empty()
    
    df_final = pd.concat(ROA_IMP, ignore_index=True)
    ROA = ROA.merge(df_final[["Ide_RO_Analitico","selecionado_fiscalizacao",
                             "criterio"]], how='left', on = "Ide_RO_Analitico")
    ROA['OBS_AJS'] = ""
    ROA['VL_AJS'] = 0
    ROA['VL_FISCALIZADO'] = 0

    if st: avl.progress(55, "Consolidando dados do ROA das Amostras...")
    worksheet2.merge_range('C5:AL5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
    formatos = {}
    lst_txt = []
    lst_moe = []
    lst_num = []
    lst_dt = []
    lst_pct = []
    for col, n in enumerate(ROA.columns):
        if n[:3].upper() in ['COD','TXT', 'CD_', 'FLG', 'TIP', 'CHV', 'CNP','DESC','UNI','NM_']:
            lst_txt.append(col)
        elif n[:3].upper() in ['VL_']:
            lst_moe.append(col)
        elif n[:3].upper() in ['QTD', 'CST', 'IND', 'NUM', 'ID_', 'SER']:
            lst_num.append(col)
        elif n[:3].upper() in ['DT_']:
            lst_dt.append(col)
        elif n[:3].upper() in ['ALI']:
            lst_pct.append(col)
        
    if len(lst_txt)>0:
        formatos[tuple(lst_txt)] = texto
    if len(lst_moe)>0:
        formatos[tuple(lst_moe)] = currency_format
    if len(lst_num)>0:
        formatos[tuple(lst_num)] = number_format
    if len(lst_dt)>0:
        formatos[tuple(lst_dt)] = data_format
    if len(lst_pct)>0:
        formatos[tuple(lst_pct)] = percentual_format
    

    x2 = ax_escreve_excel_md2(worksheet2, ROA, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)
    for row in range(linhasAMAIS+1, len(ROA) + linhasAMAIS + 1):
        worksheet2.write_formula(row, 59, f'=Q{row+1}-BG{row+1}', number_format)
    worksheet2.write(linhasAMAIS, 59, 'VL_AJUSTADO', titulo)

    fim = len(ROA) + linhasAMAIS + 1
    worksheet1.write(linhasAMAIS, 7, 'VL_FISC', titulo)
    worksheet1.write(linhasAMAIS, 8, 'SUP_INF_IA', titulo)
    worksheet1.write(linhasAMAIS, 9, 'DIFERENÇA', titulo)
    worksheet1.write(linhasAMAIS, 10, 'TIPO', titulo)
    worksheet1.write(linhasAMAIS, 11, 'ERRO', titulo)
    worksheet1.write(linhasAMAIS, 12, 'ERRO EXTRAPOLADO', titulo)
    worksheet1.write(linhasAMAIS, 13, 'ORDEM NEGATIVOS', titulo)
    worksheet1.write(linhasAMAIS, 14, 'FAP', titulo)
    worksheet1.write(linhasAMAIS, 15, 'AP', titulo)

    if st: avl.progress(65, "Preparando expansão do erro para a população...")
    for row in range(linhasAMAIS+1, len(df_PP) + linhasAMAIS + 1):
        worksheet1.write_formula(row, 7, f"=SUMIFS('DADOS_ROA'!BH8:BH{fim},'DADOS_ROA'!U8:U{fim},D{row+1},'DADOS_ROA'!E8:E{fim},C{row+1})", number_format)
        worksheet1.write_formula(row, 8, f'=IF(E{row+1}>=(G{row+1} - IF(F{row+1}<G{row+1},F{row+1},0)),"SUP","INF")', number_format)
        worksheet1.write_formula(row, 9, f"=E{row+1}-H{row+1}", number_format)
        worksheet1.write_formula(row, 10, f'=IF(J{row+1}>1, "MAIOR", IF(J{row+1}<-1, "MENOR", "OK"))', texto)
        worksheet1.write_formula(row, 11, f'=IF(AND(K{row+1}<>"OK",I{row+1}="SUP"),IFERROR((E{row+1} - H{row+1}), 0),0)', number_format)
        worksheet1.write_formula(row, 12, f'=IF(AND(K{row+1}<>"OK",I{row+1}="INF"),IFERROR((E{row+1} - H{row+1})/E{row+1}*(G{row+1}-F{row+1}), 0),0)', number_format)
        worksheet1.write_formula(row, 13, f'=IF(M{row+1}<0, RANK(M{row+1},M$8:M${len(df_PP) + linhasAMAIS + 1},1),IF(M{row+1}>0, RANK(M{row+1},M$8:M${len(df_PP) + linhasAMAIS + 1},0),0))', number_format)
        formula = f"=IF(N{row+1}=1,0.75,IF(N{row+1}=2,0.55,IF(N{row+1}=3,0.46,IF(N{row+1}=4,0.4,IF(N{row+1}=5,0.36,IF(N{row+1}=6,0.33,IF(N{row+1}=7,0.31,IF(N{row+1}=8,0.29,IF(N{row+1}=9,0.27,IF(NL{row+1}=10,0.26,IF(N{row+1}=0,0,0.26)))))))))))"
        worksheet1.write_formula(row, 14, formula, number_format)
        worksheet1.write_formula(row, 15, f"=M{row+1}*O{row+1}", number_format)

    worksheet3.merge_range('B1:D1', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
    fim = len(df_PP) + linhasAMAIS + 1
    worksheet3.write('B3', "Item", titulo)
    worksheet3.write('C3', "Valor", titulo)
    worksheet3.write('D3', "Diferença Aceitável", titulo)
    worksheet3.write('B4', 'Materialidade Ampla', texto)
    worksheet3.write('C4', MA, number_format)
    worksheet3.write('D4', 'NA', texto)
    worksheet3.write('B5', 'Materialidade Restrita', texto)
    worksheet3.write('C5', MA - MR, number_format)
    worksheet3.write('D5', 'NA', texto)
    worksheet3.write('B6', 'Erro Líquido Observado na Amostra', texto)
    worksheet3.write_formula('C6', f"=sum('RESUMO_SORTEIO'!L8:L{fim})", number_format)
    worksheet3.write('D6', 'NA', texto)
    worksheet3.write('B7', 'Erro Líquido Extrapolado para a População', texto)
    worksheet3.write_formula('C7', f"=sum('RESUMO_SORTEIO'!M8:M{fim})", number_format)
    worksheet3.write('D7', 'NA', texto)
    worksheet3.write('B8', 'ERRO SUPERESTIMADO', texto)
    worksheet3.write_formula('C8', f'=sumifs(RESUMO_SORTEIO!L8:L{fim},RESUMO_SORTEIO!L8:L{fim},">0")', number_format)
    worksheet3.write('D8', 'NA', texto)
    worksheet3.write('B9', 'ERRO SUBRESTIMADO', texto)
    worksheet3.write_formula('C9', f'=sumifs(RESUMO_SORTEIO!L8:L{fim},RESUMO_SORTEIO!L8:L{fim},"<0")', number_format)
    worksheet3.write('D9', 'NA', texto)
    worksheet3.write('B10', 'AIP SUPERESTIMADO', texto)
    worksheet3.write_formula('C10', f'=sumifs(RESUMO_SORTEIO!P8:P{fim},RESUMO_SORTEIO!P8:P{fim},">0")', number_format)
    worksheet3.write('D10', 'NA', texto)
    worksheet3.write('B11', 'AIP SUBESTIMADO', texto)
    worksheet3.write_formula('C11', f'=sumifs(RESUMO_SORTEIO!P8:P{fim},RESUMO_SORTEIO!P8:P{fim},"<0")', number_format)
    worksheet3.write('D11', 'NA', texto)
    worksheet3.write('B12', 'LIMITE SUPERIOR ERROS SUPERESTIMADOS', texto)
    worksheet3.write_formula('C12', f'=C5+C7+C8+C10', number_format)
    worksheet3.write('D12', 'NA', texto)
    worksheet3.write('B13', 'LIMITE SUPERIOR ERROS SUBESTIMADOS', texto)
    worksheet3.write_formula('C13', f'=-C5+C7+C9+C11', number_format)
    worksheet3.write('D13', 'NA', texto)
    worksheet3.write('B14', 'DIFERENÇA ERROS SUPERESTIMADOS', texto)
    worksheet3.write_formula('C14', f'=C4-C12', number_format)
    worksheet3.write_formula('D14', f'=IF(C14>0,"SIM","NÃO")', texto)
    worksheet3.write('B15', 'DIFERENÇA ERROS SUBESTIMADOS', texto)
    worksheet3.write_formula('C15', f'=-C4-C13', number_format)
    worksheet3.write_formula('D15', f'=IF(C15<0,"SIM","NÃO")', texto)
    worksheet3.hide_gridlines(2)
    worksheet3.set_column(1,1, 30)
    worksheet3.set_column(2,2, 16)
    worksheet3.set_column(3,3, 30)

    def esc_anl_ca(ws1=None, fim=12, nm_plan = 'DADOS_ROA'):
        ws1.merge_range('B1:D1', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
        ws1.merge_range('B3:B4', "Cd_SubODI", titulo)
        ws1.merge_range('C3:C4', "Nome Obra", titulo)
        ws1.merge_range('D3:E3', "UC/UAR", titulo)
        ws1.write('D4', "Qtd", titulo)
        ws1.write('E4', "Valor", titulo)
        ws1.merge_range('F3:G3', "COM", titulo)
        ws1.write('F4', "Qtd", titulo)
        ws1.write('G4', "Valor", titulo)
        ws1.merge_range('H3:O3', "MOP", titulo)
        ws1.write('H4', "Frete/Transporte", titulo)
        ws1.write('I4', "Projeto", titulo)
        ws1.write('J4', "Gerenciamento", titulo)
        ws1.write('K4', "Fiscalização", titulo)
        ws1.write('L4', "Montagem", titulo)
        ws1.write('M4', "Custo de Suporte", titulo)
        ws1.write('N4', "Direto", titulo)
        ws1.write('O4', "Indireto", titulo)
        ws1.merge_range('P3:W3', "ST", titulo)
        ws1.write('P4', "Frete/Transporte", titulo)
        ws1.write('Q4', "Projeto", titulo)
        ws1.write('R4', "Gerenciamento", titulo)
        ws1.write('S4', "Fiscalização", titulo)
        ws1.write('T4', "Montagem", titulo)
        ws1.write('U4', "Custo de Suporte", titulo)
        ws1.write('V4', "Direto", titulo)
        ws1.write('W4', "Indireto", titulo)
        ws1.write('X3', "Custos Diretos", titulo)
        ws1.write('X4', "UC + COM + MOP + ST", titulo)
        ws1.write('Y3', "Custos Indiretos", titulo)
        ws1.write('Y4', "MOP + ST", titulo)
        ws1.write('Z3', "TESTE 01", titulo)
        ws1.write('Z4', "(MOP_IND + ST_IND) / (UC + COM + MOP_DIR + ST_DIR)", titulo)
        ws1.write('AA3', "TESTE 02", titulo)
        ws1.write('AA4', "(MOP_IND + ST_IND) / (MOP_IND + ST_IND + MOP_DIR + ST_DIR)", titulo)
        ws1.merge_range('AB3:AG3', "PERCENTUAL DE MOP SOBRE CUSTOS DIRETOS", titulo)
        ws1.write('AB4', "Frete/Transporte", titulo)
        ws1.write('AC4', "Projeto", titulo)
        ws1.write('AD4', "Gerenciamento", titulo)
        ws1.write('AE4', "Fiscalização", titulo)
        ws1.write('AF4', "Montagem", titulo)
        ws1.write('AG4', "Custo de Suporte", titulo)
        ws1.merge_range('AH3:AM3', "PERCENTUAL DE ST SOBRE CUSTOS DIRETOS", titulo)
        ws1.write('AH4', "Frete/Transporte", titulo)
        ws1.write('AI4', "Projeto", titulo)
        ws1.write('AJ4', "Gerenciamento", titulo)
        ws1.write('AK4', "Fiscalização", titulo)
        ws1.write('AL4', "Montagem", titulo)
        ws1.write('AM4', "Custo de Suporte", titulo)

        for l1, n in enumerate(lst_PRJ):
            ws1.write(f'B{5+l1}', n, texto)
            ws1.write(f'C{5+l1}', f'=VLOOKUP(B{5+l1},{nm_plan}!E8:AO{fim},37,FALSE)', texto)
            ws1.write_formula(f'D{5+l1}', f'=sumifs({nm_plan}!O8:O{fim},{nm_plan}!E8:E{fim},B{5+l1},{nm_plan}!J8:J{fim},"1")', number_format)
            ws1.write_formula(f'E{5+l1}', f'=sumifs({nm_plan}!Q8:Q{fim},{nm_plan}!E8:E{fim},B{5+l1},{nm_plan}!J8:J{fim},"1")', number_format)
            ws1.write_formula(f'F{5+l1}', f'=sumifs({nm_plan}!O8:O{fim},{nm_plan}!E8:E{fim},B{5+l1},{nm_plan}!J8:J{fim},"2")', number_format)
            ws1.write_formula(f'G{5+l1}', f'=sumifs({nm_plan}!Q8:Q{fim},{nm_plan}!E8:E{fim},B{5+l1},{nm_plan}!J8:J{fim},"2")', number_format)

            for i1 in range(1,7):
                ws1.write_formula(4+l1, 6+i1, f'=sumifs({nm_plan}!Q8:Q{fim},{nm_plan}!E8:E{fim},B{5+l1},{nm_plan}!J8:J{fim},"3",{nm_plan}!L8:L{fim},"{i1}")', number_format)
                ws1.write_formula(4+l1, 14+i1, f'=sumifs({nm_plan}!Q8:Q{fim},{nm_plan}!E8:E{fim},B{5+l1},{nm_plan}!J8:J{fim},"4",{nm_plan}!L8:L{fim},"{i1}")', number_format)
            ws1.write_formula(4+l1, 13, f'=sumifs({nm_plan}!Q8:Q{fim},{nm_plan}!E8:E{fim},B{5+l1},{nm_plan}!J8:J{fim},"3",{nm_plan}!L8:L{fim},"5")', number_format)
            ws1.write_formula(
                                4 + l1,
                                14,
                                f'=SUMIFS({nm_plan}!Q8:Q{fim},{nm_plan}!E8:E{fim},B{5+l1},{nm_plan}!J8:J{fim},"3")'
                                f'-SUMIFS({nm_plan}!Q8:Q{fim},{nm_plan}!E8:E{fim},B{5+l1},{nm_plan}!J8:J{fim},"3",{nm_plan}!L8:L{fim},"5")', 
                                number_format
                            )
            ws1.write_formula(4+l1, 21, f'=sumifs({nm_plan}!Q8:Q{fim},{nm_plan}!E8:E{fim},B{5+l1},{nm_plan}!J8:J{fim},"4",{nm_plan}!L8:L{fim},"5")', number_format)
            ws1.write_formula(
                                4 + l1,
                                22,
                                f'=SUMIFS({nm_plan}!Q8:Q{fim},{nm_plan}!E8:E{fim},B{5+l1},{nm_plan}!J8:J{fim},"4")'
                                f'-SUMIFS({nm_plan}!Q8:Q{fim},{nm_plan}!E8:E{fim},B{5+l1},{nm_plan}!J8:J{fim},"4",{nm_plan}!L8:L{fim},"5")', 
                                number_format
                            )
            ws1.write_formula(f'X{5+l1}', f'=E{5+l1}+G{5+l1}+N{5+l1}+V{5+l1}', number_format)
            ws1.write_formula(f'Y{5+l1}', f'=O{5+l1}+W{5+l1}', number_format)
            ws1.write_formula(f'Z{5+l1}', f'=if(X{5+l1}=0,0,(O{5+l1}+W{5+l1})/X{5+l1})', percentual_format)
            ws1.write_formula(f'AA{5+l1}',
                              f'=IF((O{5+l1}+W{5+l1}+N{5+l1}+V{5+l1})=0,0,(O{5+l1}+W{5+l1})/(O{5+l1}+W{5+l1}+N{5+l1}+V{5+l1}))',
                              percentual_format)
            for i1 in range(1,7):
                colA = xl_col_to_name(6+i1)
                colB = xl_col_to_name(14+i1)
                ws1.write_formula(4+l1, 26+i1, f'=if(X{5+l1}=0,0,{colA}{5+l1}/X{5+l1})', percentual_format)
                ws1.write_formula(4+l1, 32+i1, f'=if(X{5+l1}=0,0,{colB}{5+l1}/X{5+l1})', percentual_format)
            
        ws1.hide_gridlines(2)
        ws1.set_column(2,80, 16)
        ws1.set_column(2,2, 45)
        

    esc_anl_ca(ws1=ws1, fim=(len(ROA) + linhasAMAIS + 1))

    if st: avl.progress(85, "Buscando ROD das Amostras...")
    lst_PRJd = tuple(ROA[ROA['Cd_ODD'].notnull()]['Cd_ODD'].unique())

    try:
        try:
            SQLq = f"""
                        WITH 
                        ROD_BASE AS (
                            SELECT
                                t1.*,
                                CASE 
                                    WHEN t1.Cd_NG IN (1,2) THEN t2.DESCR_ITEM
                                    WHEN t1.Cd_NG IN (4) THEN t3.DESCR_ITEM 
                                    ELSE NULL 
                                END AS DESC_COD_ITEM,
                                t4.Txt_Cls_Custo AS DESC_CLS_CUSTO
                            FROM
                                ROD t1
                            LEFT JOIN LST_MAT t2 ON t1.COD_ITEM = t2.COD_ITEM 
                                AND t2.dt_ARQ = ? 
                            LEFT JOIN LST_SERV t3 ON t1.COD_ITEM = t3.COD_ITEM 
                                AND t3.dt_ARQ = ?
                            LEFT JOIN DSC_CLS_CUSTO t4 ON t1.Cd_Cls_Custo = t4.Cd_Cls_Custo 
                                AND t4.dt_ARQ = ?
                            WHERE 
                                t1.Cd_ODD IN {lst_PRJd}
                                AND t1.dt_ARQ = ?
                        )

                        SELECT 
                            rb.Ide_RO_Analitico, rb.Cd_ODI, rb.Cd_ODD, rb.Cd_Cls_Custo, rb.DESC_CLS_CUSTO, 
                            rb.COD_ITEM, rb.DESC_COD_ITEM, rb.Cd_NG, 
                            CASE 
                                WHEN rb.Cd_NG IN (1) THEN 'UC/UAR'
                                WHEN rb.Cd_NG IN (2) THEN 'COM'
                                WHEN rb.Cd_NG IN (3) THEN 'MOP'
                                WHEN rb.Cd_NG IN (4) THEN 'ST'
                                WHEN rb.Cd_NG IN (5) THEN 'JOA'
                                WHEN rb.Cd_NG IN (6) THEN 'Outros' 
                                ELSE NULL 
                            END AS DESC_NG,
                            rb.Cd_CA, 
                            CASE 
                                WHEN rb.Cd_CA IN (1) THEN 'Frete/Transporte'
                                WHEN rb.Cd_CA IN (2) THEN 'Projeto'
                                WHEN rb.Cd_CA IN (3) THEN 'Gerenciamento'
                                WHEN rb.Cd_CA IN (4) THEN 'Fiscalização'
                                WHEN rb.Cd_CA IN (5) THEN 'Montagem'
                                WHEN rb.Cd_CA IN (6) THEN 'Custo de Suporte' 
                                ELSE NULL 
                            END AS DESC_CA,
                            rb.FLG_PLPT, rb.Qtd, rb.Unidade, 
                            rb.VL_tot, rb.Dt_Lcmto, rb.Nr_TI, rb.Nr_TUC,
                            rb.Nr_A1, rb.Nr_A2, rb.Nr_A3, rb.Nr_A4, rb.Nr_A5, rb.Nr_A6, 
                            rb.Txt_Nom_Forn, rb.Nr_NF, rb.Nr_ItemNF, rb.Nr_SerieNF, rb.CNPJ_Forn, 
                            rs.Txt_Desc_PRJ, rs.Cd_Tipo_Obra,
                            CASE 
                                WHEN rs.Cd_Tipo_Obra IN (1) THEN 'Ampliação/Expansão'
                                WHEN rs.Cd_Tipo_Obra IN (2) THEN 'Construção'
                                WHEN rs.Cd_Tipo_Obra IN (3,10) THEN 'Manutenção'
                                WHEN rs.Cd_Tipo_Obra IN (4) THEN 'Melhoria/Reforma'
                                WHEN rs.Cd_Tipo_Obra IN (5,6) THEN 'Administrativo'
                                WHEN rs.Cd_Tipo_Obra IN (7) THEN 'Incorporação'
                                WHEN rs.Cd_Tipo_Obra IN (8) THEN 'PEE'
                                WHEN rs.Cd_Tipo_Obra IN (9) THEN 'PeD'
                                WHEN rs.Cd_Tipo_Obra IN (11,12) THEN 'Medição'
                                ELSE NULL 
                            END AS Txt_TP_OBRA,
                            CASE 
                                WHEN rs.Cd_Tipo_Obra IN (1,2,4,5,7,8,9,10,11) THEN 'Investimento'
                                WHEN rs.Cd_Tipo_Obra IN (3,6,12) THEN 'Manutenção'
                                ELSE NULL 
                            END AS Txt_CLS_OBRA, 
                            rs.Dt_Inic_Proj, rs.Dt_Energ, rs.Dt_Uniti, rs.Pct_OE, 
                            rs.Nr_Fases, rs.VL_TEN, rs.Cd_SubODI, rs.Txt_JUST_ODD, rs.Cd_Tipo_OE,
                            CASE 
                                WHEN rs.Cd_Tipo_OE IN (1) THEN 'NO'
                                WHEN rs.Cd_Tipo_OE IN (2) THEN 'PlPT'
                                WHEN rs.Cd_Tipo_OE IN (3) THEN 'MLA'
                                WHEN rs.Cd_Tipo_OE IN (4) THEN 'Subvenção de CCC'
                                WHEN rs.Cd_Tipo_OE IN (5) THEN 'Doações'
                                WHEN rs.Cd_Tipo_OE IN (6) THEN 'Participação Financeira do Consumidor' 
                                WHEN rs.Cd_Tipo_OE IN (7) THEN 'Repasses de Recursos dos Governos Federal, Estadual, Distrital e Municipal'
                                WHEN rs.Cd_Tipo_OE IN (8) THEN 'Incorporações'
                                WHEN rs.Cd_Tipo_OE IN (9) THEN 'Outros'
                                ELSE NULL 
                            END AS DESC_OE
                        FROM 
                            ROD_BASE rb
                        LEFT JOIN 
                            ROS rs ON rb.Cd_ODD = rs.Cd_ODD 
                            AND rs.dt_ARQ = ?
                    """
            params = [
                        'LST_MAT',
                        'LST_SERV',
                        'DSC_CLS_CUSTO',
                        'ROD',
                        'ROS'     
                    ]

            ROD = imp_tbl_forma_003(params, SQLq, con = con, st=st, Empresa=Empresa)
        except:
            SQLq = f"""
                    WITH 
                    ROD_BASE AS (
                        SELECT
                            t1.*,
                            CASE 
                                WHEN t1.Cd_NG IN (1,2) THEN t2.DESCR_ITEM
                                WHEN t1.Cd_NG IN (4) THEN t3.DESCR_ITEM 
                                ELSE NULL 
                            END AS DESC_COD_ITEM,
                            '' AS DESC_CLS_CUSTO
                        FROM
                            ROD t1
                        LEFT JOIN LST_MAT t2 ON t1.COD_ITEM = t2.COD_ITEM 
                            AND t2.dt_ARQ = ? 
                        LEFT JOIN LST_SERV t3 ON t1.COD_ITEM = t3.COD_ITEM 
                            AND t3.dt_ARQ = ?
                        WHERE 
                            t1.Cd_ODD IN {lst_PRJd}
                            AND t1.dt_ARQ = ?
                    )

                    SELECT 
                        rb.Ide_RO_Analitico, rb.Cd_ODI, rb.Cd_ODD, rb.Cd_Cls_Custo, rb.DESC_CLS_CUSTO, 
                        rb.COD_ITEM, rb.DESC_COD_ITEM, rb.Cd_NG, 
                        CASE 
                            WHEN rb.Cd_NG IN (1) THEN 'UC/UAR'
                            WHEN rb.Cd_NG IN (2) THEN 'COM'
                            WHEN rb.Cd_NG IN (3) THEN 'MOP'
                            WHEN rb.Cd_NG IN (4) THEN 'ST'
                            WHEN rb.Cd_NG IN (5) THEN 'JOA'
                            WHEN rb.Cd_NG IN (6) THEN 'Outros' 
                            ELSE NULL 
                        END AS DESC_NG,
                        rb.Cd_CA, 
                        CASE 
                            WHEN rb.Cd_CA IN (1) THEN 'Frete/Transporte'
                            WHEN rb.Cd_CA IN (2) THEN 'Projeto'
                            WHEN rb.Cd_CA IN (3) THEN 'Gerenciamento'
                            WHEN rb.Cd_CA IN (4) THEN 'Fiscalização'
                            WHEN rb.Cd_CA IN (5) THEN 'Montagem'
                            WHEN rb.Cd_CA IN (6) THEN 'Custo de Suporte' 
                            ELSE NULL 
                        END AS DESC_CA,
                        rb.FLG_PLPT, rb.Qtd, rb.Unidade, 
                        rb.VL_tot, rb.Dt_Lcmto, rb.Nr_TI, rb.Nr_TUC,
                        rb.Nr_A1, rb.Nr_A2, rb.Nr_A3, rb.Nr_A4, rb.Nr_A5, rb.Nr_A6, 
                        rb.Txt_Nom_Forn, rb.Nr_NF, rb.Nr_ItemNF, rb.Nr_SerieNF, rb.CNPJ_Forn, 
                        rs.Txt_Desc_PRJ, rs.Cd_Tipo_Obra,
                        CASE 
                            WHEN rs.Cd_Tipo_Obra IN (1) THEN 'Ampliação/Expansão'
                            WHEN rs.Cd_Tipo_Obra IN (2) THEN 'Construção'
                            WHEN rs.Cd_Tipo_Obra IN (3,10) THEN 'Manutenção'
                            WHEN rs.Cd_Tipo_Obra IN (4) THEN 'Melhoria/Reforma'
                            WHEN rs.Cd_Tipo_Obra IN (5,6) THEN 'Administrativo'
                            WHEN rs.Cd_Tipo_Obra IN (7) THEN 'Incorporação'
                            WHEN rs.Cd_Tipo_Obra IN (8) THEN 'PEE'
                            WHEN rs.Cd_Tipo_Obra IN (9) THEN 'PeD'
                            WHEN rs.Cd_Tipo_Obra IN (11,12) THEN 'Medição'
                            ELSE NULL 
                        END AS Txt_TP_OBRA,
                        CASE 
                            WHEN rs.Cd_Tipo_Obra IN (1,2,4,5,7,8,9,10,11) THEN 'Investimento'
                            WHEN rs.Cd_Tipo_Obra IN (3,6,12) THEN 'Manutenção'
                            ELSE NULL 
                        END AS Txt_CLS_OBRA, 
                        rs.Dt_Inic_Proj, rs.Dt_Energ, rs.Dt_Uniti, rs.Pct_OE, 
                        rs.Nr_Fases, rs.VL_TEN, rs.Cd_SubODI, rs.Txt_JUST_ODD, rs.Cd_Tipo_OE,
                        CASE 
                            WHEN rs.Cd_Tipo_OE IN (1) THEN 'NO'
                            WHEN rs.Cd_Tipo_OE IN (2) THEN 'PlPT'
                            WHEN rs.Cd_Tipo_OE IN (3) THEN 'MLA'
                            WHEN rs.Cd_Tipo_OE IN (4) THEN 'Subvenção de CCC'
                            WHEN rs.Cd_Tipo_OE IN (5) THEN 'Doações'
                            WHEN rs.Cd_Tipo_OE IN (6) THEN 'Participação Financeira do Consumidor' 
                            WHEN rs.Cd_Tipo_OE IN (7) THEN 'Repasses de Recursos dos Governos Federal, Estadual, Distrital e Municipal'
                            WHEN rs.Cd_Tipo_OE IN (8) THEN 'Incorporações'
                            WHEN rs.Cd_Tipo_OE IN (9) THEN 'Outros'
                            ELSE NULL 
                        END AS DESC_OE
                    FROM 
                        ROD_BASE rb
                    LEFT JOIN 
                        ROS rs ON rb.Cd_ODD = rs.Cd_ODD 
                        AND rs.dt_ARQ = ?
                """
        params = [
                    'LST_MAT',
                    'LST_SERV',
                    'ROD',
                    'ROS'     
                ]

        ROD = imp_tbl_forma_003(params, SQLq, con = con, st=st, Empresa=Empresa)
    except:
        SQLq = f"""
                        WITH 
                        ROD_BASE AS (
                            SELECT
                                t1.*,
                                CASE 
                                    WHEN t1.Cd_NG IN (1,2) THEN t2.DESCR_ITEM
                                    WHEN t1.Cd_NG IN (4) THEN t3.DESCR_ITEM 
                                    ELSE NULL 
                                END AS DESC_COD_ITEM,
                                t4.Txt_Cls_Custo AS DESC_CLS_CUSTO
                            FROM
                                ROD t1
                            LEFT JOIN LST_MAT t2 ON t1.COD_ITEM = t2.COD_ITEM 
                                AND t2.dt_ARQ = ? 
                            LEFT JOIN LST_SERV t3 ON t1.COD_ITEM = t3.COD_ITEM 
                                AND t3.dt_ARQ = ?
                            LEFT JOIN DSC_CLS_CUSTO t4 ON t1.Cd_Cls_Custo = t4.Cd_Cls_Custo 
                                AND t4.dt_ARQ = ?
                            WHERE 
                                t1.Cd_ODD IN {lst_PRJd}
                                AND t1.dt_ARQ = ?
                        )

                        SELECT 
                            rb.Ide_RO_Analitico, rb.Cd_ODI, rb.Cd_ODD, rb.Cd_Cls_Custo, rb.DESC_CLS_CUSTO, 
                            rb.COD_ITEM, rb.DESC_COD_ITEM, rb.Cd_NG, 
                            CASE 
                                WHEN rb.Cd_NG IN (1) THEN 'UC/UAR'
                                WHEN rb.Cd_NG IN (2) THEN 'COM'
                                WHEN rb.Cd_NG IN (3) THEN 'MOP'
                                WHEN rb.Cd_NG IN (4) THEN 'ST'
                                WHEN rb.Cd_NG IN (5) THEN 'JOA'
                                WHEN rb.Cd_NG IN (6) THEN 'Outros' 
                                ELSE NULL 
                            END AS DESC_NG,
                            rb.Cd_CA, 
                            CASE 
                                WHEN rb.Cd_CA IN (1) THEN 'Frete/Transporte'
                                WHEN rb.Cd_CA IN (2) THEN 'Projeto'
                                WHEN rb.Cd_CA IN (3) THEN 'Gerenciamento'
                                WHEN rb.Cd_CA IN (4) THEN 'Fiscalização'
                                WHEN rb.Cd_CA IN (5) THEN 'Montagem'
                                WHEN rb.Cd_CA IN (6) THEN 'Custo de Suporte' 
                                ELSE NULL 
                            END AS DESC_CA,
                            rb.FLG_PLPT, rb.Qtd, rb.Unidade, 
                            rb.VL_tot, rb.Dt_Lcmto, rb.Nr_TI, rb.Nr_TUC,
                            rb.Nr_A1, rb.Nr_A2, rb.Nr_A3, rb.Nr_A4, rb.Nr_A5, rb.Nr_A6, 
                            rb.Txt_Nom_Forn, rb.Nr_NF, rb.Nr_ItemNF, rb.Nr_SerieNF, rb.CNPJ_Forn, 
                            rs.Txt_Desc_PRJ, rs.Cd_Tipo_Obra,
                            CASE 
                                WHEN rs.Cd_Tipo_Obra IN (1) THEN 'Ampliação/Expansão'
                                WHEN rs.Cd_Tipo_Obra IN (2) THEN 'Construção'
                                WHEN rs.Cd_Tipo_Obra IN (3,10) THEN 'Manutenção'
                                WHEN rs.Cd_Tipo_Obra IN (4) THEN 'Melhoria/Reforma'
                                WHEN rs.Cd_Tipo_Obra IN (5,6) THEN 'Administrativo'
                                WHEN rs.Cd_Tipo_Obra IN (7) THEN 'Incorporação'
                                WHEN rs.Cd_Tipo_Obra IN (8) THEN 'PEE'
                                WHEN rs.Cd_Tipo_Obra IN (9) THEN 'PeD'
                                WHEN rs.Cd_Tipo_Obra IN (11,12) THEN 'Medição'
                                ELSE NULL 
                            END AS Txt_TP_OBRA,
                            CASE 
                                WHEN rs.Cd_Tipo_Obra IN (1,2,4,5,7,8,9,10,11) THEN 'Investimento'
                                WHEN rs.Cd_Tipo_Obra IN (3,6,12) THEN 'Manutenção'
                                ELSE NULL 
                            END AS Txt_CLS_OBRA, 
                            rs.Dt_Inic_Proj, rs.Dt_Energ, rs.Dt_Uniti, rs.Pct_OE, 
                            rs.Nr_Fases, rs.VL_TEN, rs.Cd_SubODI, rs.Txt_JUST_ODD, rs.Cd_Tipo_OE,
                            CASE 
                                WHEN rs.Cd_Tipo_OE IN (1) THEN 'NO'
                                WHEN rs.Cd_Tipo_OE IN (2) THEN 'PlPT'
                                WHEN rs.Cd_Tipo_OE IN (3) THEN 'MLA'
                                WHEN rs.Cd_Tipo_OE IN (4) THEN 'Subvenção de CCC'
                                WHEN rs.Cd_Tipo_OE IN (5) THEN 'Doações'
                                WHEN rs.Cd_Tipo_OE IN (6) THEN 'Participação Financeira do Consumidor' 
                                WHEN rs.Cd_Tipo_OE IN (7) THEN 'Repasses de Recursos dos Governos Federal, Estadual, Distrital e Municipal'
                                WHEN rs.Cd_Tipo_OE IN (8) THEN 'Incorporações'
                                WHEN rs.Cd_Tipo_OE IN (9) THEN 'Outros'
                                ELSE NULL 
                            END AS DESC_OE
                        FROM 
                            ROD_BASE rb
                        LEFT JOIN 
                            ROS rs ON rb.Cd_ODD = rs.Cd_ODD 
                            AND rs.dt_ARQ = ?
                    """
        params = [
                    'LST_MAT',
                    'LST_SERV',
                    'DSC_CLS_CUSTO',
                    'ROD',
                    'ROS'     
                ]
        ROD = imp_tbl_forma_003(params, SQLq, con = con, st=st, Empresa=Empresa)


    for col in ['VL_tot','Qtd','VL_CA_ST_ODD','VL_CA_MOP_ODD','Pct_OE','VL_TEN']:
        if col in ROD.columns:
            ROD[col] = pd.to_numeric(ROD[col].astype(str).str.replace(',','.'), 
                                                        errors='coerce',
                                                        downcast='float')
    ROD_IMP = []
    progresso = st.progress(0, "Iniciando escolha de lançamentos..")
    lst_PRJ = list(lst_PRJd)
    tot_proj = len(lst_PRJd)
    for ip, PROJ in enumerate(lst_PRJd):
        progresso.progress(int(100*(ip+1)/tot_proj), f"Avaliando {PROJ}, {ip+1}/{tot_proj}")
        df_prov = ROD[ROD['Cd_ODD']==PROJ].copy()
        df_amst = ams_lcmto(df_prov[["Ide_RO_Analitico", "Cd_NG", "COD_ITEM", "Cd_CA", "Qtd", 
                                     "Unidade", "VL_tot", "Dt_Lcmto"]], st=st)
        ROD_IMP.append(df_amst)
    progresso.empty()
    
    df_final = pd.concat(ROD_IMP, ignore_index=True)
    
    ROD = ROD.merge(df_final[["Ide_RO_Analitico","selecionado_fiscalizacao",
                             "criterio"]], how='left', on = "Ide_RO_Analitico")
    if len(ROD)>1000000:
        st.warning("Verifique se uma ODD foi empregada em mais de uma SubODI.")
        workbook.close()
        return
    ROD['OBS_AJS'] = ""
    ROD['VL_AJS'] = 0
    ROD['VL_FISCALIZADO'] = 0

    worksheet4.merge_range('C5:AL5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
    formatos = {}
    lst_txt = []
    lst_moe = []
    lst_num = []
    lst_dt = []
    lst_pct = []
    for col, n in enumerate(ROD.columns):
        if n[:3].upper() in ['COD','TXT', 'CD_', 'FLG', 'TIP', 'CHV', 'CNP','DESC','UNI','NM_']:
            lst_txt.append(col)
        elif n[:3].upper() in ['VL_']:
            lst_moe.append(col)
        elif n[:3].upper() in ['QTD', 'CST', 'IND', 'NUM', 'ID_', 'SER']:
            lst_num.append(col)
        elif n[:3].upper() in ['DT_']:
            lst_dt.append(col)
        elif n[:3].upper() in ['ALI']:
            lst_pct.append(col)
        
    if len(lst_txt)>0:
        formatos[tuple(lst_txt)] = texto
    if len(lst_moe)>0:
        formatos[tuple(lst_moe)] = currency_format
    if len(lst_num)>0:
        formatos[tuple(lst_num)] = number_format
    if len(lst_dt)>0:
        formatos[tuple(lst_dt)] = data_format
    if len(lst_pct)>0:
        formatos[tuple(lst_pct)] = percentual_format
    
    x2 = ax_escreve_excel_md2(worksheet4, ROD, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)
    for row in range(linhasAMAIS+1, len(ROD) + linhasAMAIS + 1):
        worksheet4.write_formula(row, 50, f'=Q{row+1}-AX{row+1}', number_format)
    worksheet4.write(linhasAMAIS, 50, 'VL_AJUSTADO', titulo)

    
    workbook.close()
    if st: avl.progress(100, f"Finalizado e guardado em {dir_arq_saida}/Saida_AMS_F0.xlsx!")
    return "OK"

def imprimi_F0_CRONO(df_CAB, df_DG, df_PP, dir_arq_saida, Empresa, st=None):

    if st:
        avl = st.progress(0, "Iniciando exportação para excel...")

    workbook = xlsxwriter.Workbook(f'{dir_arq_saida}/Saida_CRONO_F0.xlsx', {"nan_inf_to_errors": True})

    worksheet1 = workbook.add_worksheet('CAPA')
    worksheet2 = workbook.add_worksheet('ATIVIDADES')
    worksheet3 = workbook.add_worksheet('GANTT ESTATICO')
    workbook.set_calc_mode('auto')

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo = workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'valign':'vcenter', 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    linhasAMAIS=8
    if st:
        avl.progress(5, "Criando aba com os dados da equipe...")
     
    linhasAMAIS = 8
    worksheet1.merge_range('C5:F5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
    worksheet1.write(linhasAMAIS-1, 2,'Dados do trabalho',titulo2)
    formatos = {
                    (2,3,4,5,6,7): data_format,

                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {
                        (2, 37): 8, (2, 4): 20
                      }

    x1 = ax_escreve_excel(worksheet1, df_CAB, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    linhasAMAIS = 13
    worksheet1.write(linhasAMAIS-1, 2,'Dados da equipe e datas do trabalho',titulo2)
    x2 = ax_escreve_excel(worksheet1, df_DG, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    nm_img = rf"{st.session_state.tra_dir}/RELATORIOS/figuras/grantt.png"
    if os.path.exists(nm_img):
        worksheet3.insert_image('B3', nm_img)
        worksheet3.hide_gridlines(2)

    if st:
        avl.progress(25, "Criando aba com as atividades de trabalho...")

    linhasAMAIS = 8
    worksheet2.merge_range('C5:M5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
    worksheet2.write(linhasAMAIS-1, 2,'Dados das atividades do trabalho',titulo2)
    formatos = {
                    (2,3,4,5,6,7): data_format,

                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {
                        (2, 12): 8, (2, 2): 88, (3, 4): 40,
                        (12, 12): 88
                      }
    df_PP['Dt_INI'] = pd.to_datetime(df_PP['Dt_INI'], format = '%d/%m/%Y', errors = 'coerce')
    df_PP['Dt_FIM'] = pd.to_datetime(df_PP['Dt_FIM'], format = '%d/%m/%Y', errors = 'coerce')
            

    x1 = ax_escreve_excel(worksheet2, df_PP, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    
    if st: avl.progress(100, "Finalizado!")
    
    workbook.close()
    if st:
        avl.progress(100, f"Finalizado e guardado em {dir_arq_saida}/Saida_AMS_F0.xlsx!")

    return "OK"


def imprimi_F0_CVA(bd, data_ini, data_fim, st=None, tipo = "MF"):

    if st:
        avl = st.progress(0, "Iniciando exportação para excel...")

    diret = f'{st.session_state.tra_dir}/CVA/CONC_ECD_BP'

    if not os.path.exists(diret):
        os.makedirs(diret)

    cursor = bd.cursor()
    tabAX = cursor.execute("""SELECT name 
                              FROM sqlite_master 
                              WHERE type='table' AND name LIKE 'TAB_CONC_ECD_BP%'""").fetchall()
    tabelas = [row[0] for row in tabAX]

    if len(tabelas):
        selo = datetime.now().strftime('%Y%m%d%H%M')
        workbook = xlsxwriter.Workbook(f'{diret}/Saida_VAL_F0_{st.session_state.nm_empr}_{selo}.xlsx', {"nan_inf_to_errors": True})
        workbook.set_calc_mode('auto')
        currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
        percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
        data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
        titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'valign':'center', 'align':'center','bold': True}) 
        texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
        tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
        titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
        number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
        linhasAMAIS=8
        df_itens = pd.read_csv("tabelas/tbl_itens_CVA.csv", sep="|", encoding="latin-1", dtype={"COD_CTA": str})

        for i, n in enumerate(tabelas):
            bsc = df_itens.iloc[int(n[n.rfind("_") + 1:]),-1]

            if st:
                avl.progress(int(100/len(tabelas) * i), f"Criando aba {bsc}...")
            wb = workbook.add_worksheet(bsc)
            wb.merge_range('C5:AD5', f'CÁLCULO PROVISÓRIO {st.session_state.nm_empr}', tituloP)
            wb.write(linhasAMAIS-1, 2, f'Resultado da Conciliação entre BP e ECD, {bsc}',titulo2)
            SQLq = f"SELECT * FROM {n}"
            df = pd.read_sql(SQLq, bd)
            #df = df.fillna("ND")
            datas = (i for i in df.columns.to_list() if i.startswith(("DT","Dth","Dt")))
            valores = (i for i in df.columns.to_list() if i.startswith(("VL","Vl","Vlr")))
            formatos = {
                            valores : currency_format,
                            datas : data_format
                        }

            colunas_largura = {
                                (2, 45): 10, (3, 4): 13, (5, 6): 35, (12, 14): 35, (15, 15): 74, (20, 25): 40,
                                (29, 31): 58
                            }
            

            x1 = ax_escreve_excel(wb, df, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
            #wb.set_column(2, 23, 15)
            wb.hide_gridlines(2)

            if tipo == "MF":
                wb = workbook.add_worksheet(f"{bsc}_AGREG")
                wb.merge_range('C5:F5', f'CÁLCULO PROVISÓRIO {st.session_state.nm_empr}', tituloP)
                wb.write(linhasAMAIS-1, 2, f'Resultado Agregado da Conciliação entre BP e ECD, {bsc}',titulo2)

                df['DT_LCTO_A'] = pd.to_datetime(df['DT_LCTO_A'], errors='coerce')
                df['DT_LCTO_B'] = pd.to_datetime(df['DT_LCTO_B'], errors='coerce')
                dfG1 = (df.groupby(df["DT_LCTO_A"].dt.to_period("M"), dropna=False)['VL_DC_A']
                        .sum()
                        .reset_index()
                        .rename(columns = {'DT_LCTO_A' : 'DT_LCTO'}))

                dfG2 = (df.groupby(df["DT_LCTO_B"].dt.to_period("M"), dropna=False)['VL_DC_B']
                        .sum()
                        .reset_index()
                        .rename(columns = {'DT_LCTO_B' : 'DT_LCTO'}))

                dfG1 = (dfG1
                        .merge(dfG2, how = 'outer', on = 'DT_LCTO', suffixes = ("_ECD","_BP"))
                        .rename(columns = {'VL_DC_B' : 'VL_DC_BP', 'VL_DC_A' : 'VL_DC_ECD'}))

                dfG1['VL_DC_ECD'] = dfG1['VL_DC_ECD'].fillna(0)
                dfG1['VL_DC_BP'] = dfG1['VL_DC_BP'].fillna(0)
                dfG1['DT_LCTO'] = dfG1['DT_LCTO'].fillna(0).astype(str)
                dfG1['DELTA'] = dfG1['VL_DC_ECD'] - dfG1['VL_DC_BP']

                formatos = {
                                (1,2,3) : currency_format,
                            }

                colunas_largura = {
                                    (2, 5): 10, 
                                }
                

                x1 = ax_escreve_excel(wb, dfG1, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
                
                #wb.set_column(2, 23, 15)
                wb.hide_gridlines(2)
        if st:
            avl.progress(100, f"Finalizado e guardado em {diret}/Saida_VAL_F0_{st.session_state.nm_empr}.xlsx!")
        avl.empty()
        workbook.close()
    else:
        st.warning("Necessário processar antes de imprimir resultado!")
    

    return "OK"


def imprimi_F1_CVA(df1, dic, data_ini, data_fim, st=None):

    if st:
        avl = st.progress(0, "Iniciando exportação para excel...")

    diret = f'{st.session_state.tra_dir}/CVA/REG'

    if not os.path.exists(diret):
        os.makedirs(diret)

    workbook = xlsxwriter.Workbook(f'{diret}/Saida_VAL_F1.xlsx', {"nan_inf_to_errors": True})

    worksheet1 = workbook.add_worksheet('LST_ARQ_BP')
    workbook.set_calc_mode('auto')

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'valign':'center', 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    
    diferenca = relativedelta(data_fim, data_ini)
    meses_totais = diferenca.years * 12 + diferenca.months
    
    linhasAMAIS=8
    if st:
        avl.progress(5, "Criando aba com os dados dos arquivos do BP empregados...")
     
    linhasAMAIS = 8
    worksheet1.merge_range('C5:AD5', f'CÁLCULO PROVISÓRIO {st.session_state.nm_empr}', tituloP)
    worksheet1.write(linhasAMAIS-1, 2,'Informações dos arquivos do banco de pagamentos utilizados',titulo2)
    formatos = {
                    (1,2,27,29) : data_format
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {
                        (2, 29): 10, (3, 4): 13, (5, 6): 35, (12, 14): 35, (15, 15): 74, (20, 25): 40,
                        (27, 29): 18
                      }

    x1 = ax_escreve_excel(worksheet1, df1, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)

    if st:
        avl.progress(10, "Buscando dados do banco de pagamentos...")

    f3 = 0
    dic_arq = {
                'Energia' : [ {
                                (6,7,8): currency_format,
                                (12,): number_format,
                                (2,3,18,20) : data_format
                             }, 
                             {
                                (2, 22): 18, (13, 13): 35, (15, 15): 35, (17, 19): 40,
                             }, 0
                             ],
                'RB' : [{
                            (6,7,): currency_format,
                            #(12,): number_format,
                            (2,3,16,18) : data_format
                        }, 
                        {
                            (2, 20): 18, (12, 12): 35, (14, 17): 40,
                        }, 0
                        ],
                'PROINFA' : [ {
                                (6,): currency_format,
                                #(12,): number_format,
                                (2,3,14,16) : data_format
                              }, 
                              {
                                (2, 18): 18, (11, 11): 35, (13, 16): 40
                              }, 18
                            ],
                'CDE' : [ {
                            (6,): currency_format,
                            #(12,): number_format,
                            (2,3,14,16) : data_format
                          }, 
                          {
                            (2, 18): 18, (11, 11): 35, (13, 16): 40
                          }, 15
                            ],
                'CDE_ENERGIA' : [ {
                            (6,): currency_format,
                            #(12,): number_format,
                            (2,3,14,16) : data_format
                          }, 
                          {
                            (2, 18): 18, (11, 11): 35, (13, 16): 40
                          }, 25
                            ],
                'CFURH' : [ {
                            (6,): currency_format,
                            #(12,): number_format,
                            (2,3,14,16) : data_format
                          }, 
                          {
                            (2, 18): 18, (11, 11): 35, (13, 16): 40
                          }, 0
                            ],
                'Itaipu' : [ {
                            (6,): currency_format,
                            #(12,): number_format,
                            (2,3,14,16) : data_format
                          }, 
                          {
                            (2, 18): 18, (11, 11): 35, (13, 16): 40
                          }, 0
                            ]
                }
    LST_ITENS = []

    if 'Energia' in dic:
        if dic['Energia']['NumContrato'].dtype == 'object':
            dic['Energia']['NumContrato'] = pd.to_numeric(dic['Energia']['NumContrato'], errors='coerce').fillna(0).astype(int)

    for key, value in dic.items():
        if st:
            avl.progress(int(10 + 50/len(dic) * f3), f'Informações dos arquivos do BP para {key}')
        worksheet3 = workbook.add_worksheet(f'BP_{key}')
        worksheet3.merge_range('C5:W5', f'CÁLCULO PROVISÓRIO {st.session_state.nm_empr}', tituloP)
        worksheet3.write(linhasAMAIS-1, 2, f'Informações dos arquivos do BP para {key}',titulo2)
        formatos = dic_arq[key][0]
        
        #Configuração otimizada de largura de colunas
        colunas_largura = dic_arq[key][1]
        nm_col = [ix for ix in value.columns if ix[:2]=="Dt"]
        for nm in nm_col:
            if value[nm].dtype == 'object':
                value[nm] = value[nm].str[8:10] + "/" +  value[nm].str[5:7] + "/" + value[nm].str[:4]

        x3 = ax_escreve_excel(worksheet3, value[(value['DthEfetivaPagamento'] >= (data_ini - DateOffset(months=2))) &
                             (value['DthEfetivaPagamento'] < (data_fim + DateOffset(months=2)))], linhasAMAIS, formatos, 
                             colunas_largura, texto, titulo, st=st)
        f3 += 1
        if key not in ['Energia','RB','Itaipu']:
            LST_ITENS += [key]

    df_EncREH = pd.read_csv("BD_CVA_REG/BD_EncREH.csv", sep='|', encoding='latin-1')
    df_EncREH['COD SRE'] = pd.to_numeric(df_EncREH['COD SRE'], errors='coerce')
    if df_EncREH['Montante'].dtype == 'object':
        df_EncREH['Montante'] = pd.to_numeric(df_EncREH['Montante'].str.replace(",","."), errors='coerce')
    df_EncREHCOVID = pd.read_csv("BD_CVA_REG/CDE_COVID.csv", sep='|', encoding='latin-1')
    df_DADEMP = bsc_cd_TODOS(st.session_state.nm_empr)
    
    df_EncREHCOVID = df_EncREHCOVID[df_EncREHCOVID['Id_Agente'].isin(df_DADEMP['Cd_ANEEL'].drop_duplicates().to_list())]
    df_EncREH = df_EncREH[df_EncREH['COD SRE'].isin(df_DADEMP['Cd_SGT'].drop_duplicates().to_list())]

    etapa = 0
    for item in LST_ITENS:
        if item in dic:
            if st:
                avl.progress(int(60 + 40/len(dic) * etapa), f"Criando aba com os dados de {item}...")
            nrPRO = len(dic[item]) + 10 if item in dic else 0
            

            df_PROV_REG = df_EncREH[df_EncREH['Id Detalhe Grupo Tarifa'] == dic_arq[item][2]].copy()
            
            df_resultado = (
                                df_PROV_REG.groupby(['Legenda encargo', 'Encargo', 'Vigência'], as_index=False)
                                .agg({'Montante': 'sum'})
                            )
            df_resultado = df_resultado.sort_values(by='Vigência', ascending=True)
            df_resultado.columns = ['LegENC', 'Encargo', 'DT_REH', 'VL_ANUAL']
            
            if df_resultado['DT_REH'].dtype == 'object':
                df_resultado['DT_REH'] = pd.to_datetime(df_resultado['DT_REH'].str[:10].str.replace("/","-"), format = "%Y-%m-%d", errors='coerce')
            if df_resultado['VL_ANUAL'].dtype == 'object':
                df_resultado['VL_ANUAL'] = pd.to_numeric(df_resultado['VL_ANUAL'].str.replace(".","").str.replace(",","."), errors='coerce')

            nrPROa = len(df_resultado) + 11 if item in dic else 0

            wbCVA = workbook.add_worksheet(f'CVA_{item}')
            wbCVA.merge_range('C5:F5', f'CÁLCULO PROVISÓRIO {st.session_state.nm_empr}', tituloP)
            wbCVA.write(linhasAMAIS + 1,2, f'Análise de pagamento contra regulatório: {item}.',titulo2)
            wbCVA.write(linhasAMAIS + 2,2,"Dt_CMPT", titulo)
            wbCVA.write(linhasAMAIS + 2,3,"VL_BP", titulo)
            wbCVA.write(linhasAMAIS + 2,4,"VL_REG", titulo)
            wbCVA.write(linhasAMAIS + 2,5,"DELTA", titulo)

            wbCVA.write(linhasAMAIS + 1,7, f'Tabela de dados de valor regulatório para: {item}.',titulo2)
            wbCVA.write(linhasAMAIS + 2,7,"LegENC", titulo)
            wbCVA.write(linhasAMAIS + 2,8,"Encargo", titulo)
            wbCVA.write(linhasAMAIS + 2,9,"DT_VIG", titulo)
            wbCVA.write(linhasAMAIS + 2,10,"VL_ANUAL", titulo)
            
            for n1 in range(len(df_resultado)):
                try:
                    wbCVA.write(linhasAMAIS+3+n1, 7, df_resultado.iloc[n1,0], texto)
                    wbCVA.write(linhasAMAIS+3+n1, 8, df_resultado.iloc[n1,1].upper(), texto)
                    wbCVA.write(linhasAMAIS+3+n1, 9, df_resultado.iloc[n1,2], data_format)
                    wbCVA.write(linhasAMAIS+3+n1, 10, df_resultado.iloc[n1,3], number_format)
                except:
                    pass

            if item == "CDE":
                df_EncREHCOVID['Encargo'] = "CDE COVID"
                df_resultadoC = (
                                    df_EncREHCOVID.groupby(['Nm_ATO', 'Encargo', 'DT_VIG'], as_index=False)
                                    .agg({'VL_AN_CDE_COVID': 'sum'})
                                )
                df_resultadoC = df_resultadoC.sort_values(by='DT_VIG', ascending=True)
                df_resultadoC.columns = ['LegENC', 'Encargo', 'DT_REH', 'VL_ANUAL']

                if df_resultadoC['DT_REH'].dtype == 'object':
                    df_resultadoC['DT_REH'] = pd.to_datetime(df_resultadoC['DT_REH'].str[:10].str.replace("-","/"), format = "%Y/%m/%d", errors='coerce')
                if df_resultadoC['VL_ANUAL'].dtype == 'object':
                    df_resultadoC['VL_ANUAL'] = pd.to_numeric(df_resultadoC['VL_ANUAL'].str.replace(".","").str.replace(",","."), errors='coerce')

                nrPROaC = len(df_resultadoC) + 11 if item in dic else 0


                wbCVA.write(linhasAMAIS + 1,12, f'Tabela de dados de valor regulatório para: {item} COVID.',titulo2)
                wbCVA.write(linhasAMAIS + 2,12,"LegENC", titulo)
                wbCVA.write(linhasAMAIS + 2,13,"Encargo", titulo)
                wbCVA.write(linhasAMAIS + 2,14,"DT_VIG", titulo)
                wbCVA.write(linhasAMAIS + 2,15,"VL_ANUAL", titulo)

                for n1 in range(len(df_resultado)):
                    try:
                        wbCVA.write(linhasAMAIS+3+n1, 12, df_resultadoC.iloc[n1,0], texto)
                        wbCVA.write(linhasAMAIS+3+n1, 13, df_resultadoC.iloc[n1,1].upper(), texto)
                        wbCVA.write(linhasAMAIS+3+n1, 14, df_resultadoC.iloc[n1,2], data_format)
                        wbCVA.write(linhasAMAIS+3+n1, 15, df_resultadoC.iloc[n1,3], number_format)
                    except:
                        pass

            for n1 in range(meses_totais):
                wbCVA.write(linhasAMAIS+3+n1, 2, (data_ini + relativedelta(months=n1)).replace(day=1), data_format)
                wbCVA.write(
                                    linhasAMAIS + 3 + n1, 
                                    3, 
                                    f'''=SUMPRODUCT(
                                            (MONTH(BP_{item}!E10:E{nrPRO})=MONTH(C{12+n1}))*
                                            (YEAR(BP_{item}!E10:E{nrPRO})=YEAR(C{12+n1}))*
                                            (BP_{item}!I10:I{nrPRO})
                                        )
                                        ''', 
                                    currency_format
                                )
                if item == "CDE":
                    wbCVA.write(
                                        linhasAMAIS + 3 + n1, 
                                        4, 
                                        f'''=IFERROR(
                                                        (VLOOKUP(C{12+n1}, J10:K{nrPROa}, 2, TRUE) + IFERROR(VLOOKUP(C{12+n1}, O10:P{nrPROaC}, 2, TRUE),0)) / 12 *
                                                        IF(((YEAR(C{12+n1}) -  YEAR(J{nrPROa})) * 12 + MONTH(C{12+n1}) -  MONTH(J{nrPROa})) > 12, 0, 1),
                                                        0
                                                    )
                                            ''', 
                                        currency_format
                                    )
                else:
                    wbCVA.write(
                                        linhasAMAIS + 3 + n1, 
                                        4, 
                                        f'''=IFERROR(
                                                        VLOOKUP(C{12+n1}, J10:K{nrPROa}, 2, TRUE) / 12 *
                                                        IF(((YEAR(C{12+n1}) -  YEAR(J{nrPROa})) * 12 + MONTH(C{12+n1}) -  MONTH(J{nrPROa})) > 12, 0, 1),
                                                        0
                                                    )
                                            ''', 
                                        currency_format
                                    )
                
                wbCVA.write(
                                    linhasAMAIS + 3 + n1, 
                                    5, 
                                    f'''= E{12+n1} - D{12+n1}
                                    ''', 
                                    currency_format
                                )
                wbCVA.set_column(2, 23, 15)
                wbCVA.set_column(7, 7, 52)
                wbCVA.set_column(12, 12, 52)
                wbCVA.hide_gridlines(2)
            etapa += 1
    item = "Itaipu"
    if item in dic:
        if st:
            avl.progress(int(60 + 40/len(dic) * etapa), f"Criando aba com os dados de {item}...")
        nrPRO = len(dic[item]) + 10 if item in dic else 0

        df_TARIT = pd.read_csv("BD_CVA_REG/BD_TarITAIPU.csv", sep='|', encoding='latin-1')
        df_SRG = pd.read_csv("BD_CVA_REG/BD_SRGITAIPU.csv", sep='|', encoding='latin-1')
        df_PIT = pd.read_csv("BD_CVA_REG/BD_PrITAIPU.csv", sep='|', encoding='latin-1')

        df_SRG = df_SRG[df_SRG['COD SAMP'].isin(df_DADEMP['Cd_ANEEL'].drop_duplicates().to_list())][['Montante',
                                                                                                     'Referência',
                                                                                                     'NOTA']]

        wbCVA = workbook.add_worksheet(f'CVA_{item}')
        wbCVA.merge_range('C5:F5', f'CÁLCULO PROVISÓRIO {st.session_state.nm_empr}', tituloP)
        wbCVA.write(linhasAMAIS + 1,2, f'Análise de pagamento contra regulatório: {item}.',titulo2)
        wbCVA.write(linhasAMAIS + 2,2,"Dt_CMPT", titulo)
        wbCVA.write(linhasAMAIS + 2,3,"VL_BP", titulo)
        wbCVA.write(linhasAMAIS + 2,4,"VL_REG", titulo)
        wbCVA.write(linhasAMAIS + 2,5,"DELTA", titulo)


        wbCVA.write(linhasAMAIS + 1,7, f'Tabela de dados de valor regulatório para tarifa de {item}.',titulo2)
        wbCVA.write(linhasAMAIS + 2,7,"Dt_REF", titulo)
        wbCVA.write(linhasAMAIS + 2,8,"VL_TAR", titulo)
        wbCVA.write(linhasAMAIS + 2,9,"Txt_DOC", titulo)

        wbCVA.write(linhasAMAIS + 1,11, f'Tabela de dados de valor regulatório para montante de {item}.',titulo2)
        wbCVA.write(linhasAMAIS + 2,11,"Dt_REF", titulo)
        wbCVA.write(linhasAMAIS + 2,12,"VL_MONT", titulo)
        wbCVA.write(linhasAMAIS + 2,13,"Txt_DOC", titulo)

        if df_TARIT['Data Vigência'].dtype == 'object':
            df_TARIT['Data Vigência'] = pd.to_datetime(df_TARIT['Data Vigência'].str[:10], format = "%Y-%m-%d", errors='coerce')
        if df_TARIT['TR ITAIPU'].dtype == 'object':
            df_TARIT['TR ITAIPU'] = pd.to_numeric(df_TARIT['TR ITAIPU'].str.replace(".","").str.replace(",","."), errors='coerce')

        df_TARIT = df_TARIT.sort_values(by='Data Vigência', ascending=True)
        nrPROaC = len(df_TARIT) + 11 if item in dic else 0

        if df_SRG['Referência'].dtype == 'object':
            df_SRG['Referência'] = pd.to_datetime(df_SRG['Referência'].str[:10], format = "%Y-%m-%d", errors='coerce')
        if df_SRG['Montante'].dtype == 'object':
            df_SRG['Montante'] = pd.to_numeric(df_SRG['Montante'].str.replace(".","").str.replace(",","."), errors='coerce')

        df_SRG = df_SRG.sort_values(by='Referência', ascending=True)
        nrPROaD = len(df_SRG) + 11 if item in dic else 0

        for n1 in range(len(df_TARIT)):
            try:
                wbCVA.write(linhasAMAIS+3+n1, 7, df_TARIT.iloc[n1,0], data_format)
                wbCVA.write(linhasAMAIS+3+n1, 8, df_TARIT.iloc[n1,1], number_format)
                wbCVA.write(linhasAMAIS+3+n1, 9, df_TARIT.iloc[n1,2], texto)
            except:
                pass
        
        for n1 in range(len(df_SRG)):
            try:
                wbCVA.write(linhasAMAIS+3+n1, 11, df_SRG.iloc[n1,1], data_format)
                wbCVA.write(linhasAMAIS+3+n1, 12, df_SRG.iloc[n1,0], number_format)
                wbCVA.write(linhasAMAIS+3+n1, 13, df_SRG.iloc[n1,2], texto)
            except:
                pass

        for n1 in range(meses_totais):
            wbCVA.write(linhasAMAIS+3+n1, 2, (data_ini + relativedelta(months=n1)).replace(day=1), data_format)
            wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                3, 
                                f'''=SUMPRODUCT(
                                        (MONTH(BP_{item}!E10:E{nrPRO})=MONTH(C{12+n1}))*
                                        (YEAR(BP_{item}!E10:E{nrPRO})=YEAR(C{12+n1}))*
                                        (BP_{item}!I10:I{nrPRO})
                                    )
                                    ''', 
                                currency_format
                            )
            
            wbCVA.write(
                            linhasAMAIS + 3 + n1, 
                            4, 
                            f'''=IFERROR(
                                            VLOOKUP(C{12+n1}, H10:I{nrPROaC}, 2, TRUE) * VLOOKUP(C{12+n1}, L10:M{nrPROaD}, 2, FALSE) * (1 / (1 - 0.0925)) *
                                            IF(((YEAR(C{12+n1}) -  YEAR(H{nrPROaC})) * 12 + MONTH(C{12+n1}) -  MONTH(H{nrPROaC})) > 12, 0, 1) *
                                            IF(((YEAR(C{12+n1}) -  YEAR(L{nrPROaD})) * 12 + MONTH(C{12+n1}) -  MONTH(L{nrPROaD})) > 12, 0, 1),
                                            0
                                        )
                                ''', 
                            currency_format
                        )
            wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                5, 
                                f'''= E{12+n1} - D{12+n1}
                                ''', 
                                currency_format
                            )
            wbCVA.set_column(2, 23, 15)
            wbCVA.set_column(9, 9, 52)
            wbCVA.set_column(13, 13, 52)
            wbCVA.hide_gridlines(2)

        etapa += 1

    item = "RB"
    if item in dic:
        if st:
            avl.progress(int(60 + 40/len(dic) * etapa), f"Criando aba com os dados de {item}...")
        nrPRO = len(dic[item]) + 10 if item in dic else 0


        AvisoDebito = pd.read_sas("BD_CVA_REG/AvisoDebito.sas7bdat")
        InformacaoAgente = pd.read_sas("BD_CVA_REG/InformacaoAgente.sas7bdat")
        AgenteCredor = pd.read_sas("BD_CVA_REG/agentecredor.sas7bdat")


        try:
            AvisoDebito['AnmApuracao'] = AvisoDebito['AnmApuracao'].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
        except:
            AvisoDebito['AnmApuracao'] = AvisoDebito['AnmApuracao'].apply(lambda x: x.decode('latin1') if isinstance(x, bytes) else x)

        for col in ['DthEmissao', 'DthPrimeiraParcela', 'DthSegundaParcela', 'DthTerceiraParcela']:
            if AvisoDebito[col] .dtype == 'object':
                AvisoDebito[col] = pd.to_datetime(AvisoDebito[col], errors='coerce')

        AvisoDebito['DT_CMPT'] = pd.to_datetime({
                                        'year': AvisoDebito['AnmApuracao'].str[:4],
                                        'month': AvisoDebito['AnmApuracao'].str[4:],
                                        'day': 1
                                    })
        COD_ONS = tuple(df_DADEMP['Cd_ONS'].drop_duplicates().to_list())

        #Dados da empresa que estamos trabalhando
        BD_EXTERNO_ONSa = (
                            AvisoDebito
                            .merge(InformacaoAgente, on='IdeInformacaoAgente', how='inner')
                            .query("IdeONSApuracao in @COD_ONS and DT_CMPT >= @data_ini and DT_CMPT <= @data_fim")
                            .rename(columns={
                                'DthEmissao': 'DT_EMIS',
                                'DthPrimeiraParcela': 'DT_P1',
                                'DthSegundaParcela': 'DT_P2',
                                'DthTerceiraParcela': 'DT_P3'
                            })
                            [[
                                'IdeAvisoDebito', 'DscRazaoSocial', 'IdeONSApuracao','DT_P1', 'DT_P2','DT_P3',
                                'DT_CMPT'
                            ]]
                        )

        BD_EXTERNO_ONSa = (
                            AgenteCredor
                            .merge(BD_EXTERNO_ONSa, on='IdeAvisoDebito', how='inner', suffixes = ("","_PROV"))
                            .rename(columns={
                                'DscRazaoSocial': 'SIGLA',
                                'IdeAvisoDebito': 'Nr_AVD',
                                'IdeONSApuracao': 'CodigoAgente',
                                'VlrPrimeiraParcela': 'VL_P1',
                                'VlrSegundaParcela': 'VL_P2',
                                'VlrTerceiraParcela': 'VL_P3',
                                'VlrRedeBasica' : 'VL_RB',
                                'VlrTotalFronteira' : 'VL_FR',
                                'VlrTotalTributosFed': 'VL_TOT_TRIB',
                                'PctRedeBasica' : 'Pct_RB'
                            })
                            [[
                                'DT_CMPT', 'SIGLA', 'Nr_AVD', 'CodigoAgente', 'IdeInformacaoAgente','DT_P1', 'DT_P2','DT_P3',
                                'VL_P1', 'VL_P2', 'VL_P3', 'VL_RB', 'VL_FR', 'VL_TOT_TRIB', 'Pct_RB'
                                
                            ]]
                        )
        
        
        BD_EXTERNO_ONSa['VL_TOT'] = BD_EXTERNO_ONSa['VL_P1'] + BD_EXTERNO_ONSa['VL_P2'] + BD_EXTERNO_ONSa['VL_P3']

        BD_EXTERNO_ONSa = (BD_EXTERNO_ONSa
                        .merge(InformacaoAgente[['IdeInformacaoAgente','IdeONSApuracao','DscRazaoSocial',
                                                   'NumCNPJAgente']], how = 'left', on = 'IdeInformacaoAgente')
                          .rename(columns={
                                'DscRazaoSocial': 'Nm_Transm',
                                'IdeONSApuracao': 'Cd_Transm',
                                'NumCNPJAgente': 'Cd_CNPJ_Transm'
                            })                         
                          )[[
                              'DT_CMPT', 'SIGLA', 'Nr_AVD', 'CodigoAgente', 'Cd_Transm', 'Nm_Transm', 'Cd_CNPJ_Transm',
                              'DT_P1', 'DT_P2','DT_P3', 'VL_P1', 'VL_P2', 'VL_P3', 'VL_RB', 'VL_FR', 
                              'VL_TOT_TRIB', 'VL_TOT', 'Pct_RB'

                          ]]
        
        for col in BD_EXTERNO_ONSa.select_dtypes([object]):
            try:
                BD_EXTERNO_ONSa[col] = BD_EXTERNO_ONSa[col].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
            except:
                BD_EXTERNO_ONSa[col] = BD_EXTERNO_ONSa[col].apply(lambda x: x.decode('latin1') if isinstance(x, bytes) else x)
        

        wbCVA = workbook.add_worksheet(f'CVA_{item}')
        wbCVA.merge_range('C5:F5', f'CÁLCULO PROVISÓRIO {st.session_state.nm_empr}', tituloP)
        wbCVA.write(linhasAMAIS + 1,2, f'Análise de pagamento contra regulatório: {item}.',titulo2)
        wbCVA.write(linhasAMAIS + 2,2,"Dt_CMPT", titulo)
        wbCVA.write(linhasAMAIS + 2,3,"VL_BP", titulo)
        wbCVA.write(linhasAMAIS + 2,4,"VL_REG", titulo)
        wbCVA.write(linhasAMAIS + 2,5,"DELTA", titulo)

        wbCVA.write(linhasAMAIS + 1,7, f'Análise de pagamento contra regulatório, por transmissora: {item}.',titulo2)
        wbCVA.write(linhasAMAIS + 2,7,"Dt_CMPT", titulo)
        wbCVA.write(linhasAMAIS + 2,8,"Cd_ONS", titulo)
        wbCVA.write(linhasAMAIS + 2,9,"VL_BP", titulo)
        wbCVA.write(linhasAMAIS + 2,10,"DELTA", titulo)


        wbCVA.write(linhasAMAIS + 1,12, f'Dados regulatórios para {item}.',titulo2)
        wbCVA.write(linhasAMAIS + 2,12,"Dt_REF", titulo)
        wbCVA.write(linhasAMAIS + 2,13,"SIGLA", titulo)
        wbCVA.write(linhasAMAIS + 2,14,"Nr_AVD", titulo)
        wbCVA.write(linhasAMAIS + 2,15,"CodigoAgente", titulo)
        wbCVA.write(linhasAMAIS + 2,16,"Cd_Transm", titulo)
        wbCVA.write(linhasAMAIS + 2,17,"Nm_Transm", titulo)
        wbCVA.write(linhasAMAIS + 2,18,"Cd_CNPJ_Transm", titulo)
        wbCVA.write(linhasAMAIS + 2,19,"DT_P1", titulo)
        wbCVA.write(linhasAMAIS + 2,20,"DT_P2", titulo)
        wbCVA.write(linhasAMAIS + 2,21,"DT_P3", titulo)
        wbCVA.write(linhasAMAIS + 2,22,"VL_P1", titulo)
        wbCVA.write(linhasAMAIS + 2,23,"VL_P2", titulo)
        wbCVA.write(linhasAMAIS + 2,24,"VL_P3", titulo)
        wbCVA.write(linhasAMAIS + 2,25,"VL_RB", titulo)
        wbCVA.write(linhasAMAIS + 2,26,"VL_FR", titulo)
        wbCVA.write(linhasAMAIS + 2,27,"VL_TOT_TRIB", titulo)
        wbCVA.write(linhasAMAIS + 2,28,"VL_TOT", titulo)
        wbCVA.write(linhasAMAIS + 2,29,"Pct_RB", titulo)

        for n1 in range(len(BD_EXTERNO_ONSa)):
            try:
                wbCVA.write(linhasAMAIS+3+n1, 12, BD_EXTERNO_ONSa.iloc[n1,0], data_format)
                wbCVA.write(linhasAMAIS+3+n1, 7, BD_EXTERNO_ONSa.iloc[n1,0], data_format)
                wbCVA.write(linhasAMAIS+3+n1, 8, BD_EXTERNO_ONSa.iloc[n1,4], texto)

                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                9, 
                                f'''=SUMPRODUCT(
                                        (MONTH(BP_{item}!E10:E{nrPRO})=MONTH(H{12+n1}))*
                                        (YEAR(BP_{item}!E10:E{nrPRO})=YEAR(H{12+n1}))*
                                        (BP_{item}!K10:K{nrPRO}=I{12+n1})*
                                        (BP_{item}!I10:I{nrPRO})) +

                                    SUMPRODUCT(
                                        (MONTH(BP_{item}!E10:E{nrPRO})=MONTH(H{12+n1}))*
                                        (YEAR(BP_{item}!E10:E{nrPRO})=YEAR(H{12+n1}))*
                                        (BP_{item}!K10:K{nrPRO}=I{12+n1})*
                                        (BP_{item}!J10:J{nrPRO})
                                    )
                                    ''', 
                                currency_format
                            )

                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                10, 
                                f'''= AC{12+n1} - J{12+n1}
                                ''', 
                                currency_format
                            )
                
                wbCVA.write(linhasAMAIS+3+n1, 13, BD_EXTERNO_ONSa.iloc[n1,1].upper(), texto)
                wbCVA.write(linhasAMAIS+3+n1, 14, BD_EXTERNO_ONSa.iloc[n1,2], texto)
                wbCVA.write(linhasAMAIS+3+n1, 15, BD_EXTERNO_ONSa.iloc[n1,3], texto)
                wbCVA.write(linhasAMAIS+3+n1, 16, BD_EXTERNO_ONSa.iloc[n1,4], texto)
                wbCVA.write(linhasAMAIS+3+n1, 17, BD_EXTERNO_ONSa.iloc[n1,5], texto)
                wbCVA.write(linhasAMAIS+3+n1, 18, BD_EXTERNO_ONSa.iloc[n1,6], texto)
                wbCVA.write(linhasAMAIS+3+n1, 19, BD_EXTERNO_ONSa.iloc[n1,7], data_format)
                wbCVA.write(linhasAMAIS+3+n1, 20, BD_EXTERNO_ONSa.iloc[n1,8], data_format)
                wbCVA.write(linhasAMAIS+3+n1, 21, BD_EXTERNO_ONSa.iloc[n1,9], data_format)
                wbCVA.write(linhasAMAIS+3+n1, 22, BD_EXTERNO_ONSa.iloc[n1,10], number_format)
                wbCVA.write(linhasAMAIS+3+n1, 23, BD_EXTERNO_ONSa.iloc[n1,11], number_format)
                wbCVA.write(linhasAMAIS+3+n1, 24, BD_EXTERNO_ONSa.iloc[n1,12], number_format)
                wbCVA.write(linhasAMAIS+3+n1, 25, BD_EXTERNO_ONSa.iloc[n1,13], number_format)
                wbCVA.write(linhasAMAIS+3+n1, 26, BD_EXTERNO_ONSa.iloc[n1,14], number_format)
                wbCVA.write(linhasAMAIS+3+n1, 27, BD_EXTERNO_ONSa.iloc[n1,15], number_format)
                wbCVA.write(linhasAMAIS+3+n1, 28, BD_EXTERNO_ONSa.iloc[n1,16], number_format)
                wbCVA.write(linhasAMAIS+3+n1, 29, BD_EXTERNO_ONSa.iloc[n1,17], percentual_format)

            except:
                pass

        nrPROaC = len(BD_EXTERNO_ONSa) + 11 if item in dic else 0 

        for n1 in range(meses_totais):
            wbCVA.write(linhasAMAIS+3+n1, 2, (data_ini + relativedelta(months=n1)).replace(day=1), data_format)
            wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                3, 
                                f'''=SUMPRODUCT(
                                        (MONTH(BP_{item}!E10:E{nrPRO})=MONTH(C{12+n1}))*
                                        (YEAR(BP_{item}!E10:E{nrPRO})=YEAR(C{12+n1}))*
                                        (BP_{item}!I10:I{nrPRO}))
                                        +
                                     SUMPRODUCT(
                                        (MONTH(BP_{item}!E10:E{nrPRO})=MONTH(C{12+n1}))*
                                        (YEAR(BP_{item}!E10:E{nrPRO})=YEAR(C{12+n1}))*
                                        (BP_{item}!J10:J{nrPRO}))
                                    
                                    ''', 
                                currency_format
                            )
            
            wbCVA.write(
                            linhasAMAIS + 3 + n1, 
                            4, 
                            f'''=IFERROR(
                                            SUMIFS(AC12:AC{nrPROaC}, M12:M{nrPROaC}, C{12+n1}) *
                                            IF(((YEAR(C{12+n1}) -  YEAR(M{nrPROaC})) * 12 + MONTH(C{12+n1}) -  MONTH(M{nrPROaC})) > 12, 0, 1),
                                            0
                                        )
                                ''', 
                            currency_format
                        )
            wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                5, 
                                f'''= E{12+n1} - D{12+n1}
                                ''', 
                                currency_format
                            )


        

        
        wbCVA.set_column(2, 29, 15)
        wbCVA.set_column(17, 17, 52)
        wbCVA.set_column(13, 13, 52)
        wbCVA.hide_gridlines(2)

        etapa += 1

    item = "Energia"
    if item in dic:
        if st:
            avl.progress(int(60 + 40/len(dic) * etapa), f"Criando aba com os dados de {item}...")
        nrPRO = len(dic[item]) + 10 if item in dic else 0

        COD_CCEE = df_DADEMP['Cd_CCEE'].drop_duplicates().to_list()
        CCEE_CNTR = pd.read_sas("BD_CVA_REG/ccee_lista_contratos.sas7bdat")
        CCEE_CNTR = CCEE_CNTR[CCEE_CNTR['CD_PERF_AGCOMP'].isin(COD_CCEE)]
        for col in ['DT_LEIL', 'DT_INIO_SPMT', 'DT_FIM_SPMT', 'DATA_IMPORTACAO']:
            if CCEE_CNTR[col] .dtype == 'object':
                CCEE_CNTR[col] = pd.to_datetime(CCEE_CNTR[col], errors='coerce')
        CCEE_CNTR = CCEE_CNTR[CCEE_CNTR['DT_FIM_SPMT'] >= pd.to_datetime(data_ini)]
        LST_CNTR = CCEE_CNTR['CD_CNTR'].drop_duplicates().to_list()
        CCEE_MWh = pd.read_sas("BD_CVA_REG/ccee_contratos_mensal.sas7bdat")


        CCEE_MWh = CCEE_MWh[CCEE_MWh['CD_CNTR'].isin(LST_CNTR)]
        for col in ['COMPETENCIA']:
            if CCEE_MWh[col] .dtype == 'object':
                CCEE_MWh[col] = pd.to_datetime(CCEE_MWh[col], errors='coerce')
        CCEE_MWh = CCEE_MWh[(CCEE_MWh['COMPETENCIA'] >= pd.to_datetime(data_ini)) &
                            (CCEE_MWh['COMPETENCIA'] < pd.to_datetime(data_fim))][['CD_EVCT','CD_CNTR',
                                                                        'CD_PERF_AGVEND','COMPETENCIA','QT_CQ']]

        for col in CCEE_CNTR.select_dtypes([object]):
            try:
                CCEE_CNTR[col] = CCEE_CNTR[col].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
            except:
                CCEE_CNTR[col] = CCEE_CNTR[col].apply(lambda x: x.decode('latin1') if isinstance(x, bytes) else x)
        
        for col in CCEE_MWh.select_dtypes([object]):
            try:
                CCEE_MWh[col] = CCEE_MWh[col].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
            except:
                CCEE_MWh[col] = CCEE_MWh[col].apply(lambda x: x.decode('latin1') if isinstance(x, bytes) else x)

        CCEE_MWh = CCEE_MWh[(CCEE_MWh['CD_EVCT'].str.endswith('000'))][
                    ['CD_CNTR','CD_PERF_AGVEND','COMPETENCIA','QT_CQ']]
        CCEE_MWh = CCEE_MWh.drop_duplicates(subset = ['CD_CNTR','COMPETENCIA'])
        CCEE_CNTR = CCEE_CNTR.drop_duplicates(subset = ['CD_CNTR'])
        CCEE_MWh = (CCEE_MWh
                    .merge(CCEE_CNTR, how='left', on = 'CD_CNTR', suffixes = ("","_CNTR"))
                    .rename(columns={
                                'COMPETENCIA': 'DT_CMPT',
                            })[['CD_PERF_AGVEND','NU_SEQL_PROD','NM_PROD','TP_CNTR','NU_SEQL_LEIL',
                               'NM_LEIL','CD_CNTR','DT_INIO_SPMT','DT_FIM_SPMT',
                               'DT_CMPT','QT_CQ','CD_CSSE_VEND','CD_CSSE_COMP',
                               'NM_RESD']])
        
        fndata = lambda x: pd.to_datetime(x, format="%d%b%Y:%H:%M:%S.%f")
        try:
            CCEE_MCSD = pd.read_csv("BD_CVA_REG/CCEE_MCSD.csv", sep='|', encoding='latin-1',
                                 usecols=['CD_EVCT', 'CD_CNTR_CESS','MM_CTBZ','QT_QTP_SAZ',
                                          'QT_QTA_SAZ'], dtype = {'CD_EVCT' : str},
                                          parse_dates=['MM_CTBZ'], date_parser=fndata)
        except:
            CCEE_MCSD = pd.read_csv("BD_CVA_REG/CCEE_MCSD.csv", sep=';', encoding='latin-1',
                                 usecols=['CD_EVCT', 'CD_CNTR_CESS','MM_CTBZ','QT_QTP_SAZ',
                                          'QT_QTA_SAZ'], dtype = {'CD_EVCT' : str},
                                          parse_dates=['MM_CTBZ'], date_parser=fndata)
        CCEE_MCSD = CCEE_MCSD.rename(columns = {'CD_CNTR_CESS' : 'CD_CNTR', 'MM_CTBZ' : 'DT_CMPT'})
        CCEE_MCSD = CCEE_MCSD[CCEE_MCSD['CD_EVCT'].str.endswith("000")][['CD_CNTR','DT_CMPT','QT_QTP_SAZ',
                                          'QT_QTA_SAZ']].drop_duplicates(subset=['CD_CNTR','DT_CMPT'])
        
        CCEE_MWh = CCEE_MWh.merge(CCEE_MCSD[['CD_CNTR', 'DT_CMPT', 'QT_QTP_SAZ', 'QT_QTA_SAZ']], how = 'left',
                                  on = ['CD_CNTR', 'DT_CMPT'], suffixes = ("","_MCSD")).fillna(0)
        
        caminho = "BD_CVA_REG"
        arquivos = [f for f in os.listdir(caminho) if os.path.isfile(os.path.join(caminho, f)) and f.upper().endswith('CSV')]
        df_RV003 = pd.DataFrame()
        df_RV007 = pd.DataFrame()
        df_RV013 = pd.DataFrame()
        fndata = lambda x: pd.to_datetime(x, format="%Y%m")
        lst_enc = ["utf-8-sig", "latin-1", "utf-8"]
        for arq in arquivos:
            if (arq[:5] == 'RV03_') & (arq[:10] !='RV_003_SQL'):
                for tenc in lst_enc:
                    flg_sc = False
                    try:
                        df_arq = pd.read_csv(f"BD_CVA_REG/{arq}", sep=',', encoding=tenc,
                                            parse_dates=['Nº Ano Mês Evento'], date_parser=fndata,
                                            usecols = ['CD_CNTR', 'Nº Ano Mês Evento','CD_EVCT','QT_som_QMe_h_m','PV_CCEAR_FINAL','VL_RFIX_U',
                                                        'VL_RFIX_AP_D'])
                        flg_sc = True
                        break
                    except:
                        continue
                if not flg_sc:
                    raise Exception(f"Erro de codec em {arq}.")
                df_arq = df_arq[df_arq['CD_EVCT'].isin(df_arq.groupby('Nº Ano Mês Evento')['CD_EVCT'].max().to_list())].rename(
                    columns = {'Nº Ano Mês Evento' : 'DT_CMPT'}
                )
                for col in ['QT_som_QMe_h_m','PV_CCEAR_FINAL','VL_RFIX_U','VL_RFIX_AP_D']:
                    if df_arq[col].dtype == 'object':
                        df_arq[col] = pd.to_numeric(df_arq[col].str.replace(".","").str.replace(",","."), errors='coerce')
                if len(df_RV003) == 0:
                    df_RV003 = df_arq[['CD_CNTR', 'DT_CMPT', 'QT_som_QMe_h_m','PV_CCEAR_FINAL','VL_RFIX_U','VL_RFIX_AP_D']].copy()
                else:
                    df_RV003 = pd.concat([df_RV003, df_arq[['CD_CNTR', 'DT_CMPT', 'QT_som_QMe_h_m','PV_CCEAR_FINAL','VL_RFIX_U','VL_RFIX_AP_D']]], 
                                         ignore_index=True)
            elif arq[:7] == 'RV_003_':
                for tenc in lst_enc:
                    flg_sc = False
                    try:
                        df_arq = pd.read_csv(f"BD_CVA_REG/{arq}", sep='|', encoding=tenc,
                                            usecols = ['CD_CNTR', 'DT_EVCT','CD_EVCT','QT_som_QMe_h_m','VL_RFIX_U',
                                                        'VL_RFIX_AP_D'])
                        flg_sc = True
                        break
                    except:
                        continue
                if not flg_sc:
                    raise Exception(f"Erro de codec em {arq}.")
                df_arq = df_arq[df_arq['CD_EVCT'].isin(df_arq.groupby('DT_EVCT')['CD_EVCT'].max().to_list())].rename(
                    columns = {'DT_EVCT' : 'DT_CMPT'}
                )
                for col in ['QT_som_QMe_h_m','VL_RFIX_U','VL_RFIX_AP_D']:
                    if df_arq[col].dtype == 'object':
                        df_arq[col] = pd.to_numeric(df_arq[col].str.replace(".","").str.replace(",","."), errors='coerce')
                df_arq['PV_CCEAR_FINAL'] = 0
                if len(df_RV003) == 0:
                    df_RV003 = df_arq[['CD_CNTR', 'DT_CMPT', 'QT_som_QMe_h_m','PV_CCEAR_FINAL','VL_RFIX_U','VL_RFIX_AP_D']].copy()
                else:
                    df_RV003 = pd.concat([df_RV003, df_arq[['CD_CNTR', 'DT_CMPT', 'QT_som_QMe_h_m','PV_CCEAR_FINAL','VL_RFIX_U','VL_RFIX_AP_D']]], 
                                         ignore_index=True)
            elif arq[:5] == 'RV07_':
                for tenc in lst_enc:
                    flg_sc = False
                    try:
                        df_arq = pd.read_csv(f"BD_CVA_REG/{arq}", sep=',', encoding=tenc,
                                     parse_dates=['Nº Ano Mês Evento'], date_parser=fndata,
                                     usecols = ['Cd_CNTR', 'Nº Ano Mês Evento','Cd_EVCT','VL_RFIX_TOT'])
                        flg_sc = True
                        break
                    except:
                        continue
                if not flg_sc:
                    raise Exception(f"Erro de codec em {arq}.")
                df_arq = df_arq[df_arq['Cd_EVCT'].isin(df_arq.groupby('Nº Ano Mês Evento')['Cd_EVCT'].max().to_list())].rename(
                    columns = {'Nº Ano Mês Evento' : 'DT_CMPT',
                               'Cd_CNTR' : 'CD_CNTR',
                               'Cd_EVCT' : 'CD_EVCT'}
                )
                for col in ['VL_RFIX_TOT']:
                    if df_arq[col].dtype == 'object':
                        df_arq[col] = pd.to_numeric(df_arq[col].str.replace(".","").str.replace(",","."), errors='coerce')
                if len(df_RV003) == 0:
                    df_RV007 = df_arq[['CD_CNTR', 'DT_CMPT', 'VL_RFIX_TOT']].copy()
                else:
                    df_RV007 = pd.concat([df_RV007, df_arq[['CD_CNTR', 'DT_CMPT', 'VL_RFIX_TOT']]], 
                                         ignore_index=True)
            elif arq[:7] == 'RV_007_':
                for tenc in lst_enc:
                    flg_sc = False
                    try:
                        df_arq = pd.read_csv(f"BD_CVA_REG/{arq}", sep='|', encoding=tenc,
                                     usecols = ['CD_CNTR', 'DT_EVCT','CD_EVCT','VL_RFIX_TOT'])
                        flg_sc = True
                        break
                    except:
                        continue
                if not flg_sc:
                    raise Exception(f"Erro de codec em {arq}.")
                df_arq = df_arq[df_arq['CD_EVCT'].isin(df_arq.groupby('DT_EVCT')['CD_EVCT'].max().to_list())].rename(
                    columns = {'DT_EVCT' : 'DT_CMPT'}
                )
                for col in ['VL_RFIX_TOT']:
                    if df_arq[col].dtype == 'object':
                        df_arq[col] = pd.to_numeric(df_arq[col].str.replace(".","").str.replace(",","."), errors='coerce')
                
                if len(df_RV007) == 0:
                    df_RV007 = df_arq[['CD_CNTR', 'DT_CMPT', 'VL_RFIX_TOT']].copy()
                else:
                    df_RV007 = pd.concat([df_RV007, df_arq[['CD_CNTR', 'DT_CMPT', 'VL_RFIX_TOT']]], 
                                         ignore_index=True)
            elif arq[:5] == 'RV13_':
                for tenc in lst_enc:
                    flg_sc = False
                    try:
                        df_arq = pd.read_csv(f"BD_CVA_REG/{arq}", sep=',', encoding=tenc, quotechar='"',
                                     parse_dates=['Nº Ano Mês Evento'], date_parser=fndata,
                                     usecols = ['Cd_CNTR', 'Nº Ano Mês Evento','Cd_EVCT','VL_RV_M'])
                        flg_sc = True
                        break
                    except:
                        continue
                if not flg_sc:
                    raise Exception(f"Erro de codec em {arq}.")

                df_arq = df_arq[df_arq['Cd_EVCT'].isin(df_arq.groupby('Nº Ano Mês Evento')['Cd_EVCT'].max().to_list())].rename(
                    columns = {'Nº Ano Mês Evento' : 'DT_CMPT',
                               'Cd_CNTR' : 'CD_CNTR',
                               'Cd_EVCT' : 'CD_EVCT'}
                )
                for col in ['VL_RV_M']:
                    if df_arq[col].dtype == 'object':
                        df_arq[col] = pd.to_numeric(df_arq[col].str.replace('"','').str.replace(".","").str.replace(",","."), errors='coerce')
                if len(df_RV013) == 0:
                    df_RV013 = df_arq[['CD_CNTR', 'DT_CMPT', 'VL_RV_M']].copy()
                else:
                    df_RV013 = pd.concat([df_RV013, df_arq[['CD_CNTR', 'DT_CMPT', 'VL_RV_M']]], 
                                         ignore_index=True)
            elif arq[:7] == 'RV_013_':
                for tenc in lst_enc:
                    flg_sc = False
                    try:
                        df_arq = pd.read_csv(f"BD_CVA_REG/{arq}", sep='|', encoding=tenc,
                                     usecols = ['CD_CNTR', 'DT_EVCT','CD_EVCT','VL_RV_M'])
                        flg_sc = True
                        break
                    except:
                        continue
                if not flg_sc:
                    raise Exception(f"Erro de codec em {arq}.")
                df_arq = df_arq[df_arq['CD_EVCT'].isin(df_arq.groupby('DT_EVCT')['CD_EVCT'].max().to_list())].rename(
                    columns = {'DT_EVCT' : 'DT_CMPT'}
                )
                for col in ['VL_RV_M']:
                    if df_arq[col].dtype == 'object':
                        df_arq[col] = pd.to_numeric(df_arq[col].str.replace('"','').str.replace(".","").str.replace(",","."), errors='coerce')

                if len(df_RV013) == 0:
                    df_RV013 = df_arq[['CD_CNTR', 'DT_CMPT', 'VL_RV_M']].copy()
                else:
                    df_RV013 = pd.concat([df_RV013, df_arq[['CD_CNTR', 'DT_CMPT', 'VL_RV_M']]], 
                                         ignore_index=True)
                    
        if CCEE_MWh['DT_CMPT'].dtype == 'object':        
            CCEE_MWh['DT_CMPT'] = pd.to_datetime(CCEE_MWh['DT_CMPT'], errors='coerce')
        if df_RV003['DT_CMPT'].dtype == 'object':        
            df_RV003['DT_CMPT'] = pd.to_datetime(df_RV003['DT_CMPT'], errors='coerce')
        if df_RV007['DT_CMPT'].dtype == 'object':        
            df_RV007['DT_CMPT'] = pd.to_datetime(df_RV007['DT_CMPT'], errors='coerce')
        if df_RV013['DT_CMPT'].dtype == 'object':        
            df_RV013['DT_CMPT'] = pd.to_datetime(df_RV007['DT_CMPT'], errors='coerce')

        df_RV013['DT_CMPT'] = df_RV013['DT_CMPT'].astype('datetime64[ns]')
        df_RV003['DT_CMPT'] = df_RV003['DT_CMPT'].astype('datetime64[ns]')
        df_RV007['DT_CMPT'] = df_RV007['DT_CMPT'].astype('datetime64[ns]')
        CCEE_MWh['DT_CMPT'] = CCEE_MWh['DT_CMPT'].astype('datetime64[ns]')

        df_RV013['CD_CNTR'] = df_RV013['CD_CNTR'].astype('int64')
        df_RV003['CD_CNTR'] = df_RV003['CD_CNTR'].astype('int64')
        df_RV007['CD_CNTR'] = df_RV007['CD_CNTR'].astype('int64')
        CCEE_MWh['CD_CNTR'] = CCEE_MWh['CD_CNTR'].astype('int64')


        CCEE_MWh = CCEE_MWh.merge(df_RV003[['CD_CNTR', 'DT_CMPT', 'QT_som_QMe_h_m', 'PV_CCEAR_FINAL','VL_RFIX_U','VL_RFIX_AP_D']], how = 'left',
                                  on = ['CD_CNTR', 'DT_CMPT'], suffixes = ("","_RV003")).rename(columns = {
                                      'QT_som_QMe_h_m' : 'QT_RV003',
                                      'PV_CCEAR_FINAL' : 'CM_RV003',
                                      'VL_RFIX_U' : 'VL_RFIX_U_RV003',
                                      'VL_RFIX_AP_D' : 'VL_RFIX_AP_D_RV003'
                                  }).fillna(0)
        CCEE_MWh = CCEE_MWh.merge(df_RV007[['CD_CNTR', 'DT_CMPT', 'VL_RFIX_TOT']], how = 'left',
                                  on = ['CD_CNTR', 'DT_CMPT'], suffixes = ("","_RV007")).rename(columns = {
                                      'VL_RFIX_TOT' : 'VL_RFIX_TOT_RV007',

                                  }).fillna(0)
        CCEE_MWh = CCEE_MWh.merge(df_RV013[['CD_CNTR', 'DT_CMPT', 'VL_RV_M']], how = 'left',
                                  on = ['CD_CNTR', 'DT_CMPT'], suffixes = ("","_RV013")).rename(columns = {
                                      'VL_RV_M' : 'VL_RVM_RV013',

                                  }).fillna(0)
        CCEE_MWh = CCEE_MWh.sort_values(by=['NM_LEIL','CD_CNTR','DT_CMPT'], ascending=True)

        nrPROen = len(CCEE_MWh) + 12

        wbCVA = workbook.add_worksheet(f'DADOS_CCEE_{item}')
        wbCVA.merge_range('C5:F5', f'CÁLCULO PROVISÓRIO {st.session_state.nm_empr}', tituloP)
        wbCVA.write(linhasAMAIS + 1,2, f'Dados da CCEE: {item}.',titulo2)
        wbCVA.write(linhasAMAIS + 2,2,"Cd_VEND", titulo)
        wbCVA.write(linhasAMAIS + 2,3,"Nr_PROD", titulo)
        wbCVA.write(linhasAMAIS + 2,4,"Nm_PROD", titulo)
        wbCVA.write(linhasAMAIS + 2,5,"TP_CNTR", titulo)
        wbCVA.write(linhasAMAIS + 2,6,"Nr_LEILAO", titulo)
        wbCVA.write(linhasAMAIS + 2,7,"Nm_LEILAO", titulo)
        wbCVA.write(linhasAMAIS + 2,8,"Cd_CNTR", titulo)
        wbCVA.write(linhasAMAIS + 2,9,"Dt_INI_SUPR", titulo)
        wbCVA.write(linhasAMAIS + 2,10,"Dt_FIM_SUPR", titulo)
        wbCVA.write(linhasAMAIS + 2,11,"Dt_CMPT", titulo)
        wbCVA.write(linhasAMAIS + 2,12,"Qtd_ENE", titulo)
        wbCVA.write(linhasAMAIS + 2,13,"Cd_CSSE_VEND", titulo)
        wbCVA.write(linhasAMAIS + 2,14,"Cd_CSSE_COMP", titulo)
        wbCVA.write(linhasAMAIS + 2,15,"Nm_GER", titulo)
        wbCVA.write(linhasAMAIS + 2,16,"Qtd_QTP_SAZ", titulo)
        wbCVA.write(linhasAMAIS + 2,17,"Qtd_QTA_SAZ", titulo)
        wbCVA.write(linhasAMAIS + 2,18,"Qtd_RV003", titulo)
        wbCVA.write(linhasAMAIS + 2,19,"CM_RV003", titulo)
        wbCVA.write(linhasAMAIS + 2,20,"VL_RFIX_U_RV003", titulo)
        wbCVA.write(linhasAMAIS + 2,21,"VL_RFIX_AP_D_RV003", titulo)
        wbCVA.write(linhasAMAIS + 2,22,"VL_RFIX_TOT_RV007", titulo)
        wbCVA.write(linhasAMAIS + 2,23,"VL_RVM_RV013", titulo)

        for n1 in range(len(CCEE_MWh)):
            try:
                wbCVA.write(linhasAMAIS+3+n1, 2, CCEE_MWh.iloc[n1,0], texto)
                wbCVA.write(linhasAMAIS+3+n1, 3, CCEE_MWh.iloc[n1,1], texto)
                wbCVA.write(linhasAMAIS+3+n1, 4, CCEE_MWh.iloc[n1,2], texto)
                wbCVA.write(linhasAMAIS+3+n1, 5, CCEE_MWh.iloc[n1,3], texto)
                wbCVA.write(linhasAMAIS+3+n1, 6, CCEE_MWh.iloc[n1,4], texto)
                wbCVA.write(linhasAMAIS+3+n1, 7, CCEE_MWh.iloc[n1,5], texto)
                wbCVA.write(linhasAMAIS+3+n1, 8, CCEE_MWh.iloc[n1,6], texto)
                wbCVA.write(linhasAMAIS+3+n1, 9, CCEE_MWh.iloc[n1,7], data_format)
                wbCVA.write(linhasAMAIS+3+n1, 10, CCEE_MWh.iloc[n1,8], data_format)
                wbCVA.write(linhasAMAIS+3+n1, 11, CCEE_MWh.iloc[n1,9], data_format)
                wbCVA.write(linhasAMAIS+3+n1, 12, CCEE_MWh.iloc[n1,10], number_format)
                wbCVA.write(linhasAMAIS+3+n1, 13, CCEE_MWh.iloc[n1,11], texto)
                wbCVA.write(linhasAMAIS+3+n1, 14, CCEE_MWh.iloc[n1,12], texto)
                wbCVA.write(linhasAMAIS+3+n1, 15, CCEE_MWh.iloc[n1,13], texto)
                wbCVA.write(linhasAMAIS+3+n1, 16, CCEE_MWh.iloc[n1,14], number_format)
                wbCVA.write(linhasAMAIS+3+n1, 17, CCEE_MWh.iloc[n1,15], number_format)
                wbCVA.write(linhasAMAIS+3+n1, 18, CCEE_MWh.iloc[n1,16], number_format)
                wbCVA.write(linhasAMAIS+3+n1, 19, CCEE_MWh.iloc[n1,17], number_format)
                wbCVA.write(linhasAMAIS+3+n1, 20, CCEE_MWh.iloc[n1,18], number_format)
                wbCVA.write(linhasAMAIS+3+n1, 21, CCEE_MWh.iloc[n1,19], number_format)
                wbCVA.write(linhasAMAIS+3+n1, 22, CCEE_MWh.iloc[n1,20], number_format)
                wbCVA.write(linhasAMAIS+3+n1, 23, CCEE_MWh.iloc[n1,21], number_format)



            except:
                pass

        
        wbCVA.set_column(2, 29, 15)
        wbCVA.set_column(7, 7, 52)
        wbCVA.set_column(15, 15, 52)
        wbCVA.hide_gridlines(2)

        df_PROV = CCEE_MWh[CCEE_MWh['TP_CNTR']==10187].drop_duplicates(subset=['CD_CNTR','DT_CMPT']).copy()

        if len(df_PROV)>0:
            wbCVA = workbook.add_worksheet(f'CVA_{item}_CCEARd')
            wbCVA.merge_range('C5:F5', f'CÁLCULO PROVISÓRIO {st.session_state.nm_empr}', tituloP)
            wbCVA.write(linhasAMAIS + 1,2, f'Cálculo da variação da parcela A: {item}.',titulo2)
            wbCVA.write(linhasAMAIS + 2,2,"Nm_Leilao", titulo)
            wbCVA.write(linhasAMAIS + 2,3,"Cd_CNTR", titulo)
            wbCVA.write(linhasAMAIS + 2,4,"Nm_PROD", titulo)
            wbCVA.write(linhasAMAIS + 2,5,"Cd_VEND", titulo)
            wbCVA.write(linhasAMAIS + 2,6,"Nm_VEND", titulo)
            wbCVA.write(linhasAMAIS + 2,7,"Dt_CMPT", titulo)
            wbCVA.write(linhasAMAIS + 2,8,"VL_RV13", titulo)
            wbCVA.write(linhasAMAIS + 2,9,"VL_PAG_LIQ", titulo)
            wbCVA.write(linhasAMAIS + 2,10,"VL_PAG_RESS", titulo)
            wbCVA.write(linhasAMAIS + 2,11,"VL_PAG_TRIB", titulo)
            wbCVA.write(linhasAMAIS + 2,12,"VL_PAG_TOT", titulo)
            wbCVA.write(linhasAMAIS + 2,13,"VL_DELTA", titulo)
            wbCVA.write(linhasAMAIS + 2,14,"Qtd_BP", titulo)
            wbCVA.write(linhasAMAIS + 2,15,"Qtd_CCEE", titulo)
            wbCVA.write(linhasAMAIS + 2,16,"Qtd_DELTA", titulo)

            for n1 in range(len(df_PROV)):
                wbCVA.write(linhasAMAIS+3+n1, 2, df_PROV.iloc[n1,5], texto)
                wbCVA.write(linhasAMAIS+3+n1, 3, df_PROV.iloc[n1,6], texto)
                wbCVA.write(linhasAMAIS+3+n1, 4, df_PROV.iloc[n1,2], texto)
                wbCVA.write(linhasAMAIS+3+n1, 5, df_PROV.iloc[n1,0], texto)
                wbCVA.write(linhasAMAIS+3+n1, 6, df_PROV.iloc[n1,13], texto)
                wbCVA.write(linhasAMAIS+3+n1, 7, df_PROV.iloc[n1,9], data_format)

                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                8,
                                f"=SUMPRODUCT(("
                                f"(MONTH(DADOS_CCEE_{item}!L12:L{nrPROen})=MONTH(H{12+n1})) * "
                                f"(YEAR(DADOS_CCEE_{item}!L12:L{nrPROen})=YEAR(H{12+n1})) * "
                                f"(DADOS_CCEE_{item}!I12:I{nrPROen}=D{12+n1})) * "
                                f"(DADOS_CCEE_{item}!X12:X{nrPROen}))",
                                currency_format
                            )
                
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                9, 
                                f"=SUMPRODUCT(("
                                f"(MONTH(BP_{item}!E10:E{nrPRO})=MONTH(H{12+n1})) * "
                                f"(YEAR(BP_{item}!E10:E{nrPRO})=YEAR(H{12+n1})) * "
                                f"(BP_{item}!L10:L{nrPRO}=D{12+n1})) * "
                                f"(BP_{item}!I10:I{nrPRO}))", 
                                currency_format
                            )
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                10, 
                                f"=SUMPRODUCT(("
                                f"(MONTH(BP_{item}!E10:E{nrPRO})=MONTH(H{12+n1})) * "
                                f"(YEAR(BP_{item}!E10:E{nrPRO})=YEAR(H{12+n1})) * "
                                f"(BP_{item}!L10:L{nrPRO}=D{12+n1})) * "
                                f"(BP_{item}!J10:J{nrPRO}))", 
                                currency_format
                            )
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                11, 
                                f"=SUMPRODUCT(("
                                f"(MONTH(BP_{item}!E10:E{nrPRO})=MONTH(H{12+n1})) * "
                                f"(YEAR(BP_{item}!E10:E{nrPRO})=YEAR(H{12+n1})) * "
                                f"(BP_{item}!L10:L{nrPRO}=D{12+n1})) * "
                                f"(BP_{item}!K10:K{nrPRO}))", 
                                currency_format
                            )
                
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                12, 
                                f'''= J{12+n1} + K{12+n1} + L{12+n1}
                                ''', 
                                currency_format
                            )
                
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                13, 
                                f'''= M{12+n1} - I{12+n1}
                                ''', 
                                currency_format
                            )
                
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                14, 
                                f"=SUMPRODUCT(("
                                f"(MONTH(BP_{item}!E10:E{nrPRO})=MONTH(H{12+n1})) * "
                                f"(YEAR(BP_{item}!E10:E{nrPRO})=YEAR(H{12+n1})) * "
                                f"(BP_{item}!L10:L{nrPRO}=D{12+n1})) * "
                                f"(BP_{item}!O10:O{nrPRO}))", 
                                number_format
                            )
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                15,
                                f"=SUMPRODUCT(("
                                f"(MONTH(DADOS_CCEE_{item}!L12:L{nrPROen})=MONTH(H{12+n1})) * "
                                f"(YEAR(DADOS_CCEE_{item}!L12:L{nrPROen})=YEAR(H{12+n1})) * "
                                f"(DADOS_CCEE_{item}!I12:I{nrPROen}=D{12+n1})) * "
                                f"(DADOS_CCEE_{item}!M12:M{nrPROen}))",
                                number_format
                            )
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                16, 
                                f'''= P{12+n1} - O{12+n1}
                                ''', 
                                number_format
                            )


            wbCVA.set_column(2, 29, 15)
            wbCVA.set_column(2, 2, 52)
            wbCVA.set_column(6, 6, 52)
            wbCVA.hide_gridlines(2)

        df_PROV = CCEE_MWh[CCEE_MWh['TP_CNTR']!=10187].drop_duplicates(subset=['CD_CNTR','DT_CMPT']).copy()

        if len(df_PROV)>0:
            wbCVA = workbook.add_worksheet(f'CVA_{item}_DEMAIS')
            wbCVA.merge_range('C5:F5', f'CÁLCULO PROVISÓRIO {st.session_state.nm_empr}', tituloP)
            wbCVA.write(linhasAMAIS + 1,2, f'Cálculo da variação da parcela A: {item}.',titulo2)
            wbCVA.write(linhasAMAIS + 2,2,"Nm_Leilao", titulo)
            wbCVA.write(linhasAMAIS + 2,3,"Cd_CNTR", titulo)
            wbCVA.write(linhasAMAIS + 2,4,"Nm_PROD", titulo)
            wbCVA.write(linhasAMAIS + 2,5,"Cd_VEND", titulo)
            wbCVA.write(linhasAMAIS + 2,6,"Nm_VEND", titulo)
            wbCVA.write(linhasAMAIS + 2,7,"Dt_CMPT", titulo)
            wbCVA.write(linhasAMAIS + 2,8,"VL_PAG_LIQ", titulo)
            wbCVA.write(linhasAMAIS + 2,9,"VL_PAG_RESS", titulo)
            wbCVA.write(linhasAMAIS + 2,10,"VL_PAG_TRIB", titulo)
            wbCVA.write(linhasAMAIS + 2,11,"VL_PAG_TOT", titulo)
            wbCVA.write(linhasAMAIS + 2,12,"Qtd_BP", titulo)
            wbCVA.write(linhasAMAIS + 2,13,"Qtd_CCEE", titulo)
            wbCVA.write(linhasAMAIS + 2,14,"Qtd_CCEE_QTP_SAZ", titulo)
            wbCVA.write(linhasAMAIS + 2,15,"Qtd_CCEE_QTA_SAZ", titulo)
            wbCVA.write(linhasAMAIS + 2,16,"Qtd_CCEE_FIM", titulo)
            wbCVA.write(linhasAMAIS + 2,17,"CM_ENE", titulo)

            wbCVA.write(linhasAMAIS + 2,18,"Qtd_RV003", titulo)
            wbCVA.write(linhasAMAIS + 2,19,"RV_FINAL", titulo)
            wbCVA.write(linhasAMAIS + 2,20,"CM_RV", titulo)

            for n1 in range(len(df_PROV)):
                wbCVA.write(linhasAMAIS+3+n1, 2, df_PROV.iloc[n1,5], texto)
                wbCVA.write(linhasAMAIS+3+n1, 3, df_PROV.iloc[n1,6], texto)
                wbCVA.write(linhasAMAIS+3+n1, 4, df_PROV.iloc[n1,2], texto)
                wbCVA.write(linhasAMAIS+3+n1, 5, df_PROV.iloc[n1,0], texto)
                wbCVA.write(linhasAMAIS+3+n1, 6, df_PROV.iloc[n1,13], texto)
                wbCVA.write(linhasAMAIS+3+n1, 7, df_PROV.iloc[n1,9], data_format)

                
                
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                8, 
                                f"=SUMPRODUCT(("
                                f"(MONTH(BP_{item}!E10:E{nrPRO})=MONTH(H{12+n1})) * "
                                f"(YEAR(BP_{item}!E10:E{nrPRO})=YEAR(H{12+n1})) * "
                                f"(BP_{item}!L10:L{nrPRO}=D{12+n1})) * "
                                f"(BP_{item}!I10:I{nrPRO}))", 
                                currency_format
                            )
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                9, 
                                f"=SUMPRODUCT(("
                                f"(MONTH(BP_{item}!E10:E{nrPRO})=MONTH(H{12+n1})) * "
                                f"(YEAR(BP_{item}!E10:E{nrPRO})=YEAR(H{12+n1})) * "
                                f"(BP_{item}!L10:L{nrPRO}=D{12+n1})) * "
                                f"(BP_{item}!J10:J{nrPRO}))", 
                                currency_format
                            )
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                10, 
                                f"=SUMPRODUCT(("
                                f"(MONTH(BP_{item}!E10:E{nrPRO})=MONTH(H{12+n1})) * "
                                f"(YEAR(BP_{item}!E10:E{nrPRO})=YEAR(H{12+n1})) * "
                                f"(BP_{item}!L10:L{nrPRO}=D{12+n1})) * "
                                f"(BP_{item}!K10:K{nrPRO}))", 
                                currency_format
                            )
                
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                11, 
                                f'''= I{12+n1} + K{12+n1} + J{12+n1}
                                ''', 
                                currency_format
                            )
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                12, 
                                f"=SUMPRODUCT(("
                                f"(MONTH(BP_{item}!E10:E{nrPRO})=MONTH(H{12+n1})) * "
                                f"(YEAR(BP_{item}!E10:E{nrPRO})=YEAR(H{12+n1})) * "
                                f"(BP_{item}!L10:L{nrPRO}=D{12+n1})) * "
                                f"(BP_{item}!O10:O{nrPRO}))", 
                                currency_format
                            )
                
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                13,
                                f"=SUMPRODUCT(("
                                f"(MONTH(DADOS_CCEE_{item}!L12:L{nrPROen})=MONTH(H{12+n1})) * "
                                f"(YEAR(DADOS_CCEE_{item}!L12:L{nrPROen})=YEAR(H{12+n1})) * "
                                f"(DADOS_CCEE_{item}!I12:I{nrPROen}=D{12+n1})) * "
                                f"(DADOS_CCEE_{item}!M12:M{nrPROen}))",
                                number_format
                            )
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                14,
                                f"=SUMPRODUCT(("
                                f"(MONTH(DADOS_CCEE_{item}!L12:L{nrPROen})=MONTH(H{12+n1})) * "
                                f"(YEAR(DADOS_CCEE_{item}!L12:L{nrPROen})=YEAR(H{12+n1})) * "
                                f"(DADOS_CCEE_{item}!I12:I{nrPROen}=D{12+n1})) * "
                                f"(DADOS_CCEE_{item}!Q12:Q{nrPROen}))",
                                number_format
                            )
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                15,
                                f"=SUMPRODUCT(("
                                f"(MONTH(DADOS_CCEE_{item}!L12:L{nrPROen})=MONTH(H{12+n1})) * "
                                f"(YEAR(DADOS_CCEE_{item}!L12:L{nrPROen})=YEAR(H{12+n1})) * "
                                f"(DADOS_CCEE_{item}!I12:I{nrPROen}=D{12+n1})) * "
                                f"(DADOS_CCEE_{item}!R12:R{nrPROen}))",
                                number_format
                            )
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                16, 
                                f'''= N{12+n1} - O{12+n1} - P{12+n1}
                                ''', 
                                currency_format
                            )
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                17, 
                                f'''= iferror(L{12+n1} / Q{12+n1},0)
                                ''', 
                                currency_format
                            )
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                18,
                                f"=SUMPRODUCT(("
                                f"(MONTH(DADOS_CCEE_{item}!L12:L{nrPROen})=MONTH(H{12+n1})) * "
                                f"(YEAR(DADOS_CCEE_{item}!L12:L{nrPROen})=YEAR(H{12+n1})) * "
                                f"(DADOS_CCEE_{item}!I12:I{nrPROen}=D{12+n1})) * "
                                f"(DADOS_CCEE_{item}!S12:S{nrPROen}))",
                                number_format
                            )
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                19,
                                f"=SUMPRODUCT(("
                                f"(MONTH(DADOS_CCEE_{item}!L12:L{nrPROen})=MONTH(H{12+n1})) * "
                                f"(YEAR(DADOS_CCEE_{item}!L12:L{nrPROen})=YEAR(H{12+n1})) * "
                                f"(DADOS_CCEE_{item}!I12:I{nrPROen}=D{12+n1})) * "
                                f"(DADOS_CCEE_{item}!W12:W{nrPROen}))",
                                currency_format
                            )
                wbCVA.write(
                                linhasAMAIS + 3 + n1, 
                                20, 
                                f'''= iferror(T{12+n1} / S{12+n1},0)
                                ''', 
                                currency_format
                            )
                


            wbCVA.set_column(2, 29, 15)
            wbCVA.set_column(2, 2, 52)
            wbCVA.set_column(6, 6, 52)
            wbCVA.hide_gridlines(2)

        etapa += 1    

    workbook.close()
    if st:
        avl.progress(100, f"Finalizado e guardado em {diret}/Saida_VAL_F1.xlsx!")
        avl.empty()
    return "OK"

def imprimi_F00_INCR(dir_arq_saida, con, Empresa, st=None):
    
    if existe_tabela('TBL_CTB_FIS_TESTES', con):
        SQLq = f"""
            SELECT *
            FROM TBL_CTB_FIS_TESTES 
            
            """
        CTB_FIS = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo CTB_FIS da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo CTB_FIS da base local.')

    workbook = xlsxwriter.Workbook(f'{dir_arq_saida}/Saida_INCR_F0_CTB_FIS.xlsx', options={'nan_inf_to_errors': True})

    wb = workbook.add_worksheet('CTB_FIS')

    workbook.set_calc_mode('auto')
    workbook.use_zip64()

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    number2_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8,  'align':'center', 'bottom':1})
    currency2_format = workbook.add_format({'bg_color':'#D9D9D9','num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})

    linhasAMAIS=8

    lst_num = tuple([n for n, nm in enumerate(CTB_FIS.columns.to_list()) if nm[:6].upper() in ['CTB_VL', 'FIS_VL']])
    lst_dt = tuple([n for n, nm in enumerate(CTB_FIS.columns.to_list()) if nm[:6].upper() in ['CTB_DT', 'FIS_DT']])
    
    if not len(lst_num):
        lst_num = (2,)
    if not len(lst_dt):
        lst_num = (1,)

    with st.spinner(text="Construíndo Excel CTB_FIS..."):
        wb.merge_range('C5:X5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
        wb.write(linhasAMAIS-1, 2,'CTB_FIS',titulo2)
        formatos = {
                        lst_num: currency_format,
                        lst_dt: data_format
                    }
        
        #Configuração otimizada de largura de colunas
        colunas_largura = {}
        for i, col in enumerate(CTB_FIS.columns):
            max_len = max(
                            CTB_FIS[col].astype(str).map(len).max(),
                            len(col)                              
                         ) + 2  
            colunas_largura[(i+2, i+2)] = max_len


        x1 = ax_escreve_excel(wb, CTB_FIS, linhasAMAIS, formatos, colunas_largura, texto, titulo,st=st)

    workbook.close()
    
    return "OK"

def imprimi_F1_BB(dir_arq_saida, con, Empresa, st=None):
    if st:
        avl = st.progress(0, "Iniciando exportação para excel...")

    workbook = xlsxwriter.Workbook(f'{dir_arq_saida}/Saida_BB_F1.xlsx', {"nan_inf_to_errors": True})

    
    
    workbook.set_calc_mode('auto')
    workbook.use_zip64()

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    linhasAMAIS=8
    if st:
        avl.progress(5, "Criando aba com a análise do ponto de partida...")

    #Primeiro vamos imprimir os resultados sintéticos das baixas aplicadas
    if existe_tabela('tbl_sintetica_baixas_aplicadas', con):
        SQLq = f"""
                    SELECT *
                    FROM tbl_sintetica_baixas_aplicadas  
            """
        df_RESs = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo Sintético da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo Sintético da base local.')
        
    linhasAMAIS = 6
    wb1 = workbook.add_worksheet('SINTETICO_BAIXAS')
    wb1.merge_range('C5:F5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
    formatos = {
                    (4,): currency_format,
                    (3,5): number_format,
                    (7,): data_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {}
    for i, col in enumerate(df_RESs.columns):
        max_len = max(
                        df_RESs[col].astype(str).map(len).max(),
                        len(col)                              
                        ) + 2  
        colunas_largura[(i+2, i+2)] = max_len

    x1 = ax_escreve_excel(wb1, df_RESs, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)

    # Agora, imprimir os resultados analiticos das baixas aplicadas
    if existe_tabela('tbl_analitica_baixas_aplicadas', con):
        SQLq = f"""
                    SELECT *
                    FROM tbl_analitica_baixas_aplicadas  
            """
        df_RESa = pd.read_sql(SQLq, con)
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo Analítico da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo Analítico da base local.')

    wb1 = workbook.add_worksheet('ANALITICO_BAIXAS')
    wb1.merge_range('C5:H5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
    formatos = {
                    (4,5): currency_format,
                    (3,6): number_format,
                    (7,): data_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {}
    for i, col in enumerate(df_RESa.columns):
        max_len = max(
                        df_RESa[col].astype(str).map(len).max(),
                        len(col)                              
                        ) + 2  
        colunas_largura[(i+2, i+2)] = max_len

    x1 = ax_escreve_excel(wb1, df_RESa, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
    workbook.close()

    # Agora, imprimir os resultados analiticos das baixas não aplicadas
    if existe_tabela('tbl_baixas_nao_aplicadas', con):
        SQLq = f"""
                    SELECT *
                    FROM tbl_baixas_nao_aplicadas  
            """
        df_RESa = pd.read_sql(SQLq, con)
        df_RESa = df_RESa.drop(columns=['__emb__'])
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo Analítico de Baixas não APlicadas da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo Analítico de Baixas não APlicadas da base local.')

    if st:
        avl.progress(20, "Criando abas com a avaliação analítica...")
    wb1 = workbook.add_worksheet('ANL_BAIXAS_NA')
    wb1.merge_range('C5:H5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
    formatos = {
                    (4,5): currency_format,
                    (3,6): number_format,
                    (7,): data_format,
                }
    
    #Configuração otimizada de largura de colunas
    colunas_largura = {}
    for i, col in enumerate(df_RESa.columns):
        max_len = max(
                        df_RESa[col].astype(str).map(len).max(),
                        len(col)                              
                        ) + 2  
        colunas_largura[(i+2, i+2)] = max_len

    x1 = ax_escreve_excel(wb1, df_RESa, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)

    if st:
        avl.progress(40, "Criando abas com a laudo movimentado...")

    if existe_tabela('tbl_laudo_pos_mov', con):
        SQLq = f"""
                    SELECT *
                    FROM tbl_laudo_pos_mov
            """
        df = pd.read_sql(SQLq, con)
        df = df.drop(columns=['__emb__'])
        tmn = 500000
        n = 0
        formatos = {
                        (21,23,24,34,28,29,30,31,32,33,47,39,40,41,42,43,44,45,46,49,50,
                         57,51,52,53,54,55,56,58,59,62,66): number_format,
                        (25,37,48): data_format,
                        (63,64,65,68,67,69,70): percentual_format,
                    }
        
        #Configuração otimizada de largura de colunas
        colunas_largura = {}
        for i, col in enumerate(df.columns):
            max_len = max(
                            df[col].astype(str).map(len).max(),
                            len(col)                              
                            ) + 2  
            colunas_largura[(i+2, i+2)] = max_len
                        
        df['Id_SEQ_PP']=pd.to_numeric(df['Id_SEQ_PP'].str.replace(',','.'),errors='coerce')
        while n*tmn <= (len(df) + 1):
            BL_DFimp = df.iloc[n*tmn : (n+1)*tmn].copy()
            wb = workbook.add_worksheet(f'MOV_LAUDO_{n}')
            wb.merge_range('C5:L5', f'CÁLCULO PROVISÓRIO {Empresa}', tituloP)
            xn = ax_escreve_excel(wb, BL_DFimp, linhasAMAIS, formatos, colunas_largura, texto, titulo, st=st)
            n += 1
    else:
        workbook.close()
        if st:
            st.error('Falha ao importar o arquivo MOVIMENTACAO da base local.')
            return None
        else:
            raise UserWarning('Falha ao importar o arquivo MOVIMENTACAO da base local.')
        
    
    workbook.close()
    if st:
        avl.progress(100, f"Finalizado e guardado em {dir_arq_saida}/Saida_BB_F1.xlsx!")
    return "OK"

def imp_ck_list(arq = None, dados = None):
        if dados == None or arq == None:
            return "Falhou"
        workbook = xlsxwriter.Workbook(arq)
        worksheet = workbook.add_worksheet("Checklist")


        header_fmt = workbook.add_format({
                                            'bold': True, 'font_color': '#FFFFFF', 'bg_color': '#305496',
                                            'border': 0, 'align': 'center', 'valign': 'vcenter'
                                        })

        section_fmt = workbook.add_format({
                                                'bold': True, 'bg_color': '#D9E1F2', 'border': 0,
                                                'font_size': 11, 'align': 'left', 'valign': 'vcenter'
                                            })

        item_fmt = workbook.add_format({
                                            'text_wrap': True, 'bg_color': '#F2F2F2',
                                            'font_size': 10, 'align': 'left', 'valign': 'top',
                                            'border': 0
                                        })

        status_fmt = workbook.add_format({
                                            'align': 'center', 'valign': 'vcenter',
                                            'font_color': '#333333', 'bg_color': '#FFFFFF',
                                            'border': 1
                                        })


        worksheet.set_column('A:A', 32)
        worksheet.set_column('B:B', 80)
        worksheet.set_column('C:C', 18)
        worksheet.set_row(0, 25)

        for row_idx, row in enumerate(dados):
            for col_idx, cell_value in enumerate(row):
                if row_idx == 0:
                    worksheet.write(row_idx, col_idx, cell_value, header_fmt)
                elif col_idx == 0 and cell_value:
                    worksheet.write(row_idx, col_idx, cell_value, section_fmt)
                elif col_idx == 0:
                    worksheet.write_blank(row_idx, col_idx, None, item_fmt)
                elif col_idx == 1:
                    worksheet.write(row_idx, col_idx, cell_value, item_fmt)
                elif col_idx == 2:
                    worksheet.write(row_idx, col_idx, cell_value, status_fmt)
        worksheet.hide_gridlines(2)
        workbook.close()
        return "OK"

@st.fragment()
def imprimi_F0_ABT(dir_arq_saida, con, Empresa, st=None):
    if st:
        avl = st.progress(0, "Iniciando exportação para excel...")

    workbook = xlsxwriter.Workbook(f'{dir_arq_saida}/Saida_ABT_F0.xlsx', options={'nan_inf_to_errors': True})

    worksheet1 = workbook.add_worksheet('TBL_ABERTURA_ROA')
    
    workbook.set_calc_mode('auto')
    workbook.use_zip64()

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    number2_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8,  'align':'center', 'bottom':1})
    currency2_format = workbook.add_format({'bg_color':'#D9D9D9','num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})

    formato1 = workbook.add_format({'bg_color': '#FFC7CE',
                                   'font_color': '#9C0006'})
    formato2 = workbook.add_format({'bg_color': '#C6EFCE',
                                   'font_color': '#006100'})
    
    def formato_def(df):
        formatos = {}
        lst_txt = []
        lst_moe = []
        lst_num = []
        lst_dt = []
        lst_pct = []
        for col, n in enumerate(df.columns):
            if n[:3].upper() in ['COD','TXT', 'CD_', 'FLG', 'TIP', 'CHV', 'CNP','DESC','UNI','NM_']:
                lst_txt.append(col)
            elif n[:3].upper() in ['VL_','FC','FC_', 'DEL', 'DIF']:
                lst_moe.append(col)
            elif n[:3].upper() in ['QTD', 'CST', 'IND', 'NUM', 'ID_', 'SER']:
                lst_num.append(col)
            elif n[:3].upper() in ['DT_']:
                lst_dt.append(col)
            elif n[:3].upper() in ['ALI','PCT']:
                lst_pct.append(col)
        if len(lst_txt)>0:
            formatos[tuple(lst_txt)] = texto
        if len(lst_moe)>0:
            formatos[tuple(lst_moe)] = currency_format
        if len(lst_num)>0:
            formatos[tuple(lst_num)] = number_format
        if len(lst_dt)>0:
            formatos[tuple(lst_dt)] = data_format
        if len(lst_pct)>0:
            formatos[tuple(lst_pct)] = percentual_format
        return formatos
    
    def realce_col(worksheet = None, lista = [], df = None, colunas = []):
        tam = 9 + len(df)
        for l, lst in enumerate(lista):
            worksheet.write(l,70,lst)
        int_val = f"$BS$1:$BS${len(lista)}"
  
        for letra in colunas:
            intervalo = f'{letra}10:{letra}{tam}'
            base = f'MATCH({letra}10, {int_val}, 0)'
            worksheet.conditional_format( intervalo, {
                'type':     'formula',
                'criteria': f'=ISNUMBER({base})',
                'format':   formato2
            })
            worksheet.conditional_format( intervalo, {
                'type':     'formula',
                'criteria': f'=ISNA({base})',
                'format':   formato1
            })

    linhasAMAIS=8
    if st: avl.progress(3, "Criando aba com os dados de abertura do ROA...")

    TST_ABERTURA_PROJETOS_TI = imp_tbl_forma_000(nm_tbl="TST_ABERTURA_PROJETOS_TI", con=con, st=st, lst_cnv=[], workbook = workbook)
    worksheet1.merge_range('C5:U5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet1.write(linhasAMAIS-1, 2,'Tabela com os dados de abertura do ROA',titulo2)
    formatos = formato_def(TST_ABERTURA_PROJETOS_TI)
    x1 = ax_escreve_excel_md2(worksheet1, TST_ABERTURA_PROJETOS_TI, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

    TST_ABERTURA_PROJETOS_CLS_CST = imp_tbl_forma_000(nm_tbl="TST_ABERTURA_PROJETOS_CLS_CST", con=con, st=st, lst_cnv=[])
    if len(TST_ABERTURA_PROJETOS_CLS_CST)>0:
        ws = workbook.add_worksheet('TBL_ABERTURA_CLS_CST')
        ws.merge_range('C5:U5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
        ws.write(linhasAMAIS-1, 2,'Tabela com os dados de abertura do ROA por classe de custo',titulo2)
        formatos = formato_def(TST_ABERTURA_PROJETOS_CLS_CST)
        x1 = ax_escreve_excel_md2(ws, TST_ABERTURA_PROJETOS_CLS_CST, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)
    
    workbook.close()
    if st: avl.progress(100, f"Finalizado e guardado em {dir_arq_saida}/Saida_ABT_F0.xlsx!")
    return "OK"

@st.fragment()
def imprimi_F1_ABT(dir_arq_saida, con, Empresa, st=None):
    if st:
        avl = st.progress(0, "Iniciando exportação para excel...")

    workbook = xlsxwriter.Workbook(f'{dir_arq_saida}/Saida_ABT_F1.xlsx', options={'nan_inf_to_errors': True})

    worksheet1 = workbook.add_worksheet('TBL_ABERTURA_VF')
    worksheet2 = workbook.add_worksheet('TBL_ABERTURA_JOA')
    
    workbook.set_calc_mode('auto')
    workbook.use_zip64()

    currency_format = workbook.add_format({'num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    percentual_format = workbook.add_format({'num_format': '#0.00%;(#0.00%)','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    data_format = workbook.add_format({'num_format': 'dd/mm/yyyy','font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'center'})
    titulo =workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':2, 'align':'center','bold': True}) 
    texto= workbook.add_format({'font_name': 'Roboto','font_size': 8, 'bottom':1, 'align':'left'})
    tituloP =workbook.add_format({'font_name': 'Roboto','font_size': 20,  'align':'center','bold': True})
    titulo2 =workbook.add_format({'font_name': 'Roboto','font_size': 10, 'align':'left','bold': True}) 
    number_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})
    number2_format = workbook.add_format({'num_format': '#,##0.00;[Red]#,##0.00','font_name': 'Roboto','font_size': 8,  'align':'center', 'bottom':1})
    currency2_format = workbook.add_format({'bg_color':'#D9D9D9','num_format': 'R$ #,##0.00;[Red]R$ #,##0.00','font_name': 'Roboto','font_size': 8, 'bottom':1})

    formato1 = workbook.add_format({'bg_color': '#FFC7CE',
                                   'font_color': '#9C0006'})
    formato2 = workbook.add_format({'bg_color': '#C6EFCE',
                                   'font_color': '#006100'})
    
    def formato_def(df):
        formatos = {}
        lst_txt = []
        lst_moe = []
        lst_num = []
        lst_dt = []
        lst_pct = []
        for col, n in enumerate(df.columns):
            if n[:3].upper() in ['COD','TXT', 'CD_', 'FLG', 'TIP', 'CHV', 'CNP','DESC','UNI','NM_']:
                lst_txt.append(col)
            elif n[:3].upper() in ['VL_','FC','FC_', 'DEL', 'DIF']:
                lst_moe.append(col)
            elif n[:3].upper() in ['QTD', 'CST', 'IND', 'NUM', 'ID_', 'SER']:
                lst_num.append(col)
            elif n[:3].upper() in ['DT_']:
                lst_dt.append(col)
            elif n[:3].upper() in ['ALI','PCT']:
                lst_pct.append(col)
        if len(lst_txt)>0:
            formatos[tuple(lst_txt)] = texto
        if len(lst_moe)>0:
            formatos[tuple(lst_moe)] = currency_format
        if len(lst_num)>0:
            formatos[tuple(lst_num)] = number_format
        if len(lst_dt)>0:
            formatos[tuple(lst_dt)] = data_format
        if len(lst_pct)>0:
            formatos[tuple(lst_pct)] = percentual_format
        return formatos
    
    def realce_col(worksheet = None, lista = [], df = None, colunas = []):
        tam = 9 + len(df)
        for l, lst in enumerate(lista):
            worksheet.write(l,70,lst)
        int_val = f"$BS$1:$BS${len(lista)}"
  
        for letra in colunas:
            intervalo = f'{letra}10:{letra}{tam}'
            base = f'MATCH({letra}10, {int_val}, 0)'
            worksheet.conditional_format( intervalo, {
                'type':     'formula',
                'criteria': f'=ISNUMBER({base})',
                'format':   formato2
            })
            worksheet.conditional_format( intervalo, {
                'type':     'formula',
                'criteria': f'=ISNA({base})',
                'format':   formato1
            })

    linhasAMAIS=8
    if st: avl.progress(3, "Criando aba com os dados de abertura do VF...")

    TST_VL_VF_TAB_ROAf = imp_tbl_forma_000(nm_tbl="TST_VL_VF_TAB_ROAf", con=con, st=st, lst_cnv=[], workbook = workbook)
    worksheet1.merge_range('C5:U5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet1.write(linhasAMAIS-1, 2,'Tabela com os dados de abertura do ROA',titulo2)
    formatos = formato_def(TST_VL_VF_TAB_ROAf)
    x1 = ax_escreve_excel_md2(worksheet1, TST_VL_VF_TAB_ROAf, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)
    
    if st: avl.progress(65, "Criando aba com os dados de abertura do JOA...")
    TST_VL_JOA_TAB_ROAf = imp_tbl_forma_000(nm_tbl="TST_VL_JOA_TAB_ROAf", con=con, st=st, lst_cnv=[], workbook = workbook)
    worksheet2.merge_range('C5:U5', f'CÁLCULO PROVISÓRIO: {Empresa}', tituloP)
    worksheet2.write(linhasAMAIS-1, 2,'Tabela com os dados de abertura do JOA',titulo2)
    formatos = formato_def(TST_VL_JOA_TAB_ROAf)
    x1 = ax_escreve_excel_md2(worksheet2, TST_VL_JOA_TAB_ROAf, linhasAMAIS, formatos, texto=texto, titulo=titulo, st=st)

    workbook.close()
    if st: avl.progress(100, f"Finalizado e guardado em {dir_arq_saida}/Saida_ABT_F1.xlsx!")
    return "OK"