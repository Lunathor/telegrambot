"""
Telegram-бот "Какое у вас тотемное животное?"
Бот для популяризации программы опеки Московского зоопарка
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ContextTypes, ConversationHandler, MessageHandler, filters
)

from config import BOT_TOKEN, ZOO_CONTACT_EMAIL, ZOO_CONTACT_PHONE
from quiz_data import QUIZ_QUESTIONS, ANIMALS, GUARDIANSHIP_INFO

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния разговора
START, QUIZ, FEEDBACK = range(3)

# Хранилище данных пользователей (в продакшене лучше использовать базу данных)
user_data = {}

class QuizBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        
        # Основные команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("restart", self.restart_command))
        
        # Обработчики викторины
        self.application.add_handler(CallbackQueryHandler(self.handle_quiz_answer, pattern="^answer_"))
        self.application.add_handler(CallbackQueryHandler(self.handle_menu_action, pattern="^menu_"))
        
        # Обработчик обратной связи
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_feedback))
        
        # Обработчик ошибок
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        
        # Инициализация данных пользователя
        user_id = user.id
        user_data[user_id] = {
            'current_question': 0,
            'answers': {},
            'start_time': datetime.now().isoformat(),
            'quiz_completed': False
        }
        
        welcome_text = f"""
🦁 **Добро пожаловать в викторину "Какое у вас тотемное животное?"** 🦁

Привет, {user.first_name}! 

Я помогу тебе узнать, какое животное из Московского зоопарка больше всего подходит твоему характеру! 

🎯 **Как это работает:**
• Ответь на {len(QUIZ_QUESTIONS)} интересных вопросов
• Узнай свое тотемное животное
• Познакомься с программой опеки зоопарка
• Поделись результатом с друзьями

