import sqlite3
from datetime import datetime

def criar_banco():
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            hora TEXT,
            pessoa TEXT,
            valor REAL,
            local TEXT
        )
    """)
    conn.commit()
    conn.close()
    
def salvar_transacao(pessoa, valor, local):
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()

    agora = datetime.now()

    cursor.execute("""
        INSERT INTO transacoes (data, hora, pessoa, valor, local)
        VALUES (?, ?, ?, ?, ?)
    """, (
        agora.strftime("%Y-%m-%d"),
        agora.strftime("%H:%M:%S"),
        pessoa,
        valor,
        local
    ))

    conn.commit()
    conn.close()

def relatorio_por_pessoa():
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT pessoa, SUM(valor)
        FROM transacoes
        GROUP BY pessoa
    """)

    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        return "Nenhum gasto registrado ainda."

    resposta = "📊 Relatório de gastos:\n\n"

    for pessoa, total in resultados:
        resposta += f"{pessoa}: R${total:.2f}\n"

    return resposta