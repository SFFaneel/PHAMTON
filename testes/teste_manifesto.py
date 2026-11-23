import hashlib
import json
from pathlib import Path
import pandas as pd
import pytest
import sys, tempfile
import MANIFESTO as modulo

from MANIFESTO import carregar_csv, comparar, criar_manifesto_multi, dados_equivalentes, sha256

IS_WINDOWS = sys.platform == "win32"
DOWNLOADS = Path.home() / "Downloads"
DIRETORIO_TESTES = DOWNLOADS / "auditoria_pytest"

@pytest.fixture(scope="session", autouse=True)
def pasta_sessao():
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    DIRETORIO_TESTES.mkdir(parents=True, exist_ok=True)
    pasta = Path(tempfile.mkdtemp(prefix='sessao-', dir=DIRETORIO_TESTES))
    yield pasta

@pytest.fixture
def ambiente(pasta_sessao, tmp_path):
    pasta = pasta_sessao / tmp_path.name
    pasta.mkdir(parents=True, exist_ok=False)
    arquivo = pasta / 'clientes.csv'
    raiz = pasta / 'auditoria'

    def escrever(texto, *, encoding='utf-8'):
        arquivo.write_text(texto, encoding=encoding)
        return arquivo

    def processar(id_arquivo='CLIENTES', **kwargs):
        return criar_manifesto_multi(arquivo, id_arquivo, raiz, encoding='utf-8', **kwargs)

    return arquivo, raiz, escrever, processar

def indice(raiz, tipo='CLIENTES'):
    return json.loads((raiz / tipo / 'MANIFESTOS' / 'indice.json').read_text(encoding='utf-8'))

def requer_parquet():
    pytest.importorskip('pyarrow', reason='Testes de snapshots exigem pyarrow')

def teste_sha256_reflete_bytes(tmp_path):
    arquivo = tmp_path / 'entrada.csv'
    arquivo.write_bytes(b'ID|NOME\n1|ANA\n')
    assert sha256(arquivo) == hashlib.sha256(arquivo.read_bytes()).hexdigest()
    anterior = sha256(arquivo)
    arquivo.write_bytes(b'ID|NOME\r\n1|ANA\r\n')
    assert sha256(arquivo) != anterior

def teste_carregar_csv_preserva_zeros_e_vazios(tmp_path):
    arquivo = tmp_path / 'dados.csv'
    arquivo.write_text('ID|NOME|OBS\n001|ANA|\n002|JOAO|OK\n', encoding='utf-8')
    df, chave = carregar_csv(arquivo, 'ID', '|', 'utf-8')
    assert chave == 'ID'
    assert df.index.tolist() == ['001', '002']
    assert df.loc['001', 'OBS'] == ''

@pytest.mark.parametrize('conteudo,erro', [
                            ('ID|NOME\n1|ANA\n1|JOAO\n', 'duplicados'),
                            ('ID|NOME\n|ANA\n', 'vazios'),
                        ])
def teste_carregar_csv_rejeita_ids_invalidos(tmp_path, conteudo, erro):
    arquivo = tmp_path / 'dados.csv'
    arquivo.write_text(conteudo, encoding='utf-8')
    with pytest.raises(ValueError, match=erro):
        carregar_csv(arquivo, 'ID', '|', 'utf-8')

def teste_comparar_inclusoes_exclusoes_e_campos():
    antigo = pd.DataFrame({'ID': ['1', '2'], 'NOME': ['ANA', 'JOAO']}).set_index('ID')
    novo = pd.DataFrame({'ID': ['2', '3'], 'NOME': ['JOSE', 'MARIA']}).set_index('ID')
    incluidos, excluidos, alterados = comparar(antigo, novo, 'ID')
    assert incluidos.to_dict('records') == [{'ID': '3', 'NOME': 'MARIA'}]
    assert excluidos.to_dict('records') == [{'ID': '1', 'NOME': 'ANA'}]
    assert alterados.to_dict('records') == [
                                                {'ID': '2', 'coluna': 'NOME', 'valor_anterior': 'JOAO', 'valor_novo': 'JOSE'}
                                            ]

