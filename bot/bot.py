#!/usr/bin/env python3
"""
Outline VPN Telegram Bot
Автоматическая выдача ключей для доступа к российским ресурсам
"""

import os
import json
import logging
import requests
import urllib3
from io import BytesIO

import qrcode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Отключаем предупреждения SSL (Outline использует self-signed сертификат)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN", "8475117340:AAGU3eukBvvYdIpI9Odj2EUsbwwohirivRo")
ADMIN_ID = int(os.getenv("ADMIN_ID", "5330170"))
OUTLINE_API_URL = os.getenv("OUTLINE_API_URL", "")
OUTLINE_CERT_SHA256 = os.getenv("OUTLINE_CERT_SHA256", "")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Хранилище выданных ключей (user_id -> key_id)
user_keys = {}


def outline_request(method: str, endpoint: str, data: dict = None) -> dict:
    """Запрос к Outline API"""
    url = f"{OUTLINE_API_URL}{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, verify=False, timeout=10)
        elif method == "POST":
            resp = requests.post(url, json=data, verify=False, timeout=10)
        elif method == "DELETE":
            resp = requests.delete(url, verify=False, timeout=10)
        elif method == "PUT":
            resp = requests.put(url, json=data, verify=False, timeout=10)
        else:
            return {"error": "Unknown method"}
        
        if resp.status_code in [200, 201, 204]:
            if resp.text:
                return resp.json()
            return {"success": True}
        return {"error": f"HTTP {resp.status_code}"}
    except Exception as e:
        logger.error(f"Outline API error: {e}")
        return {"error": str(e)}


def get_all_keys() -> list:
    """Получить все ключи"""
    result = outline_request("GET", "/access-keys")
    return result.get("accessKeys", [])


def create_key(name: str = "") -> dict:
    """Создать новый ключ"""
    result = outline_request("POST", "/access-keys")
    if "id" in result and name:
        outline_request("PUT", f"/access-keys/{result['id']}/name", {"name": name})
        result["name"] = name
    return result


def delete_key(key_id: str) -> bool:
    """Удалить ключ"""
    result = outline_request("DELETE", f"/access-keys/{key_id}")
    return "error" not in result


def generate_qr(data: str) -> BytesIO:
    """Генерация QR-кода"""
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    bio = BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    return bio


