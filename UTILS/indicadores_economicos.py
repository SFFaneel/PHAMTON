import pandas as pd
import os
from datetime import date

def busca_ipca(st=None):
    arq = 'tabelas/IPCA.csv'
    if os.path.isfile(arq):
        df_ipca = pd.read_csv(arq,sep="|", encoding="Latin-1")
        df_ipca['Dt_REF'] = pd.to_datetime(df_ipca['Dt_REF'], errors='coerce')
    else:
        df_ipca = pd.DataFrame()
    pos = df_ipca.columns.to_list().index("Dt_REF")
    if (len(df_ipca)==0) or ((date.today() - df_ipca.iloc[-1,pos].date()).days >= 70):
        try:
            url_ipca_csv = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=csv"
            url_ipca_csv_sidra = "https://apisidra.ibge.gov.br/values/t/1737/n1/1/v/2266/p/all"
            df_ipca = pd.read_json(url_ipca_csv_sidra)

        
            df_ipca = df_ipca.iloc[1:].copy()
            df_ipca = df_ipca.rename(columns={
                                        'V': 'Nr_IPCA',
                                        'D3C': 'periodo'
                                    })
            df_ipca['Dt_REF'] = pd.to_datetime(df_ipca['periodo'], format='%Y%m')
            df_ipca['Nr_IPCA'] = (
                                df_ipca['Nr_IPCA']
                                .str.replace(',', '.', regex=False)
                                .astype(float)
                            )
            df_ipca = df_ipca.sort_values("Dt_REF")

            df_ipca["VAR_MENSAL"] = (
                                    (df_ipca["Nr_IPCA"] / df_ipca["Nr_IPCA"].shift(1) - 1) * 100
                                )
            
            df_ipca = df_ipca[['Dt_REF', 'VAR_MENSAL', 'Nr_IPCA']]
            df_ipca.to_csv(arq,sep="|", encoding="Latin-1")
        except:
            df_ipca = pd.read_csv(arq,sep="|", encoding="Latin-1")
    return df_ipca