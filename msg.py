# ===============================
# bot_core.py
# ===============================

import asyncio
import os
import json
import time
import tempfile
from gtts import gTTS

# ---------- CONSTANTS ----------
DEFAULT_TEXT = "lofi papa"

EMOJIS = [
    "💖","✨","🔥","🌸","🌼","🌈","🦋","🌙","⭐","🎶",
    "💫","🌺","🌹","💐","🌻","🍃","🕊️","💎","🎧","🎵",
    "🧿","🥀","🌟","🌷"
]

STATE_FILE = "state.json"

# ---------- SPEED ----------
delay = 0.08

# ---------- STATE ----------
text_slide_targets = {}    # uid -> word
voice_slide_targets = {}   # uid -> word
voice_loop_enabled = False
group_name_tasks = {}

# ---------- STATE SAVE / LOAD ----------
def save_state():
    data = {
        "text_slide_targets": text_slide_targets,
        "voice_slide_targets": voice_slide_targets,
        "voice_loop_enabled": voice_loop_enabled,
        "delay": delay,
    }
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

def load_state():
    global voice_loop_enabled, delay
    if not os.path.exists(STATE_FILE):
        return
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
        text_slide_targets.update(data.get("text_slide_targets", {}))
        voice_slide_targets.update(data.get("voice_slide_targets", {}))
        voice_loop_enabled = data.get("voice_loop_enabled", False)
        delay = data.get("delay", delay)
    except:
        pass

# ---------- TEXT BUILDER ----------
def animated_text(step: int, word: str = ""):
    emoji = EMOJIS[step % len(EMOJIS)]
    if word:
        text = f"{word} {DEFAULT_TEXT}"
    else:
        text = DEFAULT_TEXT
    return f"{emoji} {text} {emoji}"

# ---------- VOICE (HINDI ONLY) ----------
async def send_voice(bot, chat_id):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as f:
            gTTS(text=DEFAULT_TEXT, lang="hi").save(f.name)
            await bot.send_voice(chat_id, open(f.name, "rb"))
            os.unlink(f.name)
    except:
        pass

# ---------- SLIDE CONTROL ----------
def add_slide(uid, word):
    text_slide_targets[uid] = word
    voice_slide_targets[uid] = word
    save_state()

def remove_slide(uid):
    text_slide_targets.pop(uid, None)
    voice_slide_targets.pop(uid, None)
    save_state()

# ---------- VOICE LOOP ----------
def voice_on():
    global voice_loop_enabled
    voice_loop_enabled = True
    save_state()

def voice_off():
    global voice_loop_enabled
    voice_loop_enabled = False
    save_state()

# ---------- AUTO REPLY ----------
async def auto_reply(update, context):
    if not update.message or not update.message.text:
        return

    uid = str(update.message.from_user.id)
    chat_id = update.message.chat_id
    step = int(time.time())

    if uid in text_slide_targets:
        word = text_slide_targets[uid]
        await update.message.reply_text(animated_text(step, word))
        await asyncio.sleep(delay)

    if uid in voice_slide_targets:
        await send_voice(context.bot, chat_id)

    if voice_loop_enabled:
        await send_voice(context.bot, chat_id)

# ---------- GROUP NAME LOOP ----------
async def group_name_loop(bot, chat_id, base_word):
    i = 0
    while True:
        try:
            emoji = EMOJIS[i % len(EMOJIS)]
            name = f"{emoji} {base_word} {DEFAULT_TEXT} {emoji}"
            await bot.set_chat_title(chat_id, name)
            i += 1
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            break
        except:
            await asyncio.sleep(2)

def start_ncloop(bot, chat_id, base_word):
    if chat_id in group_name_tasks:
        return
    task = asyncio.create_task(group_name_loop(bot, chat_id, base_word))
    group_name_tasks[chat_id] = task

def stop_ncloop(chat_id):
    task = group_name_tasks.pop(chat_id, None)
    if task:
        task.cancel()
