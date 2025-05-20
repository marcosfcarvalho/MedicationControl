import sqlite3
import os
import datetime

DB_PATH = r"D:\programas em python\controle_medicamentos.db"


def conectar_banco():
    conn = sqlite3.connect(DB_PATH)
    return conn

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
            dosagem_diaria INTEGER not null default 1,
            miligrama REAL not null CHECK(miligrama >= 0),
            quantidade_atual INT NOT NULL CHECK(quantidade_atual >= 0),
            alerta INT NOT NULL CHECK(alerta >= 0),
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

def consultar_pacientes():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
     SELECT id_paciente, nome, observacao FROM paciente WHERE stts = 1
     ''')
    pacientes = cursor.fetchall()
    print("Pacientes cadastrados:\n\n")
    for paciente in pacientes:
        print(f"{paciente[0]}- {paciente[1]}, Observação: {paciente[2]}")
    conn.close()

def consultar_pacientes_inativos():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
     SELECT id_paciente, nome, observacao FROM paciente WHERE stts = 0
     ''')
    pacientes = cursor.fetchall()
    print("Pacientes cadastrados:\n\n")
    for paciente in pacientes:
        print(f"{paciente[1]}, Observação: {paciente[2]}")
    conn.close()

def consultar_medicamntos():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM medicamento
    ''')
    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        print("Nenhum medicamento cadastrado.")
        return

    print("\nLista de medicamentos cadastrados:")
    print("-" * 40)

    for id_medicamento, nome, descricao in resultados:
        print(f"{id_medicamento}- {nome}       |Descrição: {descricao}")
        print("-" * 80)

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
        SELECT id_medicamento, nome FROM medicamento WHERE nome COLLATE NOCASE LIKE ?
    ''', ('%' + nome_medicamento + '%',))

    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        print("Nenhum medicamento encontrado.")
        opcao = input("Deseja cadastrar um novo medicamento? (s/n): ").strip().lower()
        if opcao == 's':
            nome = input("Digite o nome do novo medicamento: ")
            descricao = input("Digite uma descrição: ")
            inserir_medicamento(nome, descricao)
            return buscar_medicamento_por_nome(nome)  # Busca novamente após cadastrar
        else:
            return None

    print("\nMedicamentos encontrados:")
    for i, (id_medicamento, nome) in enumerate(resultados, 1):
        print(f"{i}. {nome})")

    while True:
        try:
            escolha = int(input("\nDigite o número correspondente ao medicamento desejado: "))
            if 1 <= escolha <= len(resultados):
                return resultados[escolha - 1][0]  # Retorna o ID do medicamento escolhido
            else:
                print("Opção inválida, tente novamente.")
        except ValueError:
            print("Entrada inválida, digite um número.")

def buscar_paciente_por_nome_ativos(nome_paciente):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id_paciente, nome FROM paciente WHERE nome COLLATE NOCASE LIKE ? AND stts = 1;
    ''', ('%' + nome_paciente + '%',))

    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        print("Nenhum paciente encontrado.")
        return None

    print("\nPacientes encontrados:")
    for i, (id_paciente, nome) in enumerate(resultados, 1):
        print(f"{i}. {nome}")

    while True:
        try:
            escolha = int(input("\nDigite o número correspondente ao paciente desejado: "))
            if 1 <= escolha <= len(resultados):
                return resultados[escolha - 1][0]  # Retorna o ID do paciente escolhido
            else:
                print("Opção inválida, tente novamente.")
        except ValueError:
            print("Entrada inválida, digite um número.")

def buscar_paciente_por_nome_inativos(nome_paciente):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id_paciente, nome FROM paciente WHERE nome COLLATE NOCASE LIKE ? AND stts = 0;
    ''', ('%' + nome_paciente + '%',))

    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        print("Nenhum paciente encontrado.")
        return None

    print("\nPacientes encontrados:")
    for i, (id_paciente, nome) in enumerate(resultados, 1):
        print(f"{i}. {nome}")

    while True:
        try:
            escolha = int(input("\nDigite o número correspondente ao paciente desejado: "))
            if 1 <= escolha <= len(resultados):
                return resultados[escolha - 1][0]  # Retorna o ID do paciente escolhido
            else:
                print("Opção inválida, tente novamente.")
        except ValueError:
            print("Entrada inválida, digite um número.")

