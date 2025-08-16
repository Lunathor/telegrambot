import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Контактные данные сотрудника зоопарка
ZOO_CONTACT_EMAIL = os.getenv('ZOO_CONTACT_EMAIL', 'contact@moscowzoo.ru')
ZOO_CONTACT_PHONE = os.getenv('ZOO_CONTACT_PHONE', '+7(495)123-45-67')

# Настройки логирования
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Настройки викторины
MAX_QUESTIONS = 10
MIN_QUESTIONS = 5
