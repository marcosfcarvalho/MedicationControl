import datetime
import time
from datetime import datetime
from confirm_number import confirma_int, confirma_float
from auto_backups import executar_backup_pelo_python
from script_db import conectar_banco, criar_tabela
from data_time import atualizar_estoque_com_dias, salvar_data_execucao, atualiza_receita
from clear import limpa_tela
from inserts import inserir_medicamento, cadastrar_paciente_com_medicamentos, cadastrar_nova_prescricao
from menus import menu_caso2, menuprincipal, menu_caso3
from searches import (buscar_paciente_por_nome_ativos, buscar_paciente_por_nome_inativos, nome_paciente_pelo_id,
selecionar_medicamento_por_paciente, consultar_medicamentos_por_paciente, buscar_medicamento_por_id, consultar_medicamntos,
consultar_pacientes, consultar_medicamentos_proximos_de_acabar,buscar_medicamento_por_nome, consultar_pacientes_inativos)
import sys
import getpass

# Redireciona erros para um arquivo de log
sys.stderr = open("erro_log.txt", "w")

criar_tabela()

def main():

    senha = "" #coloque aqui a sua senha, caso queira, esta parte ainda esta em desenvolvimento de aprimoramento.
    senha_digitada = getpass.getpass("\n\n        Digite sua senha de acesso : ")
    limpa_tela()
    while senha_digitada != senha:
        print(" Senha incorreta. Tente novamente.")
        senha_digitada = getpass.getpass("\n\n        Digite sua senha de acesso : ")
        limpa_tela()

    opcao_consulta = 0  # Variável declarada globalmente para ser usada na função buscar_medicamento_por_nome
    
    # Início do programa

    data_atual = datetime.now()
    print(f""" 
        Para que o sistema funcione corretamente, é necessário que a data do computador esteja correta.
        Caso contrario, vocé irá perder o controle de estoque.
        O sistema esta marcando que hoje é: {data_atual.strftime("%d/%m/%Y")}
    """) #fui obrigado a deixar a verificação de data a encargo do usuario, pois nem sempre o local onde minha usuaria está tem acesso a internet para verificar a data correta.
    opcao = confirma_int(input("     Está correta? (1-sim/0-não):"))
    if opcao == 1:
        print("\n\n     Sistema iniciado...")
        executar_backup_pelo_python()
        limpa_tela()
    else:
        limpa_tela()
        print("\n\n     Por favor, ajuste a data do computador e reinicie o sistema.")
        time.sleep(3)
        exit()

    while True:
        atualizar_estoque_com_dias()
        salvar_data_execucao()
        atualiza_receita()
        menuprincipal()
        opcao = confirma_int(input("         Escolha uma opção: "))
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
                    opcao_ajuste = confirma_int(input("      Escolha uma opção: "))
                    limpa_tela()

                    match opcao_ajuste:
                        case 1:
                            print(f"Medicamentos do paciente {nome_pac}:")
                            id_estoque = selecionar_medicamento_por_paciente(id_paciente)
                            if id_estoque is None:
                                print("Nenhum medicamento encontrado para esse paciente.")
                                continue

                            dosagem_diaria = confirma_float(input("    Digite a nova quantidade de comprimidos/dia: "))
                            quantidade_atual = confirma_float(input("  Digite a nova quantidade atual: "))
                            alerta = confirma_float(input("    Digite com quantos comprimidos você gostaria de ser alertado: "))
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
                                time.sleep(2)
                                limpa_tela()
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
    
                            reposicao_estoque = confirma_int(input("Digite a quantidade de comprimidos de reposição: "))

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
                            opcao_certificar = confirma_int(input("\nVocê tem certeza que deseja excluir essa prescrição? (1-sim/2-não)"))
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
                            
                        
                        case 0:
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
                    menu_caso3()
                    opcao_consulta = confirma_int(input("        Escolha uma opção: "))
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
                            WHERE e.id_paciente IS NULL AND p.stts = 1;
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
                        receitas_test = confirma_int(input("1 - receitas por fazer\n" \
                        "2 - receitas feitas\n"\
                        "\nDigite a opção desejada: "
                        ))
                        limpa_tela()
                        if receitas_test == 1:
                            lista_pacientes, lista_medicamentos = consultar_medicamentos_proximos_de_acabar()
                            z = confirma_int(input("\n\n Deseja declarar receitas como 'feitas'? (1-sim/2-não): "))
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
                                    s = confirma_int(input(f'\n\nA receita de {c} do {m} foi feita? (1-sim/2-não)'))
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
                    elif opcao_consulta == 0:
                        print("\n\nVoltando ao menu principal...")
                        time.sleep(1)
                        limpa_tela()
                        break
                    else:
                        print("Opção inválida!")


            case 4:
                opcao_alta = confirma_int(input("\n\nDigite 1 para dar alta" \
                " 2 para reativar o prontuário: "))
                if opcao_alta == 1:
                    nome_ativo = input("Digite o nome do paciente: ")
                    id_paciente = buscar_paciente_por_nome_ativos(nome_ativo)
                    if id_paciente is None:
                        print("Paciente não encontrado.")
                        break
                    escolha = confirma_int(input("Você tem certeza que deseja dar alta? (1-sim/2-não)"))
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
                
                print("Voltando ao menu principal...")
                time.sleep(1.5)
                limpa_tela()
            
            case 0:
                print("Saindo do sistema...")
                executar_backup_pelo_python()
                sys.exit()
                break
            case _:
                print("\n\n\n       Opção inválida!")
                time.sleep(1.5)
                limpa_tela()
                continue

if __name__ == "__main__":
    main()
