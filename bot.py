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
        logger.info("Creating bot application...")
        logger.info(f"Bot token length: {len(BOT_TOKEN)}")
        logger.info(f"Bot token starts with: {BOT_TOKEN[:20]}...")
        self.application = Application.builder().token(BOT_TOKEN).build()
        logger.info("Bot application created")
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        logger.info("Setting up bot handlers...")
        
        # Основные команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        logger.info("Added start command handler")
        self.application.add_handler(CommandHandler("help", self.help_command))
        logger.info("Added help command handler")
        self.application.add_handler(CommandHandler("restart", self.restart_command))
        logger.info("Added restart command handler")
        
        # Обработчики викторины
        self.application.add_handler(CallbackQueryHandler(self.handle_quiz_answer, pattern="^answer_"))
        logger.info("Added quiz answer handler")
        self.application.add_handler(CallbackQueryHandler(self.handle_menu_action, pattern="^menu_"))
        logger.info("Added menu action handler")
        
        # Обработчик обратной связи
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_feedback))
        logger.info("Added feedback handler")
        
        # Обработчик ошибок
        self.application.add_error_handler(self.error_handler)
        logger.info("Added error handler")
        
        logger.info("Bot handlers setup completed")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        logger.info(f"Start command from user {user.id} ({user.username})")
        
        # Инициализация данных пользователя
        user_id = user.id
        user_data[user_id] = {
            'current_question': 0,
            'answers': {},
            'start_time': datetime.now().isoformat(),
            'quiz_completed': False
        }
        logger.info(f"User data initialized for user {user_id}")
        
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
        user = update.effective_user
        logger.info(f"Help command from user {user.id} ({user.username})")
        
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
        logger.info(f"Restart command from user {user_id}")
        
        # Сброс данных пользователя
        if user_id in user_data:
            user_data[user_id] = {
                'current_question': 0,
                'answers': {},
                'start_time': datetime.now().isoformat(),
                'quiz_completed': False
            }
            logger.info(f"User data reset for user {user_id}")
        
        await self.start_command(update, context)
        return START
    
    async def handle_menu_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик действий в главном меню"""
        query = update.callback_query
        await query.answer()
        
        # Логирование для отладки
        logger.info(f"Menu action received: {query.data}")
        
        try:
            action = query.data.split('_', 1)[1]
            logger.info(f"Parsed action: {action}")
            
            if action == "start_quiz":
                logger.info("Starting quiz...")
                await self.start_quiz(query)
            elif action == "guardianship":
                logger.info("Showing guardianship info...")
                await self.show_guardianship_info(query)
            elif action == "contact":
                logger.info("Showing contact info...")
                await self.show_contact_info(query)
            elif action == "back_to_start":
                logger.info("Going back to start...")
                await self.show_start_menu(query)
            elif action == "share_result":
                logger.info("Sharing result...")
                await self.show_share_result(query)
            else:
                logger.warning(f"Unknown action: {action}")
                await query.answer(f"Неизвестное действие: {action}")
        except Exception as e:
            logger.error(f"Error in handle_menu_action: {e}")
            await query.answer("Произошла ошибка при обработке действия")
    
    async def start_quiz(self, query):
        """Начало викторины"""
        user_id = query.from_user.id
        logger.info(f"Starting quiz for user {user_id}")
        
        # Сброс данных для новой викторины
        user_data[user_id] = {
            'current_question': 0,
            'answers': {},
            'start_time': datetime.now().isoformat(),
            'quiz_completed': False
        }
        
        logger.info(f"User data reset for user {user_id}")
        logger.info(f"User data: {user_data[user_id]}")
        await self.show_question(query, user_id)
    
    async def show_question(self, query, user_id: int):
        """Показать текущий вопрос викторины"""
        current_q = user_data[user_id]['current_question']
        logger.info(f"Showing question {current_q + 1} for user {user_id}")
        
        if current_q >= len(QUIZ_QUESTIONS):
            logger.info(f"Quiz completed for user {user_id}, showing results")
            await self.show_results(query, user_id)
            return
        
        question_data = QUIZ_QUESTIONS[current_q]
        logger.info(f"Question data: {question_data['question'][:50]}...")
        question_text = f"❓ **Вопрос {current_q + 1} из {len(QUIZ_QUESTIONS)}**\n\n{question_data['question']}"
        
        # Создание клавиатуры с вариантами ответов
        keyboard = []
        for i, option in enumerate(question_data['options']):
            keyboard.append([InlineKeyboardButton(
                option['text'], 
                callback_data=f"answer_{current_q}_{i}"
            )])
            logger.info(f"Added option {i}: {option['text'][:30]}...")
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        logger.info(f"Created keyboard with {len(keyboard)} options")
        
        try:
            if query.message:
                await query.message.edit_text(question_text, reply_markup=reply_markup, parse_mode='Markdown')
                logger.info(f"Question {current_q + 1} displayed for user {user_id}")
            else:
                await query.answer(question_text)
                logger.info(f"Question {current_q + 1} answered for user {user_id}")
        except Exception as e:
            logger.error(f"Error showing question {current_q + 1} for user {user_id}: {e}")
            await query.answer("Произошла ошибка при показе вопроса")
    
    async def handle_quiz_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ответов на вопросы викторины"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        logger.info(f"Quiz answer from user {user_id}: {query.data}")
        
        try:
            _, question_id, answer_id = query.data.split('_')
            question_id, answer_id = int(question_id), int(answer_id)
            logger.info(f"Parsed answer: question {question_id}, option {answer_id}")
            
            # Сохранение ответа
            if user_id not in user_data:
                user_data[user_id] = {
                    'current_question': 0,
                    'answers': {},
                    'start_time': datetime.now().isoformat(),
                    'quiz_completed': False
                }
                logger.info(f"User data initialized for user {user_id}")
            
            user_data[user_id]['answers'][question_id] = answer_id
            user_data[user_id]['current_question'] = question_id + 1
            logger.info(f"Answer saved for user {user_id}, current question: {user_data[user_id]['current_question']}")
            
            # Показ следующего вопроса или результатов
            if user_data[user_id]['current_question'] < len(QUIZ_QUESTIONS):
                await self.show_question(query, user_id)
            else:
                logger.info(f"Quiz completed for user {user_id}, showing results")
                await self.show_results(query, user_id)
        except Exception as e:
            logger.error(f"Error handling quiz answer for user {user_id}: {e}")
            await query.answer("Произошла ошибка при обработке ответа")
    
    async def show_results(self, query, user_id: int):
        """Показать результаты викторины"""
        logger.info(f"Showing results for user {user_id}")
        
        if user_id not in user_data or not user_data[user_id]['answers']:
            logger.warning(f"No user data or answers for user {user_id}")
            await query.message.edit_text("❌ Произошла ошибка. Попробуйте начать викторину заново.")
            return
        
        # Подсчет результатов
        animal_scores = {}
        logger.info(f"Calculating results for user {user_id}")
        logger.info(f"User answers: {user_data[user_id]['answers']}")
        
        for question_id, answer_id in user_data[user_id]['answers'].items():
            question = QUIZ_QUESTIONS[question_id]
            option = question['options'][answer_id]
            logger.info(f"Question {question_id}, answer {answer_id}: {option['text'][:30]}...")
            
            for animal, weight in option['weight'].items():
                if animal not in animal_scores:
                    animal_scores[animal] = 0
                animal_scores[animal] += weight
                logger.info(f"Added {weight} points for {animal}, total: {animal_scores[animal]}")
        
        logger.info(f"Final animal scores: {animal_scores}")
        
        # Определение победителя
        if animal_scores:
            winner_animal = max(animal_scores, key=animal_scores.get)
            animal_info = ANIMALS[winner_animal]
            logger.info(f"Winner animal for user {user_id}: {winner_animal} with {animal_scores[winner_animal]} points")
            
            # Отметка завершения викторины
            user_data[user_id]['quiz_completed'] = True
            user_data[user_id]['result_animal'] = winner_animal
            user_data[user_id]['completion_time'] = datetime.now().isoformat()
            logger.info(f"Quiz completed for user {user_id}, result saved")
            
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
            
            logger.info(f"Showing results for user {user_id}: {animal_info['name']}")
            try:
                await query.message.edit_text(result_text, reply_markup=reply_markup, parse_mode='Markdown')
                logger.info(f"Results displayed for user {user_id}")
            except Exception as e:
                logger.error(f"Error displaying results for user {user_id}: {e}")
                await query.answer("Произошла ошибка при показе результатов")
        else:
            logger.warning(f"No animal scores for user {user_id}")
            await query.message.edit_text("❌ Не удалось определить результат. Попробуйте пройти викторину еще раз.")
    
    async def show_start_menu(self, query):
        """Показать главное меню (для callback queries)"""
        user = query.from_user
        user_id = user.id
        logger.info(f"Showing start menu for user {user_id}")
        
        # Инициализация данных пользователя
        user_data[user_id] = {
            'current_question': 0,
            'answers': {},
            'start_time': datetime.now().isoformat(),
            'quiz_completed': False
        }
        logger.info(f"User data initialized for user {user_id}")
        
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
        
        try:
            await query.message.edit_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
            logger.info(f"Start menu displayed for user {user_id}")
        except Exception as e:
            logger.error(f"Error showing start menu for user {user_id}: {e}")
            await query.answer("Произошла ошибка при показе главного меню")
    
    async def show_guardianship_info(self, query):
        """Показать информацию о программе опеки"""
        user_id = query.from_user.id
        logger.info(f"Showing guardianship info for user {user_id}")
        
        guardianship_text = GUARDIANSHIP_INFO.format(
            email=ZOO_CONTACT_EMAIL,
            phone=ZOO_CONTACT_PHONE
        )
        
        keyboard = [
            [InlineKeyboardButton("📞 Связаться с зоопарком", callback_data="menu_contact")],
            [InlineKeyboardButton("🔙 Вернуться к началу", callback_data="menu_back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            if query.message:
                await query.message.edit_text(guardianship_text, reply_markup=reply_markup, parse_mode=None)
                logger.info(f"Guardianship info displayed for user {user_id}")
            else:
                await query.answer(guardianship_text)
                logger.info(f"Guardianship info answered for user {user_id}")
        except Exception as e:
            logger.error(f"Error showing guardianship info for user {user_id}: {e}")
            await query.answer("Произошла ошибка при показе информации о программе опеки")
    
    async def show_contact_info(self, query):
        """Показать контактную информацию"""
        user_id = query.from_user.id
        logger.info(f"Showing contact info for user {user_id}")
        
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
        
        try:
            if query.message:
                await query.message.edit_text(contact_text, reply_markup=reply_markup, parse_mode=None)
                logger.info(f"Contact info displayed for user {user_id}")
            else:
                await query.answer(contact_text)
                logger.info(f"Contact info answered for user {user_id}")
        except Exception as e:
            logger.error(f"Error showing contact info for user {user_id}: {e}")
            await query.answer("Произошла ошибка при показе контактной информации")
    
    async def show_share_result(self, query):
        """Показать информацию о том, как поделиться результатом"""
        user_id = query.from_user.id
        logger.info(f"Showing share result info for user {user_id}")
        
        # Проверяем, есть ли результат викторины
        if user_id not in user_data or not user_data[user_id].get('quiz_completed'):
            share_text = """
