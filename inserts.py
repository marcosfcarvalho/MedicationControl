import sqlite3
import time
from script_db import conectar_banco
from clear import limpa_tela
from confirm_number import confirma_int, confirma_float
from searches import buscar_medicamento_por_nome, consultar_medicamntos, obter_id_precrisao


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
        print(f"    Paciente inserido com sucesso! ID: {id_paciente}")
        return id_paciente
    except sqlite3.IntegrityError:
        print(" Paciente já cadastrado.")
        return None
    finally:
        conn.close()

def inserir_medicamento(nome, descricao, conn=None, cursor=None):
    if conn is None or cursor is None:
        conn = conectar_banco()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO medicamento (nome, descricao)
            VALUES (?, ?)
        ''', (nome, descricao))
        conn.commit()
        print(f"Medicamento '{nome}' inserido com sucesso!")
        time.sleep(1.5)
        limpa_tela()

def inserir_estoque(id_paciente, id_medicamento, dosagem_diaria, quantidade_atual, alerta, observacao):
    conn = conectar_banco()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO estoque (id_paciente, id_medicamento, dosagem_diaria, quantidade_atual, alerta, observacao)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (id_paciente, id_medicamento, dosagem_diaria, quantidade_atual, alerta, observacao))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Estoque já cadastrada.")
    finally:
        conn.close()

def cadastrar_paciente_com_medicamentos():
    conn = conectar_banco()
    cursor = conn.cursor()

    try:
        conn.execute('BEGIN TRANSACTION')  # Inicia uma transação

        nome_p = input("    Digite o nome do paciente: ")
        obs = input("    Digite uma observação: ")
        cursor.execute('''
            INSERT INTO paciente (nome, observacao)
            VALUES (?, ?)
        ''', (nome_p, obs))
        id_paciente = cursor.lastrowid

        x = confirma_int(input("     Quantos medicamentos o paciente faz uso? Digite um número: "))
        limpa_tela()
        i = 0
        while i < x:
            print(f"\n  Medicamento {i+1}:")
            nome_m = input("\n    Digite o nome do medicamento: ")
            id_medicamento = buscar_medicamento_por_nome(nome_m)
            if id_medicamento is None:
                opcao = confirma_int(input("    Deseja cadastrar um novo medicamento? (1-sim/2-não/3-consultar medicamentos/0-sair): "))
                limpa_tela()
                if opcao == 1:
                    nome_m = input("      Digite o nome do novo medicamento: ")
                    descricao = input("     Digite uma descrição: ")
                    limpa_tela()
                    cursor.execute('''
                    INSERT INTO medicamento (nome, descricao)
                    VALUES (?, ?)
                    ''', (nome_m, descricao))
                    id_medicamento = cursor.lastrowid  # Pega o ID do medicamento recém-inserido
                    time.sleep(4)
                    limpa_tela()
                elif opcao == 2:
                    print(" Tente novamente.")
                    continue
                elif opcao == 3:
                    consultar_medicamntos()
                    nome_m = input("     Digite o nome do medicamento: ")
                    id_medicamento = buscar_medicamento_por_nome(nome_m)
                    if id_medicamento is None:
                        print(" Medicamento não encontrado.")
                        time.sleep(2)
                        limpa_tela()
                        continue
                elif opcao == 0:
                    print(" Saindo do cadastro de paciente...")
                    time.sleep(1.5)
                    limpa_tela()
                    return                  

            dosagem_diaria = confirma_float(input("    Digite a quantidade de comprimidos/dia: "))
            quantidade_atual = confirma_float(input("      Digite a quantidade atual: "))
            alerta = confirma_float(input("    Digite com quantos comprimidos você gostaria de ser alertado: "))
            observacao = input("    Digite o Responsavel: ")
            limpa_tela()

            cursor.execute('''
                INSERT INTO estoque (id_paciente, id_medicamento, dosagem_diaria, quantidade_atual, alerta, observacao)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (id_paciente, id_medicamento, dosagem_diaria, quantidade_atual, alerta, observacao))

            i += 1

        conn.commit()  # Confirma tudo de uma vez

        print(f"\n    Paciente {nome_p} e seus medicamentos foram cadastrados com sucesso!")
        time.sleep(1.5)
        limpa_tela()

    except Exception as e:
        conn.rollback()  # Cancela tudo em caso de erro
        print(f"\n  Erro ao cadastrar paciente e medicamentos: {e}")

    finally:
        conn.close()

def cadastrar_nova_prescricao(id_paciente):
    conn = conectar_banco()
    cursor = conn.cursor()

    nome_medicamento = input("Digite o nome do medicamento: ")
    id_medicamento = buscar_medicamento_por_nome(nome_medicamento)
    if id_medicamento is None:
        print("Medicamento não encontrado.")
        time.sleep(2)
        limpa_tela()
        return
    # Verifica se o medicamento já está cadastrado para o paciente
    id_estoque = obter_id_precrisao(id_paciente, id_medicamento)
    if id_estoque is not None:
        print("Esse medicamento já está cadastrado para esse paciente.")
        time.sleep(2)
        limpa_tela()
        return

    dosagem_diaria = confirma_float(input("Digite a quantidade de comprimidos/dia o paciente toma: "))
    quantidade_atual = confirma_float(input("Digite a quantidade atual de comprimidos: "))
    alerta = confirma_float(input("Digite com quantos comprimidos você gostaria de ser alertado(a): "))
    observacao = input("Digite o responsavel: ")

    inserir_estoque(id_paciente, id_medicamento, dosagem_diaria, quantidade_atual, alerta, observacao)
    print("\n\n\nNova prescrição cadastrada com sucesso!")
    time.sleep(2)
    limpa_tela()
