from telegram import Update, ReplyKeyboardMarkup
import os
import unicodedata
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from database import salvar_transacao, relatorio_por_pessoa, criar_banco, relatorio_por_mes

TOKEN = os.getenv("TOKEN")

def normalizar_texto(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto

# Meses
meses = {
    "janeiro": "01",
    "fevereiro": "02",
    "marco": "03",
    "abril": "04",
    "maio": "05",
    "junho": "06",
    "julho": "07",
    "agosto": "08",
    "setembro": "09",
    "outubro": "10",
    "novembro": "11",
    "dezembro": "12"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fala! Me manda um gasto que eu salvo 😄")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = normalizar_texto(update.message.text)

    # Menu principal
    if "relatorio" in texto:
        teclado = [["Geral", "Mensal"]]
        reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)

        await update.message.reply_text(
            "Escolha o tipo de relatório:",
            reply_markup=reply_markup
        )
        return

    # Relatório geral
    if texto == "geral":
        resposta = relatorio_por_pessoa()
        await update.message.reply_text(resposta)
        return

    # Mostrar meses
    if texto == "mensal":
        teclado = [
            ["Janeiro", "Fevereiro", "Março"],
            ["Abril", "Maio", "Junho"],
            ["Julho", "Agosto", "Setembro"],
            ["Outubro", "Novembro", "Dezembro"]
        ]
        reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)

        await update.message.reply_text(
            "Escolha o mês:",
            reply_markup=reply_markup
        )
        return

    # Seleção de mês
    if texto in meses:
        ano_atual = datetime.now().year
        mes_numero = meses[texto]

        resposta = relatorio_por_mes(ano_atual, mes_numero)
        await update.message.reply_text(resposta)
        return

    # Salvar gasto
    try:
        partes = texto.split("-")

        valor = float(partes[0].strip())
        local = partes[1].strip()
        pessoa = partes[2].strip()

        salvar_transacao(pessoa, valor, local)

        await update.message.reply_text("✅ Gasto salvo com sucesso!")

    except Exception as e:
        print(e)
        await update.message.reply_text(
            "❌ Formato inválido.\nUse: 50 - almoço - João"
        )

# Servidor fake para Render
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

criar_banco()

print("Bot rodando...")

app.run_polling()
