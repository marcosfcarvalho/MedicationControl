import sqlite3
import os
import datetime

DB_PATH = 'controle_medicamentos.db'

def conectar_banco():
    conn = sqlite3.connect(DB_PATH)
    return conn

def criar_tabela():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paciente (
            id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL unique,
            stts INTEGER CHECK(stts IN (0, 1)) NOT NULL DEFAULT 1, -- verifica se o prontuario esta ativo
            observacao TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicamento (
            id_medicamento INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao text
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estoque (
            id_estoque INTEGER PRIMARY KEY AUTOINCREMENT,
            id_paciente INTEGER NOT NULL,
            id_medicamento INTEGER NOT NULL,
            dosagem_diaria INTEGER not null default 1,
            miligrama REAL not null,
            quantidade_atual INT NOT NULL,
            alerta INT NOT NULL,
            observacao TEXT,
            FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente) on delete cascade,
            FOREIGN KEY (id_medicamento) REFERENCES medicamento(id_medicamento) on delete cascade
        )
    ''')

    conn.commit()
    conn.close()

def inserir_paciente(nome, observacao):
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO paciente (nome, observacao)
            VALUES (?, ?)
        ''', (nome, observacao))
        conn.commit()
        # Captura o ID gerado
        id_paciente = cursor.lastrowid
        print(f"Paciente inserido com sucesso! ID: {id_paciente}")
        return id_paciente
    except sqlite3.IntegrityError:
        print("Paciente já cadastrado.")
        return None
    finally:
        conn.close()

def inserir_medicamento(nome, descricao):
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO medicamento (nome, descricao)
            VALUES (?, ?)
        ''', (nome, descricao))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Medicamento já cadastrado.")
    finally:
        conn.close()

def inserir_estoque(id_paciente, id_medicamento, dosagem_diaria, miligrama, quantidade_atual, alerta, observacao):
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO estoque (id_paciente, id_medicamento, dosagem_diaria, miligrama, quantidade_atual, alerta, observacao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (id_paciente, id_medicamento, dosagem_diaria, miligrama, quantidade_atual, alerta, observacao))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Estoque já cadastrada.")
    finally:
        conn.close()


def buscar_medicamento_por_nome(nome_medicamento):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id_medicamento FROM medicamento WHERE nome = ?
    ''', (nome_medicamento,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None

def menuprincipal():
    print ("""
          1- Cadastrar novo paciente
          2- Ajustar medicamentos
          3- consultar medicamentos/pacientes
          4- declarar alta/reativar prontuario
          5- cadastrar medicamento
          6- sair
          """)

criar_tabela()

while True:
    menuprincipal()
    opcao = int(input("Escolha uma opção: "))

    match opcao:
        case 1:
            nome = input("Digite o nome do paciente: ")
            obs = input("Digite uma observação: ")
            inserir_paciente(nome, obs)
            id_paciente = inserir_paciente(nome, obs)
            x = int(input("Quantos medicamentos o paciente faz uso? "))
            for i in range(x):
                print(f"Medicamento {i+1}:")
                nome = input("Digite o nome do medicamento: ")
                id_medicamento = buscar_medicamento_por_nome(nome)
                while id_medicamento is None:
                    print("Medicamento não encontrado.")
                    nome = input("Digite o nome do medicamento: ")
                    id_medicamento = buscar_medicamento_por_nome(nome)
                dosagem_diaria = input("Digite a dosagem diária: ")
                miligrama = input("Digite a dosagem em miligramas: ")
                quantidade_atual = input("Digite a quantidade atual: ")
                alerta = input("Digite com quantos comprimidos você gostaria de ser alertado: ")
                observacao = input("Digite uma observação: ")
                inserir_estoque(id_paciente, id_medicamento, dosagem_diaria, miligrama, quantidade_atual, alerta, observacao)

        case 2:
            id_paciente = int(input("Digite o ID do paciente: "))
            id_medicamento = int(input("Digite o ID do medicamento: "))
            dosagem_fixa = int(input("A dosagem é fixa? (1 para sim, 0 para não): "))
            dosagem_diaria = int(input("Digite a dosagem diária: "))
            observacao = input("Digite uma observação: ")
            
            
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO prescricao (id_paciente, id_medicamento, dosagem_fixa, dosagem_diaria, observacao)
                VALUES (?, ?, ?, ?, ?)
            ''', (id_paciente, id_medicamento, dosagem_fixa, dosagem_diaria, observacao))
            conn.commit()
            conn.close()
            print("Medicamento ajustado com sucesso.")

        case 3:
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id_paciente, nome, observacao FROM paciente WHERE stts = 1
            ''')
            pacientes = cursor.fetchall()
            print("Pacientes cadastrados:\n\n")
            for paciente in pacientes:
                print(f"ID: {paciente[0]}, Nome: {paciente[1]}, Observação: {paciente[2]}")
            conn.close()

        case 4:
            id_paciente = int(input("Digite o ID do paciente: "))
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE paciente SET stts = 0 WHERE id_paciente = ?
            ''', (id_paciente,))
            conn.commit()
            conn.close()
            print("Paciente teve alta.")

        case 5:
            nome = input("Digite o nome do medicamento: ")
            tipo = input("Digite o tipo do medicamento: ")
            descricao = input("Digite uma descrição: ")
            inserir_medicamento(nome, tipo, descricao)

        
        case 6:
            print("Saindo do sistema...")
            exit()
            break
        case _:
            print("Opção inválida!")

