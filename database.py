import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def criar_banco():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id SERIAL PRIMARY KEY,
            data DATE,
            hora TIME,
            pessoa TEXT,
            valor REAL,
            local TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def salvar_transacao(pessoa, valor, local):
    conn = conectar()
    cur = conn.cursor()
    agora = datetime.now()
    data = agora.date()
    hora = agora.time()
    cur.execute("""
        INSERT INTO transacoes (data, hora, pessoa, valor, local)
        VALUES (%s, %s, %s, %s, %s)
    """, (data, hora, pessoa, valor, local))
    conn.commit()
    cur.close()
    conn.close()

def relatorio_por_pessoa():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT pessoa, SUM(valor) as total
        FROM transacoes
        GROUP BY pessoa
    """)
    resultados = cur.fetchall()
    cur.close()
    conn.close()

    if not resultados:
        return "Nenhum gasto registrado ainda."

    resposta = "📊 Relatório de gastos:\n\n"
    for r in resultados:
        resposta += f"{r['pessoa']}: R${r['total']:.2f}\n"
    return resposta

def relatorio_mensal():
    conn = conectar()
    cur = conn.cursor()
    mes_atual = datetime.now().strftime("%Y-%m")
    cur.execute("""
        SELECT pessoa, SUM(valor) as total
        FROM transacoes
        WHERE TO_CHAR(data, 'YYYY-MM') = %s
        GROUP BY pessoa
    """, (mes_atual,))
    resultados = cur.fetchall()
    cur.close()
    conn.close()

    if not resultados:
        return "Nenhum gasto registrado este mês."

    resposta = "📅 Relatório do mês:\n\n"
    for r in resultados:
        resposta += f"{r['pessoa']}: R${r['total']:.2f}\n"
    return resposta

def relatorio_por_mes(ano, mes):
    conn = conectar()
    cur = conn.cursor()
    filtro = f"{ano}-{mes:0>2}"
    cur.execute("""
        SELECT pessoa, SUM(valor) as total
        FROM transacoes
        WHERE TO_CHAR(data, 'YYYY-MM') = %s
        GROUP BY pessoa
    """, (filtro,))
    resultados = cur.fetchall()
    cur.close()
    conn.close()

    if not resultados:
        return "Nenhum gasto nesse mês."

    resposta = "📅 Relatório do mês:\n\n"
    for r in resultados:
        resposta += f"{r['pessoa']}: R${r['total']:.2f}\n"
    return resposta
