# ===============================
# bot_main.py
# ===============================

import asyncio
from telegram import Update
from telegram.ext import (
    Application, CommandHandler,
    ContextTypes, MessageHandler, filters
)

import bot_core as core

# ---------- CONFIG ----------
TOKENS = [
    "8524877041:AAEiBD7SBIHx17nC5v825dPtHFtoLrsNKj8"
]

OWNER_ID = 8312119030

core.load_state()

# ---------- DECORATOR ----------
def only_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != OWNER_ID:
            return
        return await func(update, context)
    return wrapper

async def reply(update):
    await update.message.reply_text(core.animated_text(0))

# ---------- BASIC ----------
@only_owner
async def start(update, ctx): await reply(update)

@only_owner
async def help_cmd(update, ctx): await reply(update)

@only_owner
async def ping(update, ctx): await reply(update)

@only_owner
async def myid(update, ctx): await reply(update)

@only_owner
async def status(update, ctx): await reply(update)

@only_owner
async def delay_cmd(update, ctx):
    if ctx.args:
        try:
            core.delay = float(ctx.args[0])
            core.save_state()
        except:
            pass
    await reply(update)

# ---------- GROUP NAME ----------
@only_owner
async def ncloop(update, ctx):
    if not ctx.args:
        return await reply(update)
    base_word = " ".join(ctx.args)
    core.start_ncloop(ctx.bot, update.message.chat_id, base_word)
    await reply(update)

@only_owner
async def stopgcnc(update, ctx):
    core.stop_ncloop(update.message.chat_id)
    await reply(update)

@only_owner
async def stopall(update, ctx):
    core.stop_ncloop(update.message.chat_id)
    await reply(update)

# ---------- SWIPE ----------
@only_owner
async def swipe(update, ctx):
    if not update.message.reply_to_message:
        return
    uid = str(update.message.reply_to_message.from_user.id)
    word = " ".join(ctx.args) if ctx.args else ""
    core.add_slide(uid, word)
    await reply(update)

@only_owner
async def stopswipe(update, ctx):
    if not update.message.reply_to_message:
        return
    uid = str(update.message.reply_to_message.from_user.id)
    core.remove_slide(uid)
    await reply(update)

# ---------- VOICE ----------
@only_owner
async def voiceon(update, ctx):
    core.voice_on()
    await reply(update)

@only_owner
async def voiceoff(update, ctx):
    core.voice_off()
    await reply(update)

# ---------- BUILD ----------
def build_app(token):
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("delay", delay_cmd))
    app.add_handler(CommandHandler("status", status))

    app.add_handler(CommandHandler("ncloop", ncloop))
    app.add_handler(CommandHandler("stopgcnc", stopgcnc))
    app.add_handler(CommandHandler("stopall", stopall))

    app.add_handler(CommandHandler("swipe", swipe))
    app.add_handler(CommandHandler("stopswipe", stopswipe))

    app.add_handler(CommandHandler("voiceon", voiceon))
    app.add_handler(CommandHandler("voiceoff", voiceoff))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, core.auto_reply))
    return app

# ---------- RUN ----------
async def run():
    for token in TOKENS:
        app = build_app(token)
        await app.initialize()
        await app.start()
        await app.updater.start_polling()

    print("BOT STARTED | lofi papa")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(run())