def teste_dados_equivalentes_ignora_ordem():
    antigo = pd.DataFrame({'ID': ['1', '2'], 'NOME': ['ANA', 'JOAO'], 'UF': ['SP', 'RJ']}).set_index('ID')
    novo = pd.DataFrame({'UF': ['RJ', 'SP'], 'ID': ['2', '1'], 'NOME': ['JOAO', 'ANA']}).set_index('ID')
    assert dados_equivalentes(antigo, novo)
    novo.loc['1', 'NOME'] = 'MARIA'
    assert not dados_equivalentes(antigo, novo)

def teste_primeira_versao_snapshot_e_manifesto(ambiente):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n001|ANA\n002|JOAO\n')
    resultado = processar()
    assert resultado['status'] == 'nova_versao'
    assert resultado['versao'] == 'v0001'
    assert resultado['incluidos'] == 2
    assert resultado['excluidos'] == 0
    assert resultado['alteracao_dados'] is True
    pasta = raiz / 'CLIENTES'
    snapshot = pasta / resultado['snapshot']
    assert snapshot.suffix == '.parquet'
    assert sha256(snapshot) == resultado['sha256_snapshot']
    assert pd.read_parquet(snapshot).loc['001', 'NOME'] == 'ANA'
    assert (pasta / 'MANIFESTOS' / 'v0001.json').exists()
    for nome in ('incluidos', 'excluidos', 'alterados'):
        rel = resultado['relatorios'][nome]
        caminho = pasta / rel['caminho']
        assert caminho.exists()
        assert sha256(caminho) == rel['sha256']
    assert len(indice(raiz)['ingestoes']) == 1

def teste_hash_igual_nao_cria_versao_mas_registra_ingestao(ambiente):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n')
    primeira = processar()
    segunda = processar()
    assert segunda['status'] == 'sem_alteracao'
    assert segunda['motivo'] == 'hash_identico'
    assert segunda['versao'] == primeira['versao']
    historico = indice(raiz)
    assert len(historico['versoes']) == 1
    assert len(historico['ingestoes']) == 2
    assert historico['ingestoes'][1]['sha256_origem'] == primeira['sha256_origem']

def teste_hash_diferente_com_dados_iguais_cria_versao(ambiente):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n2|JOAO\n')
    primeira = processar()
    escrever('ID|NOME\n2|JOAO\n1|ANA\n')
    segunda = processar()
    assert segunda['status'] == 'nova_versao'
    assert segunda['versao'] == 'v0002'
    assert segunda['sha256_origem'] != primeira['sha256_origem']
    assert segunda['alteracao_dados'] is False
    assert (segunda['incluidos'], segunda['excluidos'], segunda['campos_alterados']) == (0, 0, 0)
    assert len(indice(raiz)['versoes']) == 2
    assert len(indice(raiz)['ingestoes']) == 2

def teste_modificacoes_registradas_no_manifesto(ambiente):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n2|JOAO\n')
    processar()
    escrever('ID|NOME\n2|JOSE\n3|MARIA\n')
    segunda = processar()
    assert segunda['versao_anterior'] == 'v0001'
    assert segunda['alteracao_dados'] is True
    assert segunda['incluidos'] == 1
    assert segunda['excluidos'] == 1
    assert segunda['registros_alterados'] == 1
    assert segunda['campos_alterados'] == 1
    alterados = pd.read_parquet(raiz / 'CLIENTES' / segunda['relatorios']['alterados']['caminho'])
    assert alterados.iloc[0].to_dict() == {
                                                'ID': '2', 'coluna': 'NOME', 'valor_anterior': 'JOAO', 'valor_novo': 'JOSE'
                                            }

def teste_alteracao_de_esquema(ambiente):
    requer_parquet()
    _, _, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n')
    processar()
    escrever('ID|NOME|UF\n1|ANA|SP\n')
    segunda = processar()
    assert segunda['colunas_adicionadas'] == ['UF']
    assert segunda['colunas_removidas'] == []
    assert segunda['alteracao_dados'] is True
    escrever('ID|UF\n1|SP\n')
    terceira = processar()
    assert terceira['colunas_removidas'] == ['NOME']
    assert terceira['alteracao_dados'] is True

def teste_historicos_independentes_por_tipo(ambiente):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n')
    a = processar('CLIENTES')
    b = processar('PRODUTOS')
    assert a['versao'] == b['versao'] == 'v0001'
    assert len(indice(raiz, 'CLIENTES')['versoes']) == 1
    assert len(indice(raiz, 'PRODUTOS')['versoes']) == 1

