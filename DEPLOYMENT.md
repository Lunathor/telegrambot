# 🚀 Руководство по развертыванию Telegram-бота

Подробные инструкции по настройке и запуску бота "Какое у вас тотемное животное?" в продакшене.

## 📋 Предварительные требования

### Системные требования
- **ОС**: Linux (Ubuntu 18.04+), Windows 10+ или macOS 10.14+
- **Python**: 3.8 или выше
- **RAM**: Минимум 512 MB (рекомендуется 1 GB+)
- **Диск**: Минимум 100 MB свободного места
- **Сеть**: Стабильное интернет-соединение

### Программное обеспечение
- Python 3.8+
- pip (менеджер пакетов Python)
- Git (для управления версиями)
- virtualenv или venv (для изоляции зависимостей)

## 🔑 Получение Telegram Bot Token

### 1. Создание бота через BotFather
1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям:
   - Введите имя бота (например: "Тотемное Животное Зоопарка")
   - Введите username бота (например: "totem_zoo_bot")
4. Получите токен бота (выглядит как `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Настройка бота
Отправьте BotFather следующие команды для настройки:

```
/setdescription - Установить описание бота
/setabouttext - Установить информацию о боте
/setuserpic - Установить аватар бота
/setcommands - Установить команды бота
```

### 3. Команды для настройки
```
start - Начать викторину
restart - Перезапустить викторину
help - Показать справку
```

## 🖥️ Локальная установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/telegrambot.git
cd telegrambot
```

### 2. Создание виртуального окружения
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Создание файла конфигурации
Создайте файл `.env` в корне проекта:
```env
BOT_TOKEN=your_actual_bot_token_here
ZOO_CONTACT_EMAIL=contact@moscowzoo.ru
ZOO_CONTACT_PHONE=+7(495)123-45-67
LOG_LEVEL=INFO
```

### 5. Тестирование установки
```bash
# Запуск тестов
python test_bot.py

# Запуск бота
python bot.py
```

## ☁️ Развертывание на сервере

### Вариант 1: VPS/Выделенный сервер

#### 1. Подготовка сервера
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и зависимостей
sudo apt install python3 python3-pip python3-venv git nginx -y

# Создание пользователя для бота
sudo adduser botuser
sudo usermod -aG sudo botuser
```

#### 2. Установка бота
```bash
# Переключение на пользователя бота
sudo su - botuser

# Клонирование репозитория
git clone https://github.com/your-username/telegrambot.git
cd telegrambot

# Создание виртуального окружения
python3 -m venv .venv
source .venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Создание конфигурации
cp config.py .env
nano .env  # Редактирование конфигурации
```

#### 3. Настройка systemd сервиса
Создайте файл `/etc/systemd/system/totem-bot.service`:
```ini
[Unit]
Description=Telegram Totem Animal Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/telegrambot
Environment=PATH=/home/botuser/telegrambot/.venv/bin
ExecStart=/home/botuser/telegrambot/.venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 4. Запуск сервиса
```bash
sudo systemctl daemon-reload
sudo systemctl enable totem-bot
sudo systemctl start totem-bot
sudo systemctl status totem-bot
```

### Вариант 2: Docker

#### 1. Создание Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

#### 2. Создание docker-compose.yml
```yaml
version: '3.8'

services:
  totem-bot:
    build: .
    container_name: totem-bot
    restart: unless-stopped
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ZOO_CONTACT_EMAIL=${ZOO_CONTACT_EMAIL}
      - ZOO_CONTACT_PHONE=${ZOO_CONTACT_PHONE}
      - LOG_LEVEL=${LOG_LEVEL}
    volumes:
      - ./generated_images:/app/generated_images
      - ./logs:/app/logs
```

#### 3. Запуск с Docker
```bash
# Создание .env файла
cp config.py .env
nano .env

# Запуск контейнера
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

### Вариант 3: Облачные платформы

#### Heroku
```bash
# Установка Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Логин в Heroku
heroku login

# Создание приложения
heroku create your-totem-bot

# Настройка переменных окружения
heroku config:set BOT_TOKEN=your_token
heroku config:set ZOO_CONTACT_EMAIL=contact@zoo.ru
heroku config:set ZOO_CONTACT_PHONE=+7(495)123-45-67

# Деплой
git push heroku main
```

#### Railway
```bash
# Установка Railway CLI
npm install -g @railway/cli

# Логин
railway login

# Создание проекта
railway init

# Настройка переменных
railway variables set BOT_TOKEN=your_token

# Деплой
railway up
```

## 🔧 Настройка мониторинга

### 1. Логирование
Создайте папку для логов:
```bash
mkdir logs
```

Настройте ротацию логов в `/etc/logrotate.d/totem-bot`:
```
/home/botuser/telegrambot/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 botuser botuser
    postrotate
        systemctl reload totem-bot
    endscript
}
```

### 2. Мониторинг состояния
Создайте скрипт проверки `/usr/local/bin/check-bot.sh`:
```bash
#!/bin/bash
if ! systemctl is-active --quiet totem-bot; then
    echo "Bot is down, restarting..."
    systemctl restart totem-bot
    echo "Bot restarted at $(date)" | mail -s "Bot Restart" admin@example.com
