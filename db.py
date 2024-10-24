import sqlite3

def criar_bd():
    conn = sqlite3.connect('dados_cpf.db')
    cursor = conn.cursor()

    # Criar a tabela se não existir
    cursor.execute('''CREATE TABLE IF NOT EXISTS cpf_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        CPF TEXT,
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