import sqlite3
from datetime import datetime
import os

# Define o caminho do banco de dados relativo à raiz do projeto
# Assumindo que a execução ocorre na raiz (onde está run.py)
DB_NAME = "biblioteca.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Permite acessar colunas por nome
    return conn

def inicializar_banco():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela Usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id TEXT PRIMARY KEY,
        nome TEXT,
        email TEXT,
        senha TEXT,
        cpf TEXT,
        tipo TEXT
    )
    ''')

    # Tabela Itens
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS itens (
        id TEXT PRIMARY KEY, -- UUID ou Inteiro, dependendo da sua implementação atual
        tipo TEXT, -- 'livro' ou 'ebook'
        nome TEXT,
        autor TEXT,
        isbn TEXT,
        categoria TEXT,
        paginas INTEGER,
        status TEXT,
        imagem_url TEXT,
        imagem_arquivo TEXT,
        extra_info TEXT -- Para URL/Arquivo de ebook
    )
    ''')

    # Tabela Empréstimos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS emprestimos (
        id TEXT PRIMARY KEY,
        item_id TEXT,
        membro_id TEXT,
        data_emprestimo TIMESTAMP,
        data_devolucao TIMESTAMP,
        data_quitacao TIMESTAMP,
        quantidade_renovacoes INTEGER,
        status TEXT,
        multa_valor REAL,
        multa_paga BOOLEAN,
        FOREIGN KEY(item_id) REFERENCES itens(id),
        FOREIGN KEY(membro_id) REFERENCES usuarios(id)
    )
    ''')
    
    # Tabela Reservas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reservas (
        id TEXT PRIMARY KEY,
        item_id TEXT,
        membro_id TEXT,
        data_reserva TIMESTAMP,
        data_cancelamento TIMESTAMP,
        data_finalizacao TIMESTAMP,
        status TEXT,
        FOREIGN KEY(item_id) REFERENCES itens(id),
        FOREIGN KEY(membro_id) REFERENCES usuarios(id)
    )
    ''')

    conn.commit()
    conn.close()
