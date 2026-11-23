from .validador_D import (
                        VALIDADOR_D,

                    )
from .validador_funcoes import (
                                ler_dados_csv, 
                                validar_tabela_em_lotes, 
                                gerar_relatorio_erros, 
                                limpar_texto_latin1
                               )
from .imprimir_erros_MANUAL import (
                                        grafico_resultado, 
                                        imprime
                                    )

__version__ = "1.0.0"

__all__ = [

                "VALIDADOR_D",

                "ler_dados_csv", 
                "validar_tabela_em_lotes", 
                "gerar_relatorio_erros", 
                "limpar_texto_latin1",

                "grafico_resultado", 
                "imprime",

                "__version__",
            ]