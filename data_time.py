import time
import sqlite3
from datetime import datetime
from script_db import conectar_banco

def salvar_data_execucao():
    conn = conectar_banco()
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
    conn = conectar_banco()
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
        conn = conectar_banco()
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