def cadastrar_paciente_com_medicamentos():
    conn = conectar_banco()
    cursor = conn.cursor()

    try:
        conn.execute('BEGIN TRANSACTION')  # Inicia uma transação

        nome_p = input("Digite o nome do paciente: ")
        obs = input("Digite uma observação: ")
        cursor.execute('''
            INSERT INTO paciente (nome, observacao)
            VALUES (?, ?)
        ''', (nome_p, obs))
        id_paciente = cursor.lastrowid

        x = int(input("Quantos medicamentos o paciente faz uso? "))
        for i in range(x):
            print(f"Medicamento {i+1}:")
            nome = input("Digite o nome do medicamento: ")
            id_medicamento = buscar_medicamento_por_nome(nome)
            while id_medicamento is None:
                print("Medicamento não encontrado.")
                nome = input("Digite o nome do medicamento: ")
                id_medicamento = buscar_medicamento_por_nome(nome)

            dosagem_diaria = input("Digite a quantidade de comprimidos/dia: ")
            miligrama = float(input("Digite a dosagem em miligramas: "))
            quantidade_atual = int(input("Digite a quantidade atual: "))
            alerta = int(input("Digite com quantos comprimidos você gostaria de ser alertado: "))
            observacao = input("Digite uma observação: ")

            cursor.execute('''
                INSERT INTO estoque (id_paciente, id_medicamento, dosagem_diaria, miligrama, quantidade_atual, alerta, observacao)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (id_paciente, id_medicamento, dosagem_diaria, miligrama, quantidade_atual, alerta, observacao))

        conn.commit()  # Confirma tudo de uma vez

        print(f"Paciente {nome_p} e seus medicamentos foram cadastrados com sucesso!")

    except Exception as e:
        conn.rollback()  # Cancela tudo em caso de erro
        print(f"Erro ao cadastrar paciente e medicamentos: {e}")

    finally:
        conn.close()

def menu_caso2():
    print ("""
        1- Ajustar medicamento
        2- Reposição de estoque
        3- incluir medicamento
        4- Excluir Precrição
        5- Editar nome/obs do paciente
        6- voltar
        """)

def menuprincipal():
    print ("""
          1- Cadastrar novo paciente
          2- Ajustes
          3- consultar medicamentos/pacientes
          4- declarar alta/reativar prontuario
          5- cadastrar medicamento
          6- sair
          """)

def todos_medicamento_paciente():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.nome, m.nome, e.dosagem_diaria, e.miligrama, e.quantidade_atual, e.alerta, e.observacao
        FROM paciente p
        JOIN estoque e ON p.id_paciente = e.id_paciente
        JOIN medicamento m ON e.id_medicamento = m.id_medicamento where p.stts = 1
    ''')
    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        print("Nenhum medicamento encontrado.")
        return

    print("\nLista de medicamentos cadastrados:")
    print("-" * 40)

    for nome_paciente, nome_medicamento, dosagem_diaria, miligrama, quantidade_atual, alerta, observacao in resultados:
        print(f"Paciente: {nome_paciente} | Medicamento: {nome_medicamento} | Dosagem Diária: {dosagem_diaria} | Miligrama: {miligrama} | Quantidade Atual: {quantidade_atual} | Alerta: {alerta} | Observação: {observacao}")
        print("-" * 80)

def consultar_medicamentos_por_paciente(id_paciente):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.nome AS paciente, 
               m.nome AS medicamento, 
               e.dosagem_diaria, 
               e.miligrama, 
               e.quantidade_atual, 
               e.alerta, 
               e.observacao
        FROM paciente p
        JOIN estoque e ON p.id_paciente = e.id_paciente
        JOIN medicamento m ON e.id_medicamento = m.id_medicamento
        WHERE p.id_paciente = ?;
    ''', (id_paciente,))
    
    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        print("Nenhum medicamento encontrado para esse paciente.")
        return
    
    print(f"\nMedicamentos do paciente {resultados[0][0]}:")
    print("-" * 40)
    for registro in resultados:
        print(f"Medicamento: {registro[1]}, Dosagem: {registro[2]}x {registro[3]} mg")
        print(f"Quantidade atual: {registro[4]}, Alerta: {registro[5]} comprimidos restantes")
        print(f"Observação: {registro[6]}")
        print("-" * 40)

def obter_id_precrisao(id_paciente, id_medicamento):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id_estoque FROM estoque WHERE id_paciente = ? AND id_medicamento = ?
    ''', (id_paciente, id_medicamento))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        return resultado[0]
    else:
        print("Nenhuma prescrição encontrada.")
        return None