fi
```

Добавьте в crontab:
```bash
*/5 * * * * /usr/local/bin/check-bot.sh
```

### 3. Алерты
Настройте уведомления о проблемах:
```bash
# Установка mailutils
sudo apt install mailutils

# Настройка почты
sudo nano /etc/postfix/main.cf
```

## 📊 Аналитика и метрики

### 1. Базовые метрики
- Количество активных пользователей
- Время прохождения викторины
- Популярность животных
- Количество обращений к программе опеки

### 2. Логирование метрик
```python
# В bot.py добавьте:
import json
from datetime import datetime

def log_metric(metric_name, value, user_id=None):
    metric_data = {
        'timestamp': datetime.now().isoformat(),
        'metric': metric_name,
        'value': value,
        'user_id': user_id
    }
    
    with open('logs/metrics.json', 'a') as f:
        f.write(json.dumps(metric_data) + '\n')
```

### 3. Дашборд
Создайте простой веб-интерфейс для просмотра метрик:
```python
# metrics_dashboard.py
from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route('/')
def dashboard():
    # Чтение и обработка метрик
    return render_template('dashboard.html', metrics=metrics)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 🔒 Безопасность

### 1. Ограничение доступа
```bash
# Настройка firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. SSL сертификат
```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d yourdomain.com
```

### 3. Регулярные обновления
```bash
# Автоматические обновления безопасности
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 🚀 Масштабирование

### 1. Балансировка нагрузки
Используйте nginx для распределения запросов между несколькими экземплярами бота:

```nginx
upstream bot_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://bot_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. База данных
Для масштабирования замените in-memory хранилище на PostgreSQL:

```python
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            database="totem_bot",
            user="botuser",
            password="password"
        )
    
    def save_user_data(self, user_id, data):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_data (user_id, data, created_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (user_id) 
                DO UPDATE SET data = %s, updated_at = NOW()
            """, (user_id, json.dumps(data), json.dumps(data)))
            self.conn.commit()
```

## 📝 Чек-лист развертывания

- [ ] Получен Telegram Bot Token
- [ ] Настроен файл .env с корректными данными
- [ ] Установлены все зависимости
- [ ] Прошли все тесты
- [ ] Настроен systemd сервис (или Docker)
- [ ] Настроено логирование
- [ ] Настроен мониторинг
- [ ] Настроена безопасность
- [ ] Протестирована работа бота
- [ ] Настроены алерты
- [ ] Документированы настройки

## 🆘 Устранение неполадок

### Частые проблемы

#### 1. Бот не отвечает
```bash
# Проверка статуса сервиса
sudo systemctl status totem-bot

# Просмотр логов
sudo journalctl -u totem-bot -f

# Проверка токена
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"
```

#### 2. Ошибки с изображениями
```bash
# Проверка прав доступа
ls -la generated_images/

# Установка прав
chmod 755 generated_images/
chown botuser:botuser generated_images/
```

#### 3. Проблемы с зависимостями
```bash
# Пересоздание виртуального окружения
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `sudo journalctl -u totem-bot -f`
2. Запустите тесты: `python test_bot.py`
3. Проверьте конфигурацию: `cat .env`
4. Обратитесь к документации или создайте issue в GitHub

---

**Удачного развертывания! 🚀**
