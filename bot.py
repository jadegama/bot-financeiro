from telegram import Update
import os
from database import salvar_transacao, relatorio_por_pessoa
from database import criar_banco
import unicodedata
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = os.getenv("TOKEN")

def normalizar_texto(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto

# Quando o usuário digitar /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fala! Me manda um gasto que eu salvo 😄")
# Quando o usuário mandar qualquer mensagem
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = normalizar_texto(update.message.text)
    # Se pedir relatório
    if "relatorio" in texto:
        resposta = relatorio_por_pessoa()
        await update.message.reply_text(resposta)
        return
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
