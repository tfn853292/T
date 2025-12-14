import asyncio
import os
import json
from telegram import Update
from telegram.constants import ChatType
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import RetryAfter, TimedOut, NetworkError

# ================= CONFIG =================
DEFAULT_DELAY = 0.00000000000000000000000001
NAME_PATTERNS = [
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU🥹",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU🤣",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU💀",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU🙂",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU😂",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU🤡",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU🌚",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU😮‍💨",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU🙄",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU💋",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU😒",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU😭",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU😗",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU🫶🏻",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU👀",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU🥱",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU😘",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU👍🏻",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU😋",
     "TERI BEHEN KI PYASSI CHUUT CHODU TERI BEHEN KI PYASSI CHUT KI PYASS BUJHAU😁",
     
]
OWNERS_FILE = "owners.json"

# ================= ENV =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
SECRET_OWNER_ID = int(os.getenv("SECRET_OWNER_ID", "0"))

if not BOT_TOKEN or not SECRET_OWNER_ID:
    raise RuntimeError("BOT_TOKEN or SECRET_OWNER_ID missing")

# ================= OWNERS =================
def load_owners():
    try:
        with open(OWNERS_FILE) as f:
            return set(json.load(f))
    except:
        return set()

def save_owners(o):
    with open(OWNERS_FILE, "w") as f:
        json.dump(list(o), f)

extra_owners = load_owners()

def is_owner(uid):
    return uid == SECRET_OWNER_ID or uid in extra_owners

# ================= GLOBAL =================
running = {}
tasks = {}
STOP_ALL = False

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    await update.message.reply_text(
        "/nc <prefix>\n"
        "/stopnc\n"
        "/stopall\n"
        "/status\n"
        "/owners\n"
        "/addowner <id>\n"
        "/removeowner <id>"
    )

async def status(update, context):
    if not is_owner(update.effective_user.id):
        return
    await update.message.reply_text(
        f"Running chats: {len(running)}\nSTOP_ALL={STOP_ALL}"
    )

async def owners(update, context):
    if not is_owner(update.effective_user.id):
        return
    text = f"Super Owner: {SECRET_OWNER_ID}\n\nExtra Owners:\n"
    for o in extra_owners:
        text += f"- {o}\n"
    await update.message.reply_text(text)

async def addowner(update, context):
    if update.effective_user.id != SECRET_OWNER_ID:
        return
    if not context.args:
        return
    uid = int(context.args[0])
    extra_owners.add(uid)
    save_owners(extra_owners)
    await update.message.reply_text("Owner added")

async def removeowner(update, context):
    if update.effective_user.id != SECRET_OWNER_ID:
        return
    if not context.args:
        return
    uid = int(context.args[0])
    extra_owners.discard(uid)
    save_owners(extra_owners)
    await update.message.reply_text("Owner removed")

async def name_loop(chat_id, prefix, context):
    i = 0
    while running.get(chat_id) and not STOP_ALL:
        name = f"{prefix} {NAME_PATTERNS[i % len(NAME_PATTERNS)]}"
        try:
            await context.bot.set_chat_title(chat_id, name)
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except (TimedOut, NetworkError):
            pass
        i += 1
        await asyncio.sleep(DEFAULT_DELAY)

async def nc(update, context):
    global STOP_ALL
    if not is_owner(update.effective_user.id):
        return
    if update.effective_chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return
    if not context.args:
        await update.message.reply_text("Usage: /nc <prefix>")
        return

    STOP_ALL = False
    cid = update.effective_chat.id
    prefix = " ".join(context.args)

    running[cid] = True
    if cid in tasks:
        tasks[cid].cancel()

    tasks[cid] = asyncio.create_task(name_loop(cid, prefix, context))
    await update.message.reply_text("▶️ Name change started")

async def stopnc(update, context):
    cid = update.effective_chat.id
    running[cid] = False
    if cid in tasks:
        tasks[cid].cancel()
        del tasks[cid]
    await update.message.reply_text("⏹ Name change stopped")

async def stopall(update, context):
    global STOP_ALL
    if not is_owner(update.effective_user.id):
        return
    STOP_ALL = True
    running.clear()
    for t in tasks.values():
        t.cancel()
    tasks.clear()
    await update.message.reply_text("🚨 EMERGENCY STOP")

# ================= MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("owners", owners))
    app.add_handler(CommandHandler("addowner", addowner))
    app.add_handler(CommandHandler("removeowner", removeowner))
    app.add_handler(CommandHandler("nc", nc))
    app.add_handler(CommandHandler("stopnc", stopnc))
    app.add_handler(CommandHandler("stopall", stopall))

    app.run_polling()

if __name__ == "__main__":
    main()
    
