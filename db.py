import sqlite3
import os

# Função para processar os arquivos .txt e retornar os dados
def processar_arquivo_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

        cpf = lines[0].strip()
        nome = lines[1].strip()
        data_nascimento = lines[2].strip()
        situacao_cadastral = lines[3].strip()
        data_inscricao = lines[4].strip()
        digito_verificador = lines[5].strip()
        horario_emissao = lines[6].strip()
        data_emissao = lines[7].strip()
        codigo_controle = lines[8].strip()
        
        return (cpf, nome, data_nascimento, situacao_cadastral, data_inscricao, digito_verificador, horario_emissao, data_emissao, codigo_controle)

def criar_bd():
    conn = sqlite3.connect('dados_cpf.db')
    cursor = conn.cursor()

    # Criar a tabela se não existir
    cursor.execute('''CREATE TABLE IF NOT EXISTS cpf_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        CPF INTEGER,
                        Nome TEXT,
                        Data_Nascimento TEXT,
                        Situacao_Cadastral TEXT,
                        Data_Inscricao TEXT,
                        Digito_Verificador TEXT,
                        Horario_Emissao TEXT,
                        Data_Emissao TEXT,
                        Codigo_Controle TEXT)''')

    conn.commit()
    conn.close()

# Função para inserir os dados no banco de dados
def inserir_dados(cpf, nome, data_nascimento, situacao_cadastral, data_inscricao, digito_verificador, horario_emissao, data_emissao, codigo_controle):
    conn = sqlite3.connect('dados_cpf.db')
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO cpf_data (CPF, Nome, Data_Nascimento, Situacao_Cadastral, Data_Inscricao, Digito_Verificador, Horario_Emissao, Data_Emissao, Codigo_Controle)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (cpf, nome, data_nascimento, situacao_cadastral, data_inscricao, digito_verificador, horario_emissao, data_emissao, codigo_controle))

    conn.commit()
    conn.close()

# Função para processar todos os arquivos .txt na pasta 'consultas' e inserir no banco de dados
def processar_arquivos_e_inserir():
    # Criar o banco de dados e a tabela
    criar_bd()

    # Diretório onde os arquivos .txt estão localizados
    dir_consultas = 'consultas2'

    # Iterar sobre todos os arquivos .txt na pasta
    for file_name in os.listdir(dir_consultas):
        if file_name.endswith('.txt'):
            file_path = os.path.join(dir_consultas, file_name)
            print(f"Processando {file_path}...")

            dados = processar_arquivo_txt(file_path)

            inserir_dados(*dados)

    print("Processamento e inserção concluídos!")

if __name__ == '__main__':
    processar_arquivos_e_inserir()
