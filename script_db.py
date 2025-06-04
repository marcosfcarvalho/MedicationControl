import os
import sqlite3
import sys

def get_caminho_banco(nome_arquivo):
    if getattr(sys, 'frozen', False):
        caminho_base = os.path.dirname(sys.executable)  # Caminho do .exe
    else:
        caminho_base = os.path.dirname(os.path.abspath(__file__))  # Caminho do .py
    return os.path.join(caminho_base, nome_arquivo)

CAMINHO_BANCO = get_caminho_banco("controle_medicamentos.db")

def conectar_banco():
    return sqlite3.connect(CAMINHO_BANCO)


def criar_tabela():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paciente (
            id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL unique collate nocase,
            stts INTEGER CHECK(stts IN (0, 1)) NOT NULL DEFAULT 1, -- verifica se o prontuario esta ativo=1 ou inativo=0 
            observacao TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicamento (
            id_medicamento INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL unique collate nocase,
            descricao text
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estoque (
            id_estoque INTEGER PRIMARY KEY AUTOINCREMENT,
            id_paciente INTEGER NOT NULL,
            id_medicamento INTEGER NOT NULL,
            dosagem_diaria REAL not null default 1,
            quantidade_atual REAL NOT NULL CHECK(quantidade_atual >= 0),
            alerta REAL NOT NULL CHECK(alerta >= 0),
            receita text CHECK(receita in ('feito', 'por fazer')) DEFAULT NULL,
            observacao TEXT,
            FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente) on delete cascade,
            FOREIGN KEY (id_medicamento) REFERENCES medicamento(id_medicamento) on delete cascade
        )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS configuracao (
            ultima_execucao DATE
        )
                   ''')

    conn.commit()
    conn.close()