def selecionar_medicamento_por_paciente(id_paciente):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Buscar os medicamentos vinculados ao paciente
    cursor.execute('''
        SELECT e.id_estoque, m.nome
        FROM estoque e
        JOIN medicamento m ON e.id_medicamento = m.id_medicamento
        WHERE e.id_paciente = ?
    ''', (id_paciente,))
    
    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        print("Esse paciente não tem medicamentos cadastrados.")
        return None
    
    # Exibir os medicamentos disponíveis
    print("\nMedicamentos do paciente:")
    for i, (id_estoque, nome_medicamento) in enumerate(resultados, 1):
        print(f"{i}. {nome_medicamento}")

    while True:
        try:
            escolha = int(input("\nDigite o número correspondente ao medicamento desejado: "))
            if 1 <= escolha <= len(resultados):
                return resultados[escolha - 1][0]  # Retorna o ID do estoque selecionado
            else:
                print("Opção inválida, tente novamente.")
        except ValueError:
            print("Entrada inválida, digite um número.")

def cadastrar_nova_prescricao(id_paciente):
    conn = conectar_banco()
    cursor = conn.cursor()

    nome_medicamento = input("Digite o nome do medicamento: ")
    id_medicamento = buscar_medicamento_por_nome(nome_medicamento)
    if id_medicamento is None:
        print("Medicamento não encontrado.")
        return
    # Verifica se o medicamento já está cadastrado para o paciente
    id_estoque = obter_id_precrisao(id_paciente, id_medicamento)
    if id_estoque is not None:
        print("Esse medicamento já está cadastrado para esse paciente.")
        return

    dosagem_diaria = input("Digite a quantidade de comprimidos/dia o paciente toma: ")
    miligrama = float(input("Digite a dosagem em miligramas: "))
    quantidade_atual = int(input("Digite a quantidade atual de comprimidos: "))
    alerta = int(input("Digite com quantos comprimidos você gostaria de ser alertado(a): "))
    observacao = input("Digite uma observação: ")

    inserir_estoque(id_paciente, id_medicamento, dosagem_diaria, miligrama, quantidade_atual, alerta, observacao)
    print("Nova prescrição cadastrada com sucesso!")

criar_tabela()