def teste_snapshot_adulterado_e_detectado(ambiente):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n')
    primeira = processar()
    snapshot = raiz / 'CLIENTES' / primeira['snapshot']
    snapshot.write_bytes(snapshot.read_bytes() + b'alteracao')
    escrever('ID|NOME\n1|JOSE\n')
    with pytest.raises(ValueError, match='Integridade do snapshot'):
        processar()
    assert len(indice(raiz)['versoes']) == 1

def teste_csv_invalido_nao_publica_versao(ambiente):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n')
    processar()
    escrever('ID|NOME\n1|ANA\n1|JOAO\n')
    with pytest.raises(ValueError, match='duplicados'):
        processar()
    assert len(indice(raiz)['versoes']) == 1
    assert len(indice(raiz)['ingestoes']) == 1
    assert not (raiz / 'CLIENTES' / 'VERSOES' / 'v0002.parquet').exists()

def teste_arquivo_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        criar_manifesto_multi(tmp_path / 'ausente.csv', 'CLIENTES', tmp_path / 'auditoria')

def teste_id_arquivo_invalido(tmp_path):
    arquivo = tmp_path / 'dados.csv'
    arquivo.write_text('ID|NOME\n1|ANA\n', encoding='utf-8')
    with pytest.raises(ValueError, match='id_arquivo'):
        criar_manifesto_multi(arquivo, '../CLIENTES', tmp_path / 'auditoria', encoding='utf-8')

def teste_arquivo_origem_dentro_da_auditoria(tmp_path):
    raiz = tmp_path / 'auditoria'
    raiz.mkdir()
    arquivo = raiz / 'dados.csv'
    arquivo.write_text('ID|NOME\n1|ANA\n', encoding='utf-8')
    with pytest.raises(ValueError, match='dentro da pasta'):
        criar_manifesto_multi(arquivo, 'CLIENTES', raiz, encoding='utf-8')

def teste_snapshot_completo_preserva_todos_os_valores(ambiente):
    requer_parquet()
    arquivo, raiz, escrever, processar = ambiente
    escrever('ID|NOME|CEP|OBS\n001|ANA|01001000|\n002|JOAO|00000001|OK\n')
    resultado = processar()
    snapshot = raiz / 'CLIENTES' / resultado['snapshot']
    dados = pd.read_parquet(snapshot, engine='pyarrow')
    assert dados.index.name == 'ID'
    assert dados.index.tolist() == ['001', '002']
    assert dados.columns.tolist() == ['NOME', 'CEP', 'OBS']
    assert dados.loc['001'].to_dict() == {'NOME': 'ANA', 'CEP': '01001000', 'OBS': ''}
    assert dados.loc['002'].to_dict() == {'NOME': 'JOAO', 'CEP': '00000001', 'OBS': 'OK'}
    assert len(dados) == resultado['total_registros'] == 2

def teste_manifesto_json_hashes_contagens_e_relatorios(ambiente):
    requer_parquet()
    arquivo, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n2|JOAO\n')
    processar()
    escrever('ID|NOME\n2|JOSE\n3|MARIA\n')
    resultado = processar()
    pasta = raiz / 'CLIENTES'
    manifesto = json.loads((pasta / 'MANIFESTOS' / 'v0002.json').read_text(encoding='utf-8'))
    assert manifesto['versao'] == 'v0002'
    assert manifesto['versao_anterior'] == 'v0001'
    assert manifesto['sha256_origem'] == hashlib.sha256(arquivo.read_bytes()).hexdigest()
    assert manifesto['sha256_snapshot'] == sha256(pasta / manifesto['snapshot'])
    assert manifesto['total_registros'] == 2
    assert (manifesto['incluidos'], manifesto['excluidos']) == (1, 1)
    assert (manifesto['registros_alterados'], manifesto['campos_alterados']) == (1, 1)
    for nome, quantidade in [('incluidos', 1), ('excluidos', 1), ('alterados', 1)]:
        rel = manifesto['relatorios'][nome]
        caminho = pasta / rel['caminho']
        assert caminho.is_file()
        assert sha256(caminho) == rel['sha256']
        assert len(pd.read_parquet(caminho, engine='pyarrow')) == quantidade
    assert indice(raiz)['versoes'][-1] == manifesto

