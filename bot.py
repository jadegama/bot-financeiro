import os
import unicodedata
from datetime import datetime
import asyncio
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from database import salvar_transacao, relatorio_por_pessoa, criar_banco, relatorio_por_mes

# --- Configurações ---
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # ex: https://SEU_APP.onrender.com/webhook
PORT = int(os.environ.get("PORT", 10000))

# --- Funções utilitárias ---
def normalizar_texto(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto

meses = {
    "janeiro": "01", "fevereiro": "02", "marco": "03",
    "abril": "04", "maio": "05", "junho": "06",
    "julho": "07", "agosto": "08", "setembro": "09",
    "outubro": "10", "novembro": "11", "dezembro": "12"
}

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Oi, sou JAI 🤖! Me manda um gasto que eu salvo 😄")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = normalizar_texto(update.message.text)

    try:
        # Menu de relatórios
        if "relatorio" in texto:
            teclado = [["Geral", "Mensal"]]
            reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)
            await update.message.reply_text("Escolha o tipo de relatório:", reply_markup=reply_markup)
            return

        # Relatório geral
        if texto == "geral":
            await update.message.reply_text(relatorio_por_pessoa())
            return

        # Relatório mensal
        if texto == "mensal":
            teclado = [
                ["Janeiro","Fevereiro","Março"],
                ["Abril","Maio","Junho"],
                ["Julho","Agosto","Setembro"],
                ["Outubro","Novembro","Dezembro"]
            ]
            reply_markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True)
            await update.message.reply_text("Escolha o mês:", reply_markup=reply_markup)
            return

        # Relatório de mês específico
        if texto in meses:
            ano = datetime.now().year
            await update.message.reply_text(relatorio_por_mes(ano, meses[texto]))
            return

        # Salvar gasto
        partes = texto.split("-")
        valor = float(partes[0].strip().replace(",", "."))
        local = partes[1].strip()
        pessoa = partes[2].strip()
        salvar_transacao(pessoa, valor, local)
        await update.message.reply_text("✅ Gasto salvo com sucesso!")

    except Exception as e:
        print("ERRO NO HANDLER:", e)
        await update.message.reply_text("❌ Formato inválido.\nUse: 50 - almoço - João")

# --- Criar banco ---
criar_banco()

# --- Criar aplicação Telegram ---
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

# --- Flask para webhook ---
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.get_event_loop().create_task(application.process_update(update))
        return "ok", 200
    except Exception as e:
        print("ERRO NO WEBHOOK:", e)
        return "erro interno", 500

@app.route("/", methods=["GET"])
def index():
    return "Bot Financeiro Online ✅", 200

# --- Rodar webhook ---
if __name__ == "__main__":
    print("Bot rodando com webhook...")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=WEBHOOK_URL,
    )
