# Outline RU Access

<div align="center">

![Outline](https://img.shields.io/badge/Outline-VPN-green?style=for-the-badge)
![Shadowsocks](https://img.shields.io/badge/Shadowsocks-Proxy-blue?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge)

**VPN сервер для доступа к российским ресурсам из-за рубежа**

</div>

## 🎯 Назначение

Этот проект позволяет людям за пределами России получить доступ к российским сайтам и сервисам, которые заблокированы для иностранных IP-адресов.

## ✨ Особенности

- 🚀 **Быстрая установка** — один скрипт, 2 минуты
- 🔐 **Shadowsocks** — современный протокол, сложно заблокировать
- 📱 **Кроссплатформенность** — iOS, Android, Windows, macOS, Linux
- 👥 **Мульти-пользователи** — легко добавлять новых пользователей
- 🔄 **Автообновление** — Watchtower обновляет сервер автоматически
- 📊 **Управление** — Outline Manager для администрирования

## 🚀 Быстрая установка

```bash
# На сервере с Ubuntu/Debian
wget -qO- https://raw.githubusercontent.com/Jigsaw-Code/outline-server/master/src/server_manager/install_scripts/install_server.sh | bash
```

После установки скрипт выдаст:
1. **Ключ для Outline Manager** — JSON строка для управления сервером
2. **Access Key** — ссылка `ss://...` для подключения клиентов

## 📱 Клиенты

### Скачать Outline Client:
- **iOS**: [App Store](https://apps.apple.com/app/outline-app/id1356177741)
- **Android**: [Google Play](https://play.google.com/store/apps/details?id=org.outline.android.client)
- **Windows**: [Download](https://raw.githubusercontent.com/Jigsaw-Code/outline-releases/master/client/Outline-Client.exe)
- **macOS**: [Download](https://raw.githubusercontent.com/Jigsaw-Code/outline-releases/master/client/Outline-Client.dmg)

### Подключение:
1. Откройте Outline Client
2. Нажмите "+" → "Добавить сервер"
3. Вставьте ключ `ss://...`
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

# Логи сервера
docker logs shadowbox

# Перезапуск
docker restart shadowbox

# Получить ключи через API
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