❌ **Нет результата для публикации**

Сначала пройди викторину, чтобы узнать свое тотемное животное!

🎯 **Что делать:**
• Нажми "Начать викторину"
• Ответь на все вопросы
• Узнай свое тотемное животное
• Тогда сможешь поделиться результатом
            """
        else:
            animal_name = user_data[user_id].get('result_animal', 'неизвестное животное')
            animal_info = ANIMALS.get(animal_name, {})
            animal_emoji = animal_info.get('emoji', '🐾')
            animal_display_name = animal_info.get('name', animal_name)
            
            share_text = f"""
📤 **Поделись своим результатом!**

{animal_emoji} **Твое тотемное животное: {animal_display_name}** {animal_emoji}

💬 **Как поделиться:**
• Скопируй текст ниже
• Вставь в любой мессенджер или соцсеть
• Добавь ссылку на бота: @your_bot_username

📝 **Текст для публикации:**
"Я прошел викторину Московского зоопарка и узнал, что мое тотемное животное - {animal_display_name}! {animal_emoji}

Попробуй и ты: @your_bot_username"

🌍 **Где поделиться:**
• Telegram
• WhatsApp
• Instagram
• Facebook
• ВКонтакте
            """
        
        keyboard = [
            [InlineKeyboardButton("🔄 Пройти викторину еще раз", callback_data="menu_start_quiz")],
            [InlineKeyboardButton("🐾 О программе опеки", callback_data="menu_guardianship")],
            [InlineKeyboardButton("🔙 Вернуться к началу", callback_data="menu_back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.message.edit_text(share_text, reply_markup=reply_markup, parse_mode='Markdown')
            logger.info(f"Share result info displayed for user {user_id}")
        except Exception as e:
            logger.error(f"Error showing share result info for user {user_id}: {e}")
            await query.answer("Произошла ошибка при показе информации о публикации")
    
    async def handle_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик обратной связи от пользователей"""
        user = update.effective_user
        feedback_text = update.message.text
        
        # Логирование обратной связи
        logger.info(f"Feedback from {user.id} ({user.username}): {feedback_text}")
        logger.info(f"Feedback text: {feedback_text[:100]}...")
        
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
        
        if update and update.effective_user:
            user_id = update.effective_user.id
            logger.error(f"Error occurred for user {user_id}")
        
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
            
            try:
                await update.effective_message.reply_text(error_text, reply_markup=reply_markup, parse_mode='Markdown')
                logger.info("Error message sent to user")
            except Exception as e:
                logger.error(f"Failed to send error message: {e}")
        elif update and update.callback_query:
            logger.error("Error occurred in callback query")
            try:
                await update.callback_query.answer("Произошла ошибка. Попробуйте еще раз.")
            except Exception as e:
                logger.error(f"Failed to send error callback answer: {e}")
    
    def run(self):
        """Запуск бота"""
        logger.info("Starting bot...")
        logger.info(f"Bot token: {BOT_TOKEN[:10]}...")
        logger.info(f"Quiz questions count: {len(QUIZ_QUESTIONS)}")
        logger.info(f"Animals count: {len(ANIMALS)}")
        logger.info("Starting polling...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Главная функция"""
    try:
        logger.info("Initializing bot...")
        logger.info(f"Python version: {__import__('sys').version}")
        logger.info(f"Working directory: {__import__('os').getcwd()}")
        bot = QuizBot()
        logger.info("Bot initialized successfully")
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == '__main__':
    main()