def teste_tipos_tem_indices_e_snapshots_independentes(ambiente):
    requer_parquet()
    arquivo, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n')
    clientes = processar('CLIENTES')
    escrever('ID|NOME\n1|PRODUTO A\n')
    produtos = processar('PRODUTOS')
    assert clientes['versao'] == produtos['versao'] == 'v0001'
    assert len(indice(raiz, 'CLIENTES')['versoes']) == 1
    assert len(indice(raiz, 'PRODUTOS')['versoes']) == 1
    df_clientes = pd.read_parquet(raiz / 'CLIENTES' / clientes['snapshot'])
    df_produtos = pd.read_parquet(raiz / 'PRODUTOS' / produtos['snapshot'])
    assert df_clientes.loc['1', 'NOME'] == 'ANA'
    assert df_produtos.loc['1', 'NOME'] == 'PRODUTO A'

def teste_esquema_adicao_e_remocao_manifestos_e_snapshots(ambiente):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n')
    processar()
    escrever('ID|NOME|UF\n1|ANA|SP\n')
    segundo = processar()
    assert segundo['colunas_adicionadas'] == ['UF']
    assert segundo['colunas_removidas'] == []
    assert pd.read_parquet(raiz / 'CLIENTES' / segundo['snapshot']).loc['1', 'UF'] == 'SP'
    escrever('ID|UF\n1|SP\n')
    terceiro = processar()
    assert terceiro['colunas_adicionadas'] == []
    assert terceiro['colunas_removidas'] == ['NOME']
    assert pd.read_parquet(raiz / 'CLIENTES' / terceiro['snapshot']).columns.tolist() == ['UF']

@pytest.mark.parametrize('ponto_falha', ['snapshot', 'relatorio', 'indice'])
def teste_falha_publicacao_preserva_indice(ambiente, monkeypatch, ponto_falha):
    requer_parquet()
    _, raiz, escrever, processar = ambiente
    escrever('ID|NOME\n1|ANA\n')
    processar()
    indice_path = raiz / 'CLIENTES' / 'MANIFESTOS' / 'indice.json'
    indice_antes = indice_path.read_bytes()
    escrever('ID|NOME\n1|MARIA\n')

    if ponto_falha == 'snapshot':
        original = pd.DataFrame.to_parquet
        def falhar_snapshot(self, path, *args, **kwargs):
            if Path(path).name == 'snapshot.parquet':
                raise OSError('Falha simulada no snapshot')
            return original(self, path, *args, **kwargs)
        monkeypatch.setattr(pd.DataFrame, 'to_parquet', falhar_snapshot)
    elif ponto_falha == 'relatorio':
        original = pd.DataFrame.to_parquet
        def falhar_relatorio(self, path, *args, **kwargs):
            if Path(path).name == 'alterados.parquet':
                raise OSError('Falha simulada no relatório')
            return original(self, path, *args, **kwargs)
        monkeypatch.setattr(pd.DataFrame, 'to_parquet', falhar_relatorio)
    else:
        import inspect

        modulo_real = inspect.getmodule(criar_manifesto_multi)

        assert modulo_real is not None

        original = modulo_real.atomic_json

        def falhar_indice(path, dados):
            if Path(path).resolve() == indice_path.resolve():
                raise OSError(
                    'Falha simulada na publicação do índice'
                )

            return original(path, dados)

        monkeypatch.setattr(
                                modulo_real,
                                'atomic_json',
                                falhar_indice
                            )

    with pytest.raises(OSError, match='Falha simulada'):
        processar()
    assert indice_path.read_bytes() == indice_antes
    assert len(indice(raiz)['versoes']) == 1
    assert len(indice(raiz)['ingestoes']) == 1
    pasta = raiz / 'CLIENTES'
    assert not (pasta / 'VERSOES' / 'v0002.parquet').exists()
    assert not (pasta / 'MANIFESTOS' / 'v0002.json').exists()
    assert not (pasta / 'COMPARACOES' / 'v0001_v0002').exists()

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
                            str(DIRETORIO_TESTES / "resultado_manifestos.xml")
                        ])
                    )