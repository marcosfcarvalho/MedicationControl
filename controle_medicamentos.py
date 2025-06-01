import sqlite3
import os
import datetime
import time
from datetime import datetime

DB_PATH = r"C:\Users\clara\OneDrive\Documentos\Marcos Andre\Programas Python\controle_medicamentos.db"


def conectar_banco():
    conn = sqlite3.connect(DB_PATH)
    return conn

conectar_banco()

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

def limpa_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


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


def salvar_data_execucao():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Obtém a data atual do sistema
    data_atual = datetime.now().strftime("%Y-%m-%d")

    # Verifica se já existe um registro
    cursor.execute("SELECT COUNT(*) FROM configuracao")
    existe = cursor.fetchone()[0]

    if existe > 0:
        # Atualiza a data, pois já há um registro na tabela
        cursor.execute("UPDATE configuracao SET ultima_execucao = ?", (data_atual,))
    else:
        # Insere um novo registro, caso seja a primeira vez que o sistema está rodando
        cursor.execute("INSERT INTO configuracao (ultima_execucao) VALUES (?)", (data_atual,))

    conn.commit()
    conn.close()

def calcular_dias_passados():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT ultima_execucao FROM configuracao")
    resultado = cursor.fetchone()
    
    conn.close()

    if resultado:
        ultima_data = datetime.strptime(resultado[0], "%Y-%m-%d")
        hoje = datetime.now()
        dias_passados = (hoje - ultima_data).days
        return dias_passados
    else:
        return 0  # Se não houver registro, assume que é o primeiro dia
    
def atualizar_estoque_com_dias():
    dias_passados = calcular_dias_passados()
    
    if dias_passados > 0:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE estoque
            SET quantidade_atual = CASE 
                WHEN quantidade_atual - (dosagem_diaria * ?) < 0 THEN 0
                ELSE quantidade_atual - (dosagem_diaria * ?)
            END
            WHERE quantidade_atual > 0
        """, (dias_passados, dias_passados))

        conn.commit()
        conn.close()

    salvar_data_execucao()  # Atualiza a última data

def atualiza_receita():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id_estoque, quantidade_atual, alerta, receita
        FROM estoque
    ''')
    resultados = cursor.fetchall()
    conn.close()
    if not resultados:
        return

    for linha in resultados:
        id_estoque = linha[0]
        quantidade_atual = linha[1]
        alerta = linha[2]
        receita = linha[3]

        if quantidade_atual <= alerta and receita is None:
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE estoque SET receita = 'por fazer' WHERE id_estoque = ? and (quantidade_atual <= alerta)
            ''', (id_estoque,))
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

opcao_consulta = 0  # Variável declarada globalmente para ser usada na função buscar_medicamento_por_nome

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

        nome_p = input("    Digite o nome do paciente: ")
        obs = input("    Digite uma observação: ")
        cursor.execute('''
            INSERT INTO paciente (nome, observacao)
            VALUES (?, ?)
        ''', (nome_p, obs))
        id_paciente = cursor.lastrowid

        x = int(input("     Quantos medicamentos o paciente faz uso? Digite um número: "))
        limpa_tela()
        for i in range(x):
            print(f"\n  Medicamento {i+1}:")
            nome_m = input("\n    Digite o nome do medicamento: ")
            id_medicamento = buscar_medicamento_por_nome(nome_m)
            if id_medicamento is None:
                opcao = input("    Deseja cadastrar um novo medicamento? (s/n): ").strip().lower()
                limpa_tela()
                if opcao == 's':
                    nome_m = input("      Digite o nome do novo medicamento: ")
                    descricao = input("     Digite uma descrição: ")
                    limpa_tela()
                    inserir_medicamento(nome_m, descricao, conn, cursor)
                    id_medicamento = buscar_medicamento_por_nome(nome_m)
                    print(f"    Medicamento {id_medicamento}")
                    time.sleep(4)
                    

            dosagem_diaria = float(input("    Digite a quantidade de comprimidos/dia: "))
            quantidade_atual = float(input("      Digite a quantidade atual: "))
            alerta = float(input("    Digite com quantos comprimidos você gostaria de ser alertado: "))
            observacao = input("    Digite o Responsavel: ")
            limpa_tela()

            cursor.execute('''
                INSERT INTO estoque (id_paciente, id_medicamento, dosagem_diaria, quantidade_atual, alerta, observacao)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (id_paciente, id_medicamento, dosagem_diaria, quantidade_atual, alerta, observacao))

        conn.commit()  # Confirma tudo de uma vez

        print(f"\n    Paciente {nome_p} e seus medicamentos foram cadastrados com sucesso!")
        time.sleep(1.5)
        limpa_tela()

    except Exception as e:
        conn.rollback()  # Cancela tudo em caso de erro
        print(f"\n  Erro ao cadastrar paciente e medicamentos: {e}")

    finally:
        conn.close()


def menu_caso2():
    print ("""
    Menu de Ajustes:
           
        1- Ajustar medicamento
        2- Reposição de estoque
        3- incluir medicamento
        4- Excluir Precrição
        5- Editar nome/obs do paciente
        6- voltar
        """)

def menuprincipal():
    print ("""
    Menu Principal:
           
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
        print(f"Paciente: {nome_paciente} | Medicamento: {nome_medicamento} | Dosagem Diária: {dosagem_diaria} | Quantidade Atual: {quantidade_atual} | Alerta: {alerta} | Observação: {observacao}")
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

    dosagem_diaria = float(input("Digite a quantidade de comprimidos/dia o paciente toma: "))
    quantidade_atual = float(input("Digite a quantidade atual de comprimidos: "))
    alerta = float(input("Digite com quantos comprimidos você gostaria de ser alertado(a): "))
    observacao = input("Digite o responsavel: ")

    inserir_estoque(id_paciente, id_medicamento, dosagem_diaria, quantidade_atual, alerta, observacao)
    print("\n\n\nNova prescrição cadastrada com sucesso!")
    time.sleep(2)
    limpa_tela()

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