while True:
    menuprincipal()
    opcao = int(input("Escolha uma opção: "))

    match opcao:
        case 1:
            cadastrar_paciente_com_medicamentos()

        case 2:
            nome_paciente = input("Digite o nome do paciente: ")
            id_paciente = buscar_paciente_por_nome_ativos(nome_paciente)
            if id_paciente is None:
                print("Paciente não encontrado.")
                break

            menu_caso2()
            opcao_ajuste = int(input("Escolha uma opção: "))

            match opcao_ajuste:
                case 1:
                    print(f"Medicamentos do paciente {nome_paciente}:")
                    id_estoque = selecionar_medicamento_por_paciente(id_paciente)
                    if id_estoque is None:
                        print("Nenhum medicamento encontrado para esse paciente.")
                        break

                    dosagem_diaria = input("Digite a nova quantidade de comprimidos/dia: ")
                    miligrama = float(input("Digite a nova dosagem em miligramas: "))
                    quantidade_atual = int(input("Digite a nova quantidade atual: "))
                    alerta = int(input("Digite com quantos comprimidos você gostaria de ser alertado: "))
                    observacao = input("Digite uma nova observação: ")

                    conn = conectar_banco()
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE estoque SET dosagem_diaria = ?, miligrama = ?, quantidade_atual = ?, alerta = ?, observacao = ?
                        WHERE id_estoque = ?
                    ''', (dosagem_diaria, miligrama, quantidade_atual, alerta, observacao, id_estoque))
                    conn.commit()
                    conn.close()
                    print("Medicamento ajustado com sucesso!")

                case 2:
                    print(f"Medicamentos do paciente {nome_paciente}:")
                    id_estoque = selecionar_medicamento_por_paciente(id_paciente)
                    if id_estoque is None:
                        print("Nenhum medicamento encontrado para esse paciente.")
                        break
 
                    reposicao_estoque = int(input("Digite a quantidade de comprimidos de reposição: "))
                    
                    conn = conectar_banco()
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE estoque SET quantidade_atual = quantidade_atual + ?
                        WHERE id_estoque = ?
                    ''', (reposicao_estoque, id_estoque))
                    conn.commit()
                    conn.close()
                    print("Reposição de estoque realizada com sucesso!")

                case 3:
                    cadastrar_nova_prescricao(id_paciente)

                case 4:
                    print(f"Medicamentos do paciente {nome_paciente}:")
                    id_estoque = selecionar_medicamento_por_paciente(id_paciente)
                    if id_estoque is None:
                        print("Medicamento não encontrado.")
                        break
                    opcao_certificar = int(input("\nVocê tem certeza que deseja excluir essa prescrição? (1-sim/2-não)"))
                    if opcao_certificar == 1:
                        print("Excluindo prescrição...")
                        conn = conectar_banco()
                        cursor = conn.cursor()
                        cursor.execute('''
                            DELETE FROM estoque WHERE id_estoque = ?
                        ''', (id_estoque,))
                        conn.commit()
                        conn.close()
                        print("Prescrição excluída com sucesso!")
                    else:
                        print("Exclusão cancelada.")
                        break

                case 5: 
                    novo_nome = input("Digite o novo nome do paciente: ")
                    nova_observacao = input("Digite a nova observação: ")

                    conn = conectar_banco()
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE paciente SET nome = ?, observacao = ?
                        WHERE id_paciente = ?
                    ''', (novo_nome, nova_observacao, id_paciente))
                    conn.commit()
                    conn.close()
                    print("Nome e observação do paciente atualizados com sucesso!")
                    
                case 6:
                    print("Voltando ao menu principal...")
                    break

        case 3:

            print("1- Consultar medicamentos")
            print("2- Consultar pacientes")
            opcao_consulta = int(input("Escolha uma opção: "))
            if opcao_consulta == 1:
                consultar_medicamntos()


            elif opcao_consulta == 2:
                todos_medicamento_paciente()

            else:
                print("Opção inválida!")


        case 4:
            opcao_alta = int(input("Digite 1 para dar alta ou 2 para reativar o prontuário: "))
            if opcao_alta == 1:
                nome_ativo = input("Digite o nome do paciente: ")
                id_paciente = buscar_paciente_por_nome_ativos(nome_ativo)
                if id_paciente is None:
                    print("Paciente não encontrado.")
                    break
                escolha = int(input("Você tem certeza que deseja dar alta? (1-sim/2-não)"))
                if escolha == 1:       
                    print("Dando alta ao paciente...")
                    conn = conectar_banco()
                    cursor = conn.cursor()
                    cursor.execute('''
                       UPDATE paciente SET stts = 0 WHERE id_paciente = ?
                    ''', (id_paciente,))
                    conn.commit()
                    conn.close()
                    print("Paciente teve alta.")
                else:
                    print("Alta cancelada.")
                    break

            elif opcao_alta == 2:
                print("pacientes inativos:")
                consultar_pacientes_inativos()
                nome_inativo = input("\nDigite o nome do paciente: ")
                id_paciente = buscar_paciente_por_nome_inativos(nome_inativo)
                if id_paciente is None:
                    print("Paciente não encontrado.")
                    break
                conn = conectar_banco()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE paciente SET stts = 1 WHERE id_paciente = ?
                ''', (id_paciente,))
                conn.commit()
                conn.close()
                print("Paciente Readimitido.")

        case 5:
            nome = input("Digite o nome do medicamento: ")
            descricao = input("Digite uma descrição: ")
            inserir_medicamento(nome, descricao)

        
        case 6:
            print("Saindo do sistema...")
            exit()
            break
        case _:
            print("Opção inválida!")
