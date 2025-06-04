import time
from script_db import conectar_banco
from clear import limpa_tela


def nome_paciente_pelo_id(id_paciente):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT nome FROM paciente WHERE id_paciente = ?
    ''', (id_paciente,))
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return resultado[0]
    else:
        return None

def consultar_pacientes():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
     SELECT p.nome AS paciente, 
               m.nome AS medicamento,  
               e.quantidade_atual
        FROM paciente p
        JOIN estoque e ON p.id_paciente = e.id_paciente
        JOIN medicamento m ON e.id_medicamento = m.id_medicamento 
        WHERE p.stts = 1;
     ''')
    
    pacientes = cursor.fetchall()
    conn.close()

    # Criar um dicionário para organizar os pacientes
    dados_pacientes = {}

    for registro in pacientes:
        nome_paciente = registro[0]
        nome_medicamento = registro[1]
        quantidade_atual = registro[2]
        
        if nome_paciente not in dados_pacientes:
            dados_pacientes[nome_paciente] = []  # Inicializa a lista de medicamentos para cada paciente

        dados_pacientes[nome_paciente].append((nome_medicamento, quantidade_atual))  # Adiciona medicamentos

    # Exibir os pacientes e seus respectivos medicamentos
    print("Pacientes cadastrados:\n\n")
    for paciente, medicamentos in dados_pacientes.items():
        print(f"# {paciente}")
        for med in medicamentos:
            print(f"  -{med[0]}, Quantidade atual: {med[1]}")
        print("-" * 80)

    if not pacientes:
        print("Nenhum paciente cadastrado.")

def consultar_pacientes_inativos():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
     SELECT id_paciente, nome, observacao FROM paciente WHERE stts = 0
     ''')
    pacientes = cursor.fetchall()
    print("Pacientes em alta:\n\n")
    for paciente in pacientes:
        print(f"{paciente[1]}, Observação: {paciente[2]}")
    conn.close()
    return pacientes

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

def buscar_medicamento_por_nome(nome_medicamento):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id_medicamento, nome FROM medicamento WHERE nome COLLATE NOCASE LIKE ?
    ''', ('%' + nome_medicamento + '%',))

    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        print("     Nenhum medicamento encontrado.")
        time.sleep(1.5)
        limpa_tela()
        return None
        

    print("\n   Medicamentos encontrados:")
    for i, (id_medicamento, nome) in enumerate(resultados, 1):
        print(f"    {i}. {nome})")

    while True:
        try:
            escolha = int(input("\n     Digite o número correspondente ao medicamento desejado: "))
            limpa_tela()
            if 1 <= escolha <= len(resultados):
                return resultados[escolha - 1][0]  # Retorna o ID do medicamento escolhido
            else:
                print("     Opção inválida, tente novamente.")
                time.sleep(1.5)
                limpa_tela()
        except ValueError:
            print("     Entrada inválida, digite um número.")
            time.sleep(1.5)
            limpa_tela()

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

def todos_medicamento_paciente():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.nome, m.nome, e.dosagem_diaria, e.quantidade_atual, e.alerta, e.observacao
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

    for nome_paciente, nome_medicamento, dosagem_diaria, quantidade_atual, alerta, observacao in resultados:
        print(f"Paciente: {nome_paciente} | Medicamento: {nome_medicamento} | Dosagem Diária: {dosagem_diaria} | Quantidade Atual: {quantidade_atual} | Alerta: {alerta} | Responsavel: {observacao}")
        print("-" * 80)

def consultar_medicamentos_por_paciente(id_paciente):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.nome AS paciente, 
               m.nome AS medicamento, 
               e.dosagem_diaria, 
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
        print(f"Medicamento: {registro[1]}, Dosagem: {registro[2]}x")
        print(f"Quantidade atual: {registro[3]}, Alerta: {registro[4]} ")
        print(f"Responsavel: {registro[5]}")
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
        time.sleep(1.5)
        limpa_tela()
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
            limpa_tela()
            # Verifica se a escolha está dentro do intervalo válido
            if 1 <= escolha <= len(resultados):
                return resultados[escolha - 1][0]  # Retorna o ID do estoque selecionado
            else:
                print("Opção inválida, tente novamente.")
        except ValueError:
            print("Entrada inválida, digite um número.")

def consultar_medicamentos_proximos_de_acabar():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id_paciente, e.id_medicamento, p.nome, m.nome, e.observacao, e.receita
        FROM paciente p
        JOIN estoque e ON p.id_paciente = e.id_paciente
        JOIN medicamento m ON e.id_medicamento = m.id_medicamento
        WHERE p.stts = 1 AND (e.quantidade_atual <= e.alerta) and e.receita = 'por fazer'
    ''')
    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        print("Nenhum medicamento próximo de acabar.")
        return [], []  # retorna listas vazias para evitar erros
    else:
        print("\nMedicamentos próximos de acabar:")
        id_pacientes = []
        id_medicamentos = []
        for id_paciente, id_medicamento, nome_paciente, nome_medicamento, observacao, receita in resultados:
            print(f"{nome_paciente} | Medicamento: {nome_medicamento} | Responsavel: {observacao} | Receita: {receita}")
            print("-" * 80)
            id_pacientes.append(id_paciente)
            id_medicamentos.append(id_medicamento)

        return id_pacientes, id_medicamentos

def buscar_medicamento_por_id(id_medicamento):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT nome FROM medicamento WHERE id_medicamento = ?
    ''', (id_medicamento,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        return resultado[0]
    else:
        print("Medicamento não encontrado.")
        return None
