# INSTRUÇÕES PARA INSTALAÇÃO E EXECUÇÃO

Apresenta-ses procedimentos necessários para configurar o ambiente Python, instalar as dependências e executar a aplicação **PHAMTON'S FANG**.

A aplicação pode ser instalada utilizando uma das seguintes alternativas:

- **Opção A — Visual Studio Code com Python e `venv`** (recomendada para instalações sem Anaconda).
- **Opção B — Anaconda ou Miniconda com Conda**.

É necessário escolher apenas uma das alternativas. Não é preciso criar dois ambientes virtuais.

## 1. Pré-requisitos

Antes de iniciar, verifique se o computador possui:

- Python 3.12 ou uma versão compatível com as dependências do projeto;
- Visual Studio Code (para a Opção A);
- Anaconda ou Miniconda (para a Opção B);
- Git, caso o projeto seja obtido por meio do GitLab;
- Acesso à internet para instalar as dependências.

**Observação:** o ambiente utilizado no desenvolvimento também pode ser criado com Python 3.11. Recomenda-se utilizar a versão do Python que tenha sido validada com o `requirements.txt` do projeto.

## 2. Obter os arquivos do projeto

Clone o repositório do GitLab ou obtenha uma cópia dos arquivos do projeto.

Abra o terminal e navegue até a pasta principal, onde estão localizados `main.py` e `requirements.txt`.

Exemplo no Windows:

```powershell
cd E:\BulldozeRR
```

O caminho deve ser ajustado conforme o local em que o projeto foi armazenado.

---

# OPÇÃO A — VISUAL STUDIO CODE COM PYTHON VENV

## 3A. Criar o ambiente virtual

Abra a pasta do projeto no Visual Studio Code e acesse **Terminal → Novo Terminal**.

No terminal PowerShell, execute:

```powershell
py -3.12 -m venv .PHAMTON
```

Ou com Python 3.11, utilize:

```powershell
py -3.11 -m venv .PHAMTON
```

Esse procedimento cria a pasta `.PHAMTON` dentro do diretório do projeto.

## 4A. Ativar o ambiente virtual

No terminal PowerShell:

```powershell
.\.PHAMTON\Scripts\Activate.ps1
```

Após a ativação, o terminal deverá apresentar o nome do ambiente virtual no início da linha.

Para confirmar qual interpretador Python está sendo utilizado:

```powershell
python -c "import sys; print(sys.executable)"
```

O resultado deverá apontar para o executável localizado na pasta `.PHAMTON`.

No Visual Studio Code, também é possível selecionar o interpretador em:

**Ctrl + Shift + P → Python: Select Interpreter → `.PHAMTON\Scripts\python.exe`**

## 5A. Instalar as dependências

Atualize o gerenciador de pacotes:

```powershell
python -m pip install --upgrade pip
```

Em seguida, instale as bibliotecas do projeto:

```powershell
python -m pip install --no-cache-dir -r requirements.txt
```

O parâmetro `--no-cache-dir` evita a reutilização do cache de downloads do pip durante a instalação.

Após a conclusão, verifique a consistência das dependências:

```powershell
python -m pip check
```

Se não houver incompatibilidades, deverá aparecer:

```text
No broken requirements found.
```

**IMPORTANTE:** o arquivo `requirements.txt` deve estar na pasta em que o comando é executado. Conflitos de versões entre bibliotecas precisam ser corrigidos no próprio arquivo; a limpeza do cache não resolve incompatibilidades de dependências.

## 6A. Executar a aplicação

Com o ambiente virtual ativado:

```powershell
python -m streamlit run main.py --server.port 8502
```

A aplicação poderá ser acessada pelo navegador no endereço:

http://localhost:8502

Caso o navegador não seja aberto automaticamente, copie o endereço `Local URL` apresentado no terminal.

Para interromper a execução, pressione **Ctrl + C**.

## 7A. Desativar o ambiente virtual

Após encerrar a aplicação, execute:

```powershell
deactivate
```

## 8A. Remover o ambiente virtual (OPCIONAL)

Caso seja necessário reconstruir completamente o ambiente, primeiro encerre a aplicação e desative o ambiente virtual.