def get_user_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для обычного пользователя"""
    keyboard = [
        [InlineKeyboardButton("🔑 Получить ключ", callback_data="get_key")],
        [InlineKeyboardButton("📱 iOS", callback_data="ios"),
         InlineKeyboardButton("🤖 Android", callback_data="android")],
        [InlineKeyboardButton("💻 Windows", callback_data="windows"),
         InlineKeyboardButton("🍎 macOS", callback_data="macos")],
        [InlineKeyboardButton("📖 Инструкция", callback_data="help")]
    ]
    
    # Добавляем админ-кнопку для админа
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("⚙️ Админ-панель", callback_data="admin")])
    
    return InlineKeyboardMarkup(keyboard)


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура админ-панели"""
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("👥 Все ключи", callback_data="admin_keys")],
        [InlineKeyboardButton("➕ Создать ключ", callback_data="admin_create")],
        [InlineKeyboardButton("🗑 Удалить ключ", callback_data="admin_delete")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    
    welcome = f"""
👋 Привет, {user.first_name}!

🌍 Этот бот выдаёт VPN-ключи для доступа к российским сайтам из-за рубежа.

🔐 Протокол: Shadowsocks (Outline)
📱 Работает на: iOS, Android, Windows, macOS

Нажми «🔑 Получить ключ» чтобы начать!
"""
    
    await update.message.reply_text(
        welcome,
        reply_markup=get_user_keyboard(user.id)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    # === Пользовательские кнопки ===
    
    if data == "get_key":
        await query.edit_message_text("⏳ Создаю ключ...")
        
        # Проверяем, есть ли уже ключ у пользователя
        if user_id in user_keys:
            keys = get_all_keys()
            for key in keys:
                if key["id"] == user_keys[user_id]:
                    access_url = key["accessUrl"]
                    await send_key_message(query, access_url, is_new=False)
                    return
        
        # Создаём новый ключ
        name = f"User_{user_id}"
        key = create_key(name)
        
        if "accessUrl" in key:
            user_keys[user_id] = key["id"]
            await send_key_message(query, key["accessUrl"], is_new=True)
        else:
            await query.edit_message_text(
                f"❌ Ошибка создания ключа: {key.get('error', 'Unknown')}",
                reply_markup=get_user_keyboard(user_id)
            )
    
    elif data == "ios":
        await query.edit_message_text(
            "📱 **Outline для iOS**\n\n"
            "1️⃣ Скачайте приложение:\n"
            "https://apps.apple.com/app/outline-app/id1356177741\n\n"
            "2️⃣ Получите ключ кнопкой «🔑 Получить ключ»\n\n"
            "3️⃣ Нажмите на ключ — он автоматически добавится в приложение\n\n"
            "4️⃣ Нажмите «Подключить»",
            reply_markup=get_user_keyboard(user_id),
            parse_mode="Markdown"
        )
    
    elif data == "android":
        await query.edit_message_text(
            "🤖 **Outline для Android**\n\n"
            "1️⃣ Скачайте приложение:\n"
            "https://play.google.com/store/apps/details?id=org.outline.android.client\n\n"
            "2️⃣ Получите ключ кнопкой «🔑 Получить ключ»\n\n"
            "3️⃣ Скопируйте ключ и вставьте в приложение\n\n"
            "4️⃣ Или отсканируйте QR-код",
            reply_markup=get_user_keyboard(user_id),
            parse_mode="Markdown"
        )
    
    elif data == "windows":
        await query.edit_message_text(
            "💻 **Outline для Windows**\n\n"
            "1️⃣ Скачайте приложение:\n"
            "https://raw.githubusercontent.com/Jigsaw-Code/outline-releases/master/client/Outline-Client.exe\n\n"
            "2️⃣ Установите и запустите\n\n"
            "3️⃣ Получите ключ и скопируйте его\n\n"
            "4️⃣ В приложении: + → Вставить ключ",
            reply_markup=get_user_keyboard(user_id),
            parse_mode="Markdown"
        )
    
    elif data == "macos":
        await query.edit_message_text(
            "🍎 **Outline для macOS**\n\n"
            "1️⃣ Скачайте приложение:\n"
            "https://apps.apple.com/app/outline-app/id1356178125\n\n"
            "2️⃣ Установите и запустите\n\n"
            "3️⃣ Получите ключ и скопируйте его\n\n"
            "4️⃣ В приложении: + → Вставить ключ",
            reply_markup=get_user_keyboard(user_id),
            parse_mode="Markdown"
        )
    
    elif data == "help":
        await query.edit_message_text(
            "📖 **Инструкция**\n\n"
            "1️⃣ Скачайте Outline для своего устройства (кнопки ниже)\n\n"
            "2️⃣ Нажмите «🔑 Получить ключ»\n\n"
            "3️⃣ Скопируйте ключ `ss://...` или отсканируйте QR\n\n"
            "4️⃣ Вставьте ключ в приложение Outline\n\n"
            "5️⃣ Подключитесь и пользуйтесь!\n\n"
            "❓ Проблемы? Напишите админу.",
            reply_markup=get_user_keyboard(user_id),
            parse_mode="Markdown"
        )
    
    elif data == "back":
        await query.edit_message_text(
            "🏠 Главное меню",
            reply_markup=get_user_keyboard(user_id)
        )
    
    # === Админ-кнопки ===
    
    elif data == "admin" and user_id == ADMIN_ID:
        await query.edit_message_text(
            "⚙️ **Админ-панель**\n\n"
            "Выберите действие:",
            reply_markup=get_admin_keyboard(),
            parse_mode="Markdown"
        )
    
    elif data == "admin_stats" and user_id == ADMIN_ID:
        keys = get_all_keys()
        text = f"📊 **Статистика**\n\n"
        text += f"👥 Всего ключей: {len(keys)}\n"
        text += f"🔗 API: `{OUTLINE_API_URL[:50]}...`"
        
        await query.edit_message_text(
            text,
            reply_markup=get_admin_keyboard(),
            parse_mode="Markdown"
        )
    
    elif data == "admin_keys" and user_id == ADMIN_ID:
        keys = get_all_keys()
        if not keys:
            text = "👥 Ключей нет"
        else:
            text = "👥 **Все ключи:**\n\n"
            for key in keys[:20]:  # Максимум 20
                name = key.get("name", "Без имени")
                key_id = key.get("id", "?")
                text += f"• `{key_id}` — {name}\n"
            if len(keys) > 20:
                text += f"\n... и ещё {len(keys) - 20}"
        
        await query.edit_message_text(
            text,
            reply_markup=get_admin_keyboard(),
            parse_mode="Markdown"
        )
    
    elif data == "admin_create" and user_id == ADMIN_ID:
        key = create_key("Admin_created")
        if "accessUrl" in key:
            text = f"✅ Ключ создан!\n\n`{key['accessUrl']}`"
        else:
            text = f"❌ Ошибка: {key.get('error', 'Unknown')}"
        
        await query.edit_message_text(
            text,
            reply_markup=get_admin_keyboard(),
            parse_mode="Markdown"
        )
    
    elif data == "admin_delete" and user_id == ADMIN_ID:
        keys = get_all_keys()
        if not keys:
            await query.edit_message_text(
                "Нет ключей для удаления",
                reply_markup=get_admin_keyboard()
            )
            return
        
        keyboard = []
        for key in keys[:10]:
            name = key.get("name", "Без имени")[:15]
            key_id = key.get("id")
            keyboard.append([InlineKeyboardButton(
                f"🗑 {key_id}: {name}",
                callback_data=f"del_{key_id}"
            )])
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="admin")])
        
        await query.edit_message_text(
            "Выберите ключ для удаления:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data.startswith("del_") and user_id == ADMIN_ID:
        key_id = data[4:]
        if delete_key(key_id):
            text = f"✅ Ключ {key_id} удалён"
        else:
            text = f"❌ Ошибка удаления ключа {key_id}"
        
        await query.edit_message_text(
            text,
            reply_markup=get_admin_keyboard()
        )


async def send_key_message(query, access_url: str, is_new: bool):
    """Отправка сообщения с ключом и QR-кодом"""
    user_id = query.from_user.id
    
    status = "🆕 Ваш новый ключ:" if is_new else "🔑 Ваш ключ:"
    
    text = f"""
{status}

```
{access_url}
```

📋 Нажмите на ключ чтобы скопировать

📱 Или отсканируйте QR-код ниже
"""
    
    # Отправляем текст
    await query.edit_message_text(
        text,
        reply_markup=get_user_keyboard(user_id),
        parse_mode="Markdown"
    )
    
    # Отправляем QR-код отдельным сообщением
    try:
        qr_image = generate_qr(access_url)
        await query.message.reply_photo(
            photo=qr_image,
            caption="📱 QR-код для Outline"
        )
    except Exception as e:
        logger.error(f"QR generation error: {e}")


def main():
    """Запуск бота"""
    if not OUTLINE_API_URL:
        logger.error("OUTLINE_API_URL не задан!")
        return
    
    logger.info(f"Starting bot...")
    logger.info(f"Admin ID: {ADMIN_ID}")
    logger.info(f"Outline API: {OUTLINE_API_URL[:50]}...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
