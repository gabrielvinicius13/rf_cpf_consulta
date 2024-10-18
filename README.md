# Automação de Consulta de CPF

Este projeto automatiza a consulta da situação de CPFs no site da Receita Federal, utilizando **Playwright** e **Requests**. Os resultados são salvos em arquivos de texto.

## Configuração do Ambiente

### 1. Criar e Ativar o Ambiente Virtual

Crie um ambiente virtual para o projeto:

```bash
python -m venv venv
```

Ative o ambiente virtual:

- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

### 2. Instalar Dependências

Com o ambiente virtual ativado, instale as dependências necessárias:

```bash
pip install -r requirements.txt
```

### 3. Instalar Playwright

Após instalar as dependências, execute o seguinte comando para instalar os navegadores do Playwright:

```bash
playwright install
```

## Estrutura do Projeto

- **`nome_caged.csv`**: Arquivo CSV com CPFs e datas de nascimento.
- **`consultas/`**: Diretório onde os resultados das consultas serão salvos.
- **`main.py`**: Script principal que contém o código de automação.

## Executar o Script

Para iniciar o processo de consulta, execute:

```bash
python main.py
```

Os resultados serão salvos em arquivos `.txt` no diretório `consultas/`.

---