No PowerShell, a partir da raiz do projeto:

```powershell
Remove-Item -Recurse -Force .PHAMTON
```

Para recriá-lo:

```powershell
py -3.12 -m venv .PHAMTON
```

Ou utilize Python 3.11, caso essa seja a versão utilizada.

**ATENÇÃO:** não é necessário remover ou recriar o ambiente após cada utilização.

---

# OPÇÃO B — ANACONDA OU MINICONDA

## 3B. Criar o ambiente Conda

Abra o Anaconda Prompt ou um terminal com o Conda configurado e navegue até a pasta do projeto.

Execute:

```powershell
conda create --name PHAMTON python=3.12 pip
```

Se o projeto estiver validado com Python 3.11, substitua `3.12` por `3.11`.

Quando solicitado, digite `y` e pressione Enter para confirmar a instalação.

## 4B. Ativar o ambiente Conda

Execute:

```powershell
conda activate PHAMTON
```

## 5B. Instalar as dependências

Atualize o pip:

```powershell
python -m pip install --upgrade pip
```

Instale as bibliotecas:

```powershell
python -m pip install --no-cache-dir -r requirements.txt
```

Verifique as dependências:

```powershell
python -m pip check
```

## 6B. Executar a aplicação

```powershell
python -m streamlit run main.py --server.port 8502
```

Acesse:

http://localhost:8502

Para interromper a aplicação, pressione **Ctrl + C**.

## 7B. Desativar o ambiente Conda

```powershell
conda deactivate
```

## 8B. Remover o ambiente Conda (OPCIONAL)

Após desativar o ambiente:

```powershell
conda env remove --name PHAMTON
```

A remoção é opcional e não precisa ser realizada após cada utilização.

---

## 9. Execuções posteriores

Após a configuração inicial, não será necessário recriar o ambiente virtual nem reinstalar as dependências sempre que desejar executar a aplicação.

### Visual Studio Code / venv

Abra o terminal na pasta do projeto:

```powershell
.\.PHAMTON\Scripts\Activate.ps1
python -m streamlit run main.py --server.port 8502
```

Para encerrar:

```powershell
# Pressione Ctrl + C
deactivate
```

### Anaconda / Miniconda

```powershell
conda activate PHAMTON
python -m streamlit run main.py --server.port 8502
```

Para encerrar:

```powershell
# Pressione Ctrl + C
conda deactivate
```

Caso o ambiente tenha sido removido, será necessário repetir os procedimentos de criação e instalação.

## 10. Solução de problemas

### O PowerShell não permite ativar o ambiente

Se aparecer um erro relacionado à política de execução de scripts, execute na sessão atual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Depois tente novamente:

```powershell
.\.PHAMTON\Scripts\Activate.ps1
```

Essa configuração é temporária e se aplica apenas à sessão atual do PowerShell.

### O comando `streamlit` não é reconhecido

Execute a aplicação utilizando o interpretador Python do ambiente:

```powershell
python -m streamlit run main.py --server.port 8502
```

Se o módulo não estiver instalado, verifique se o ambiente correto está ativo e se a instalação do `requirements.txt` foi concluída.

### O pip apresenta conflitos de dependências

Verifique a mensagem de erro para identificar as bibliotecas com restrições incompatíveis.

Após ajustar o `requirements.txt`, execute novamente:

```powershell
python -m pip install --no-cache-dir -r requirements.txt
```

Não é recomendado utilizar `--no-deps` para contornar conflitos, pois isso pode produzir um ambiente inconsistente.

### A porta 8502 já está em uso

Encerre a instância anterior da aplicação ou utilize outra porta:

```powershell
python -m streamlit run main.py --server.port 8503
```

## 11. Documentação

O projeto disponibiliza documentação complementar em HTML:

[Manual de utilização em HTML](DOCUMENTACAO/HTML/index.html)

Abra o arquivo no navegador para consultar o fluxo das telas Streamlit e as funcionalidades documentadas.

---

**Observação para versionamento:** o ambiente virtual não deve ser incluído no repositório GitLab. Mantenha o código-fonte, a documentação, o `requirements.txt` e o `.gitignore` versionados.