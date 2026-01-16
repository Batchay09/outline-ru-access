# Outline RU Access

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-brightgreen?style=for-the-badge)
![Outline](https://img.shields.io/badge/Outline-VPN-green?style=for-the-badge)
![Shadowsocks](https://img.shields.io/badge/Shadowsocks-Proxy-blue?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-yellow?style=for-the-badge&logo=python)

**VPN сервер для доступа к российским ресурсам из-за рубежа**

[Установка](#-быстрая-установка) • [Telegram Bot](#-telegram-bot) • [Клиенты](#-клиенты) • [Changelog](CHANGELOG.md)

</div>

## 🎯 Назначение

Этот проект позволяет людям за пределами России получить доступ к российским сайтам и сервисам, которые заблокированы для иностранных IP-адресов.

## ✨ Особенности

- 🚀 **Быстрая установка** — один скрипт, 2 минуты
- 🔐 **Shadowsocks** — современный протокол, сложно заблокировать
- 🤖 **Telegram Bot** — автоматическая выдача ключей пользователям
- 📱 **Кроссплатформенность** — iOS, Android, Windows, macOS, Linux
- 👥 **Мульти-пользователи** — легко добавлять новых пользователей
- 🔄 **Автообновление** — Watchtower обновляет сервер автоматически
- 📊 **Админ-панель** — управление через Telegram бота

## 🚀 Быстрая установка

### 1. Установка Outline сервера

```bash
# На сервере с Ubuntu/Debian
wget -qO- https://raw.githubusercontent.com/Jigsaw-Code/outline-server/master/src/server_manager/install_scripts/install_server.sh | bash
```

После установки скрипт выдаст:
1. **Ключ для Outline Manager** — JSON строка для управления сервером
2. **Access Key** — ссылка `ss://...` для подключения клиентов

### 2. Установка Telegram бота

```bash
cd bot

# Создайте .env файл
cat > .env << EOF
BOT_TOKEN=ваш_токен_от_botfather
ADMIN_ID=ваш_telegram_id
OUTLINE_API_URL=https://ваш_сервер:порт/секрет
EOF

# Запустите
docker-compose up -d --build
```

## 🤖 Telegram Bot

Бот автоматически выдаёт VPN-ключи пользователям:

**Для пользователей:**
- `/start` — получить меню
- 🔑 Получить ключ — создаёт персональный ключ + QR-код
- 📱 Инструкции для iOS/Android/Windows/macOS

**Для админа:**
- ⚙️ Админ-панель — только для `ADMIN_ID`
- 📊 Статистика — количество выданных ключей
- 👥 Все ключи — список всех ключей
- ➕ Создать / 🗑 Удалить ключи

## 📱 Клиенты

### Скачать Outline Client:
| Платформа | Ссылка |
|-----------|--------|
| iOS | [App Store](https://apps.apple.com/app/outline-app/id1356177741) |
| Android | [Google Play](https://play.google.com/store/apps/details?id=org.outline.android.client) |
| Windows | [Download](https://raw.githubusercontent.com/Jigsaw-Code/outline-releases/master/client/Outline-Client.exe) |
| macOS | [App Store](https://apps.apple.com/app/outline-app/id1356178125) |

### Подключение:
1. Откройте Outline Client
2. Нажмите "+" → "Добавить сервер"
3. Вставьте ключ `ss://...` или отсканируйте QR
4. Подключитесь!

## 🔧 Управление сервером

### Outline Manager
1. Скачайте [Outline Manager](https://getoutline.org/get-started/#step-1)
2. Вставьте JSON ключ из установки
3. Добавляйте/удаляйте пользователей через интерфейс

### Полезные команды
```bash
# Статус контейнеров
docker ps

# Логи Outline сервера
docker logs shadowbox

# Логи Telegram бота
docker logs outline-bot

# Перезапуск
docker restart shadowbox
docker restart outline-bot

# Получить API credentials
cat /opt/outline/access.txt
```

## 🔥 Firewall

Убедитесь что открыты порты:
- **Management port** (TCP) — указан при установке
- **Access key port** (TCP + UDP) — указан при установке

```bash
# UFW
ufw allow <management_port>/tcp
ufw allow <access_port>/tcp
ufw allow <access_port>/udp

# iptables
iptables -A INPUT -p tcp --dport <port> -j ACCEPT
iptables -A INPUT -p udp --dport <port> -j ACCEPT
```

## 📋 Требования

- VPS с российским IP (или IP который не заблокирован)
- Ubuntu 18.04+ / Debian 10+ / CentOS 7+
- Docker (устанавливается автоматически)
- 512MB RAM минимум

## 🔒 Безопасность

- Все данные шифруются ChaCha20-Poly1305
- Каждый пользователь имеет уникальный ключ
- Ключи можно отозвать в любой момент
- Нет логов активности

## 📄 Лицензия

MIT License

---

<div align="center">
Made with ❤️ for people who need access to Russian resources
</div>
