"""
Telegram Yuk Bot (single-file, Pyrogram)
100% Pyrogram versiyasi, `telegram` modulidan foydalanmaydi.

Requirements:
- pyrogram
- tgcrypto

Run:
1. pip install pyrogram tgcrypto
2. Edit BOT_TOKEN, TARGET_CHANNEL, ALLOWED_ADMINS
3. python bot.py
"""

import logging
from typing import Dict, Optional
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

# ==========================
# CONFIG
# ==========================
BOT_TOKEN = "8320674665:AAHfy68KUzgM53fUygAypnZKVMLpze5Nr9I"
TARGET_CHANNEL = "@yukllarr"
ALLOWED_ADMINS = [2047965739]  # your Telegram user ID(s)
SOURCE_GROUPS = [-1002185605802]  # or None to allow all groups

KEYWORDS = [
    "yuk bor", "mashina kerak", "yuk kerak", "yuk tashish", "isuzu", "gazel",
    "orqaga qaytish", "yuk olib ketadi", "tonna", "transport kerak"
]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

admin_mode: Dict[int, Optional[str]] = {}

# ==========================
# Helper
# ==========================

def is_valid_ad(text: Optional[str]) -> bool:
    if not text:
        return False
    t = text.lower()
    for k in KEYWORDS:
        if k in t:
            return True
    return False

# ==========================
# Admin keyboard
# ==========================

def admin_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📊 Statistika", callback_data="stats"),
         InlineKeyboardButton("🔑 Kalit so'zlar", callback_data="keywords")],
        [InlineKeyboardButton("➕ Kalit qo'shish", callback_data="add_keyword"),
         InlineKeyboardButton("➖ Kalit o'chirish", callback_data="remove_keyword")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==========================
# Pyrogram Client
# ==========================

app = Client("yukbot", bot_token=BOT_TOKEN)

@app.on_message(filters.command("start") & (filters.private | filters.group))
async def on_start(client: Client, message: Message):
    await message.reply_text("Bot ishga tushdi. Guruhga qo'shing va admin qiling.")

@app.on_message(filters.command("admin") & filters.private)
async def on_admin(client: Client, message: Message):
    uid = message.from_user.id
    if uid not in ALLOWED_ADMINS:
        await message.reply_text("Siz admin emassiz.")
        return
    await message.reply_text("Admin panel:", reply_markup=admin_keyboard())

@app.on_callback_query()
async def on_callback(client: Client, callback: CallbackQuery):
    uid = callback.from_user.id
    if uid not in ALLOWED_ADMINS:
        await callback.answer("Siz admin emassiz.", show_alert=True)
        return
    data = callback.data or ""
    if data == "stats":
        await callback.edit_message_text(f"📊 Statistika:\nKalit so'zlar soni: {len(KEYWORDS)}")
    elif data == "keywords":
        await callback.edit_message_text("🔑 Kalit so'zlar:\n" + "\n".join(KEYWORDS))
    elif data == "add_keyword":
        admin_mode[uid] = "add"
        await callback.edit_message_text("Yangi kalit so'zni yuboring:")
    elif data == "remove_keyword":
        admin_mode[uid] = "remove"
        await callback.edit_message_text("O'chiriladigan kalit so'zni yuboring:")
    else:
        await callback.answer()

@app.on_message(filters.text & filters.private)
async def on_admin_text(client: Client, message: Message):
    uid = message.from_user.id
    if uid not in ALLOWED_ADMINS:
        return
    mode = admin_mode.get(uid)
    txt = message.text.strip().lower()
    if not mode:
        return
    if mode == "add":
        if txt in KEYWORDS:
            await message.reply_text(f"'{txt}' allaqachon mavjud.")
        else:
            KEYWORDS.append(txt)
            await message.reply_text(f"Qo'shildi: {txt}")
    elif mode == "remove":
        if txt in KEYWORDS:
            KEYWORDS.remove(txt)
            await message.reply_text(f"O'chirildi: {txt}")
        else:
            await message.reply_text("Topilmadi.")
    admin_mode[uid] = None

@app.on_message(filters.group & filters.text)
async def message_collector(client: Client, message: Message):
    if SOURCE_GROUPS and message.chat.id not in SOURCE_GROUPS:
        return
    text = message.text or ""
    if is_valid_ad(text):
        try:
            await client.send_message(chat_id=TARGET_CHANNEL, text=text)
            logger.info(f"Forwarded message from {message.chat.id} by {message.from_user.id}")
        except Exception as e:
            logger.error(f"Failed to forward: {e}")

# ==========================
# Self-test
# ==========================

def run_self_test():
    tests = [
        ("Yuk bor Toshkent", True),
        ("Salom hammaga", False),
        ("Isuzu yuk kerak 10 tonna", True),
        ("Rasmlar: check.png", False),
    ]
    ok = True
    for txt, expected in tests:
        got = is_valid_ad(txt)
        print(f"Test: '{txt}' -> expected={expected}, got={got}")
        if got != expected:
            ok = False
    print("Self-test passed" if ok else "Self-test FAILED")

if __name__ == "__main__":
    run_self_test()
    print("Starting Pyrogram bot...")
    app.run()