Готов начать увлекательное путешествие? 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("🎮 Начать викторину", callback_data="menu_start_quiz")],
            [InlineKeyboardButton("ℹ️ О программе опеки", callback_data="menu_guardianship")],
            [InlineKeyboardButton("📞 Связаться с зоопарком", callback_data="menu_contact")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
        return START
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
🆘 **Справка по боту**

📋 **Доступные команды:**
/start - Начать викторину
/restart - Перезапустить викторину
/help - Показать эту справку

🎯 **Как пройти викторину:**
1. Нажми "Начать викторину"
2. Отвечай на вопросы, выбирая один из вариантов
3. Узнай свое тотемное животное
4. Поделись результатом с друзьями

🐾 **О программе опеки:**
Узнай, как стать опекуном животного в Московском зоопарке и внести свой вклад в сохранение видов!

❓ **Нужна помощь?**
Используй кнопку "Связаться с зоопарком" для получения дополнительной информации.
        """
        
        keyboard = [
            [InlineKeyboardButton("🔙 Вернуться к началу", callback_data="menu_back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')
        return START
    
    async def restart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /restart"""
        user_id = update.effective_user.id
        
        # Сброс данных пользователя
        if user_id in user_data:
            user_data[user_id] = {
                'current_question': 0,
                'answers': {},
                'start_time': datetime.now().isoformat(),
                'quiz_completed': False
            }
        
        await self.start_command(update, context)
        return START
    
    async def handle_menu_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик действий в главном меню"""
        query = update.callback_query
        await query.answer()
        
        action = query.data.split('_')[1]
        
        if action == "start_quiz":
            await self.start_quiz(query)
        elif action == "guardianship":
            await self.show_guardianship_info(query)
        elif action == "contact":
            await self.show_contact_info(query)
        elif action == "back_to_start":
            await self.start_command(update, context)
    
    async def start_quiz(self, query):
        """Начало викторины"""
        user_id = query.from_user.id
        
        # Сброс данных для новой викторины
        user_data[user_id] = {
            'current_question': 0,
            'answers': {},
            'start_time': datetime.now().isoformat(),
            'quiz_completed': False
        }
        
        await self.show_question(query, user_id)
    
    async def show_question(self, query, user_id: int):
        """Показать текущий вопрос викторины"""
        current_q = user_data[user_id]['current_question']
        
        if current_q >= len(QUIZ_QUESTIONS):
            await self.show_results(query, user_id)
            return
        
        question_data = QUIZ_QUESTIONS[current_q]
        question_text = f"❓ **Вопрос {current_q + 1} из {len(QUIZ_QUESTIONS)}**\n\n{question_data['question']}"
        
        # Создание клавиатуры с вариантами ответов
        keyboard = []
        for i, option in enumerate(question_data['options']):
            keyboard.append([InlineKeyboardButton(
                option['text'], 
                callback_data=f"answer_{current_q}_{i}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query.message:
            await query.message.edit_text(question_text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await query.answer(question_text)
    
    async def handle_quiz_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ответов на вопросы викторины"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        _, question_id, answer_id = query.data.split('_')
        question_id, answer_id = int(question_id), int(answer_id)
        
        # Сохранение ответа
        if user_id not in user_data:
            user_data[user_id] = {
                'current_question': 0,
                'answers': {},
                'start_time': datetime.now().isoformat(),
                'quiz_completed': False
            }
        
        user_data[user_id]['answers'][question_id] = answer_id
        user_data[user_id]['current_question'] = question_id + 1
        
        # Показ следующего вопроса или результатов
        if user_data[user_id]['current_question'] < len(QUIZ_QUESTIONS):
            await self.show_question(query, user_id)
        else:
            await self.show_results(query, user_id)
    
    async def show_results(self, query, user_id: int):
        """Показать результаты викторины"""
        if user_id not in user_data or not user_data[user_id]['answers']:
            await query.message.edit_text("❌ Произошла ошибка. Попробуйте начать викторину заново.")
            return
        
        # Подсчет результатов
        animal_scores = {}
        for question_id, answer_id in user_data[user_id]['answers'].items():
            question = QUIZ_QUESTIONS[question_id]
            option = question['options'][answer_id]
            
            for animal, weight in option['weight'].items():
                if animal not in animal_scores:
                    animal_scores[animal] = 0
                animal_scores[animal] += weight
        
        # Определение победителя
        if animal_scores:
            winner_animal = max(animal_scores, key=animal_scores.get)
            animal_info = ANIMALS[winner_animal]
            
            # Отметка завершения викторины
            user_data[user_id]['quiz_completed'] = True
            user_data[user_id]['result_animal'] = winner_animal
            user_data[user_id]['completion_time'] = datetime.now().isoformat()
            
            # Формирование результата
            result_text = f"""
🎉 **Викторина завершена!** 🎉

{animal_info['emoji']} **Твое тотемное животное: {animal_info['name']}** {animal_info['emoji']}

📝 **Описание:**
{animal_info['description']}

🐾 **Интересные факты о {animal_info['name'].lower()}е:**
{animal_info['zoo_facts']}

💝 **О программе опеки:**
{animal_info['guardian_info']}

🎯 **Хочешь узнать больше о программе опеки или поделиться результатом?**
            """
            
            keyboard = [
                [InlineKeyboardButton("🐾 Узнать о программе опеки", callback_data="menu_guardianship")],
                [InlineKeyboardButton("📤 Поделиться результатом", callback_data="menu_share_result")],
                [InlineKeyboardButton("📞 Связаться с зоопарком", callback_data="menu_contact")],
                [InlineKeyboardButton("🔄 Пройти викторину еще раз", callback_data="menu_start_quiz")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.edit_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await query.message.edit_text("❌ Не удалось определить результат. Попробуйте пройти викторину еще раз.")
    
    async def show_guardianship_info(self, query):
        """Показать информацию о программе опеки"""
        guardianship_text = GUARDIANSHIP_INFO.format(
            email=ZOO_CONTACT_EMAIL,
            phone=ZOO_CONTACT_PHONE
        )
        
        keyboard = [
            [InlineKeyboardButton("📞 Связаться с зоопарком", callback_data="menu_contact")],
            [InlineKeyboardButton("🔙 Вернуться к началу", callback_data="menu_back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query.message:
            await query.message.edit_text(guardianship_text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await query.answer(guardianship_text)
    
    async def show_contact_info(self, query):
        """Показать контактную информацию"""
        contact_text = f"""
📞 **Свяжись с Московским зоопарком**

💌 **Email:** {ZOO_CONTACT_EMAIL}
📱 **Телефон:** {ZOO_CONTACT_PHONE}

🌐 **Веб-сайт:** https://moscowzoo.ru
📱 **Telegram-канал:** @moscowzoo

💬 **Сотрудники зоопарка готовы ответить на все твои вопросы о:**
• Программе опеки над животными
• Условиях участия
• Выборе животного для опеки
• Специальных мероприятиях

📋 **При обращении можешь упомянуть:**
• Результат прохождения викторины
• Интересующее тебя животное
• Желаемый уровень участия в программе

🕐 **Время работы:** Пн-Вс 9:00-18:00
        """
        
        keyboard = [
            [InlineKeyboardButton("🐾 Узнать о программе опеки", callback_data="menu_guardianship")],
            [InlineKeyboardButton("🔙 Вернуться к началу", callback_data="menu_back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query.message:
            await query.message.edit_text(contact_text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await query.answer(contact_text)
    
    async def handle_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик обратной связи от пользователей"""
        user = update.effective_user
        feedback_text = update.message.text
        
        # Логирование обратной связи
        logger.info(f"Feedback from {user.id} ({user.username}): {feedback_text}")
        
        # Сохранение обратной связи (в продакшене лучше использовать базу данных)
        if user.id not in user_data:
            user_data[user.id] = {}
        
        if 'feedback' not in user_data[user.id]:
            user_data[user.id]['feedback'] = []
        
        user_data[user.id]['feedback'].append({
            'text': feedback_text,
            'timestamp': datetime.now().isoformat()
        })
        
        # Ответ пользователю
        response_text = """
💬 **Спасибо за твой отзыв!**

Мы ценим твое мнение и обязательно учтем его при развитии бота.

🎯 **Что дальше?**
• Пройди викторину еще раз
• Узнай больше о программе опеки
• Свяжись с зоопарком
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 Пройти викторину", callback_data="menu_start_quiz")],
            [InlineKeyboardButton("🐾 О программе опеки", callback_data="menu_guardianship")],
            [InlineKeyboardButton("🔙 В главное меню", callback_data="menu_back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response_text, reply_markup=reply_markup, parse_mode='Markdown')
        return START
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error(f"Exception while handling an update: {context.error}")
        
        if update and update.effective_message:
            error_text = """
❌ **Произошла ошибка**

К сожалению, что-то пошло не так. Попробуй:
• Перезапустить бота командой /restart
• Обратиться к справке командой /help
• Начать заново командой /start

Если проблема повторяется, свяжись с зоопарком.
            """
            
            keyboard = [
                [InlineKeyboardButton("🔄 Перезапустить", callback_data="menu_start_quiz")],
                [InlineKeyboardButton("📞 Связаться с зоопарком", callback_data="menu_contact")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.effective_message.reply_text(error_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    def run(self):
        """Запуск бота"""
        logger.info("Starting bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Главная функция"""
    try:
        bot = QuizBot()
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")

if __name__ == '__main__':
    main()