# Início do programa


criar_tabela()
data_atual = datetime.now()
print(f""" 
    Para que o sistema funcione corretamente, é necessário que a data do computador esteja correta.
    Caso contrario, vocé irá perder o controle de estoque.
    O sistema esta marcando que hoje é: {data_atual.strftime("%d/%m/%Y")}
""") #fui obrigado a deixar a verificação de data a encargo do usuario, pois nem sempre o local onde minha usuaria está tem acesso a internet para verificar a data correta.
opcao = int(input("     Está correta? (1-sim/2-não):"))
if opcao == 1:
    print("\n\n     Sistema iniciado...")
    limpa_tela()
else:
    print("Por favor, ajuste a data do computador e reinicie o sistema.")
    time.sleep(3)
    exit()

while True:
    atualizar_estoque_com_dias()
    salvar_data_execucao()
    atualiza_receita()
    menuprincipal()
    opcao = int(input("         Escolha uma opção: "))
    limpa_tela()

    match opcao:
        case 1:
            cadastrar_paciente_com_medicamentos()
        
        case 2:
            nome_paciente = input(" Digite o nome do paciente: ")
            id_paciente = buscar_paciente_por_nome_ativos(nome_paciente)
            limpa_tela()
            while id_paciente is None:
                print("Paciente não encontrado.")
                time.sleep(1.5)
                limpa_tela()
                nome_paciente = input(" Digite novamente o nome do paciente: ")
                id_paciente = buscar_paciente_por_nome_ativos(nome_paciente)
                limpa_tela()
            nome_pac = nome_paciente_pelo_id(id_paciente)

            while True:
                print("Paciente selecionado:", nome_pac)
                menu_caso2()
                opcao_ajuste = int(input("      Escolha uma opção: "))
                limpa_tela()

                match opcao_ajuste:
                    case 1:
                        print(f"Medicamentos do paciente {nome_paciente}:")
                        id_estoque = selecionar_medicamento_por_paciente(id_paciente)
                        if id_estoque is None:
                            print("Nenhum medicamento encontrado para esse paciente.")
                            continue

                        dosagem_diaria = input("    Digite a nova quantidade de comprimidos/dia: ")
                        quantidade_atual = int(input("  Digite a nova quantidade atual: "))
                        alerta = int(input("    Digite com quantos comprimidos você gostaria de ser alertado: "))
                        observacao = input("    Digite o Respondavel: ")
                        limpa_tela()

                        conn = conectar_banco()
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE estoque SET dosagem_diaria = ?, quantidade_atual = ?, alerta = ?, observacao = ?
                            WHERE id_estoque = ?
                        ''', (dosagem_diaria, quantidade_atual, alerta, observacao, id_estoque))
                        conn.commit()
                        conn.close()
                        print(" Medicamento ajustado com sucesso!")
                        time.sleep(2)
                        limpa_tela()
                    

                    case 2:
                        print(f"Medicamentos do paciente {nome_paciente}:")
                        id_estoque = selecionar_medicamento_por_paciente(id_paciente)
                        if id_estoque is None:
                            print("Nenhum medicamento encontrado para esse paciente.")
                            break
                        
                        limpa_tela()
                        print("Detalhes do medicamento:\n")
                        # Exibe os detalhes do medicamento selecionado
                        conn = conectar_banco()
                        cursor = conn.cursor()
                        cursor.execute('''
                              SELECT m.nome, e.quantidade_atual
                            FROM estoque e
                            JOIN medicamento m ON e.id_medicamento = m.id_medicamento
                            WHERE e.id_estoque = ?
                        ''', (id_estoque,))
                        resultado = cursor.fetchone()
                        conn.close()
                        print(f"{resultado[0]}, Quantidade atual: {resultado[1]}\n\n")
 
                        reposicao_estoque = int(input("Digite a quantidade de comprimidos de reposição: "))

                        conn = conectar_banco()
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE estoque SET quantidade_atual = quantidade_atual + ?
                            WHERE id_estoque = ?
                        ''', (reposicao_estoque, id_estoque))

                        cursor.execute('''
                            UPDATE estoque
                            SET receita = NULL
                            WHERE id_estoque = ? AND quantidade_atual > alerta
                            ''', (id_estoque,))
                        conn.commit()
                        conn.close()

                        print("\n\nReposição de estoque realizada com sucesso!")
                        time.sleep(2)
                        limpa_tela()
                        continue

                    case 3:
                        cadastrar_nova_prescricao(id_paciente)

                    case 4:
                        print(f"Medicamentos do paciente {nome_paciente}:")
                        id_estoque = selecionar_medicamento_por_paciente(id_paciente)
                        if id_estoque is None:
                            print("Medicamento não encontrado.")
                            time.sleep(2)
                            limpa_tela()
                            continue
                        opcao_certificar = int(input("\nVocê tem certeza que deseja excluir essa prescrição? (1-sim/2-não)"))
                        if opcao_certificar == 1:
                            print("\n\nExcluindo prescrição...")
                            conn = conectar_banco()
                            cursor = conn.cursor()
                            cursor.execute('''
                                DELETE FROM estoque WHERE id_estoque = ?
                            ''', (id_estoque,))
                            conn.commit()
                            conn.close()
                            print("\n\nPrescrição excluída com sucesso!")
                            time.sleep(2)
                            limpa_tela()
                        else:
                            print("\n\nExclusão cancelada.")
                            time.sleep(2)
                            limpa_tela()
                            continue

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
                        print("\n\nNome e observação do paciente atualizados com sucesso!")
                        time.sleep(2)
                        limpa_tela()
                    
                    case 6:
                        print("\n\nVoltando ao menu principal...")
                        time.sleep(1)
                        limpa_tela()
                        break
                    case _:
                        print("\n\nOpção inválida!")
                        time.sleep(1.5)
                        limpa_tela()
                        continue

        case 3:
            while True:
                print("""
    Menu de Consultas:
                  
        1- Consultar medicamentos
        2- Consultar pacientes
        3- Consultar medicamentos por paciente
        4- Consultar paciente com medicamentos proximos de acabar
        5- consultar pacientes por medicamentos
        6- voltar ao menu principal
                  """)
                opcao_consulta = int(input("        Escolha uma opção: "))
                limpa_tela()

                if opcao_consulta == 1:
                  consultar_medicamntos()
                  input("\n\nPressione Enter para continuar...")
                  limpa_tela()


                elif opcao_consulta == 2:
                    consultar_pacientes()
                    conn = conectar_banco()
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT p.nome AS paciente
                        FROM paciente p
                        LEFT JOIN estoque e ON p.id_paciente = e.id_paciente
                        WHERE e.id_paciente IS NULL;
                    ''')
                    pacientes_sem_medicamentos = cursor.fetchall()
                    conn.close()
                    if pacientes_sem_medicamentos:
                        print("\nPacientes sem medicamentos cadastrados:")
                        for paciente in pacientes_sem_medicamentos:
                            print(f"- {paciente[0]}")
                            
                    input("\n\nPressione Enter para continuar...")
                    limpa_tela()

                elif opcao_consulta == 3:
                    nome_paciente = input("Digite o nome do paciente: ")
                    id_paciente = buscar_paciente_por_nome_ativos(nome_paciente)
                    if id_paciente is None:
                        print("Paciente não encontrado.")
                        break
                    consultar_medicamentos_por_paciente(id_paciente)
                    input("\n\nPressione Enter para continuar...")
                    limpa_tela()

                elif opcao_consulta == 4:
                    receitas_test = int(input("1 - receitas por fazer\n" \
                    "2 - receitas feitas\n"\
                    "\nDigite a opção desejada: "
                    ))
                    limpa_tela()
                    if receitas_test == 1:
                        lista_pacientes, lista_medicamentos = consultar_medicamentos_proximos_de_acabar()
                        z = int(input("\n\n Deseja declarar receitas como 'feitas'? (1-sim/2-não): "))
                        if lista_pacientes is None and lista_medicamentos is None:
                            print("Nenhum medicamento próximo de acabar encontrado.")
                            time.sleep(2)
                            limpa_tela()
                            continue

                        if z == 1: 
                            for id_paciente, medicamento in zip(lista_pacientes, lista_medicamentos): 
                                c = nome_paciente_pelo_id(id_paciente)
                                m = buscar_medicamento_por_id(medicamento)
                                print(medicamento)
                                s = int(input(f'\n\nA receita de {c} do {m} foi feita? (1-sim/2-não)'))
                                if s == 1:
                                    conn = conectar_banco()
                                    cursor = conn.cursor()
                                    cursor.execute('''
                                        UPDATE estoque SET receita = 'feito' WHERE id_paciente = ? and id_medicamento = ?
                                    ''', (id_paciente, medicamento))
                                    conn.commit()
                                    conn.close()
                                    print("\n\nReceita feita.")
                                    time.sleep(1.5)
                                    limpa_tela()
                                else:
                                    print("\n\nReceita não feita.")
                                    time.sleep(1.5)
                                    limpa_tela()
                                    continue
                        else:
                            print("\n\nVoltando ao menu de consultas...")
                            time.sleep(1.5)
                            limpa_tela()
                            continue


                    elif receitas_test == 2:
                        conn = conectar_banco()
                        cursor = conn.cursor()
                        cursor.execute('''
                            SELECT p.nome, m.nome, e.observacao, e.receita
                            FROM paciente p
                            JOIN estoque e ON p.id_paciente = e.id_paciente
                            JOIN medicamento m ON e.id_medicamento = m.id_medicamento
                            WHERE p.stts = 1 AND (e.quantidade_atual <= e.alerta) and e.receita = 'feito'
                        ''')
                        resultados = cursor.fetchall()
                        conn.close()
                        if not resultados:
                            print("\nNenhum medicamento com receita feita encontrado.")
                            time.sleep(2)
                            limpa_tela()
                        for nome_paciente, nome_medicamento, observacao, receita in resultados:
                            print(f"{nome_paciente} | Medicamento: {nome_medicamento} | Responsavel: {observacao} | Receita: {receita}")
                            print("-" * 80)
                            input("\n\nPressione Enter para continuar...")
                            limpa_tela()
                    else:
                        print("\n\nOpção inválida!")
                        time.sleep(1.5)
                        limpa_tela()
                        continue
                        

                elif opcao_consulta == 5:
                    nome_medicamento = input("Digite o nome do medicamento: ")
                    id_medicamento = buscar_medicamento_por_nome(nome_medicamento)
                    if id_medicamento is None:
                        print("Medicamento não encontrado.")
                        time.sleep(2)
                        limpa_tela()
                        continue
                    conn = conectar_banco()
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT p.nome, m.nome, e.quantidade_atual, e.observacao from estoque as e 
                        JOIN 
                        medicamento as m on m.id_medicamento = e.id_medicamento
                        JOIN 
                        paciente as p on p.id_paciente = e.id_paciente WHERE m.id_medicamento = ? AND p.stts = 1;
                    ''', (id_medicamento,))
                    resultados = cursor.fetchall()
                    conn.close()

                    if not resultados:
                        print("Nenhum paciente encontrado com esse medicamento.")
                        time.sleep(2)
                        limpa_tela()
                        continue

                    print("\nPacientes que usam esse medicamento:\n")
                    for nome_paciente, nome_medicamento, quantidade_atual, observacao in resultados:
                        print(f"{nome_paciente}, {nome_medicamento}, {quantidade_atual} Responsavel: {observacao}")
                        print("-" * 80)
                    
                    input("\n\nPressione Enter para continuar...")
                    limpa_tela()
                elif opcao_consulta == 6:
                    print("\n\nVoltando ao menu principal...")
                    time.sleep(1)
                    limpa_tela()
                    break
                else:
                    print("Opção inválida!")


        case 4:
            opcao_alta = int(input("\n\nDigite 1 para dar alta" \
            " 2 para reativar o prontuário: "))
            if opcao_alta == 1:
                nome_ativo = input("Digite o nome do paciente: ")
                id_paciente = buscar_paciente_por_nome_ativos(nome_ativo)
                if id_paciente is None:
                    print("Paciente não encontrado.")
                    break
                escolha = int(input("Você tem certeza que deseja dar alta? (1-sim/2-não)"))
                if escolha == 1:       
                    print("\nDando alta ao paciente...")
                    conn = conectar_banco()
                    cursor = conn.cursor()
                    cursor.execute('''
                       UPDATE paciente SET stts = 0 WHERE id_paciente = ?
                    ''', (id_paciente,))
                    conn.commit()
                    conn.close()
                    print("\nPaciente teve alta.")
                    time.sleep(2)
                    limpa_tela()
                else:
                    print("Alta cancelada.")
                    break

            elif opcao_alta == 2:
                paciente_inativos= consultar_pacientes_inativos()
                if paciente_inativos is None:
                    print("Nenhum paciente inativo encontrado.")
                    time.sleep(2)
                    limpa_tela()
                    continue
                nome_inativo = input("\nDigite o nome do paciente: ")
                limpa_tela()
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
                print("\nPaciente Readimitido.")
                time.sleep(2)
                limpa_tela()

        case 5:
            nome = input("  Digite o nome do medicamento: ")
            descricao = input("   Digite uma descrição: ")
            inserir_medicamento(nome, descricao)
            print("\n\nMedicamento cadastrado com sucesso!")
            time.sleep(3)
            limpa_tela()
        
        case 6:
            print("Saindo do sistema...")
            exit()
            break
        case _:
            print("\n\n\n       Opção inválida!")
            time.sleep(1.5)
            limpa_tela()
            continue
