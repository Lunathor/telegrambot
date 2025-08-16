"""
Демонстрационный скрипт для показа работы бота
Запускает викторину в консольном режиме
"""

import json
from datetime import datetime
from quiz_data import QUIZ_QUESTIONS, ANIMALS, GUARDIANSHIP_INFO

def print_header():
    """Вывод заголовка демонстрации"""
    print("=" * 60)
    print("🦁 ДЕМОНСТРАЦИЯ БОТА 'КАКОЕ У ВАС ТОТЕМНОЕ ЖИВОТНОЕ?' 🦁")
    print("=" * 60)
    print("Этот скрипт демонстрирует логику работы Telegram-бота")
    print("без необходимости его запуска в Telegram.")
    print()

def simulate_quiz():
    """Симуляция прохождения викторины"""
    print("🎮 СИМУЛЯЦИЯ ВИКТОРИНЫ")
    print("-" * 40)
    
    # Данные пользователя
    user_data = {
        'current_question': 0,
        'answers': {},
        'start_time': datetime.now().isoformat(),
        'quiz_completed': False
    }
    
    print(f"Привет! Давайте пройдем викторину из {len(QUIZ_QUESTIONS)} вопросов.")
    print("Отвечай на вопросы, выбирая номер варианта ответа (1-4).")
    print()
    
    # Прохождение вопросов
    for i, question in enumerate(QUIZ_QUESTIONS):
        print(f"❓ Вопрос {i + 1} из {len(QUIZ_QUESTIONS)}")
        print(f"   {question['question']}")
        print()
        
        # Показ вариантов ответов
        for j, option in enumerate(question['options']):
            print(f"   {j + 1}. {option['text']}")
        print()
        
        # Получение ответа (в демо используем первый вариант)
        answer_id = 0  # В реальном боте это выбор пользователя
        user_data['answers'][i] = answer_id
        
        print(f"✅ Выбран ответ: {answer_id + 1}")
        print(f"   {question['options'][answer_id]['text']}")
        print("-" * 40)
        print()
    
    return user_data

def calculate_results(user_data):
    """Подсчет результатов викторины"""
    print("🎯 ПОДСЧЕТ РЕЗУЛЬТАТОВ")
    print("-" * 40)
    
    # Подсчет баллов
    animal_scores = {}
    for question_id, answer_id in user_data['answers'].items():
        question = QUIZ_QUESTIONS[question_id]
        option = question['options'][answer_id]
        
        print(f"Вопрос {question_id + 1}: {option['text']}")
        
        for animal, weight in option['weight'].items():
            if animal not in animal_scores:
                animal_scores[animal] = 0
            animal_scores[animal] += weight
            print(f"  +{weight} балл для {ANIMALS[animal]['name']} ({animal})")
        print()
    
    # Определение победителя
    if animal_scores:
        winner_animal = max(animal_scores, key=animal_scores.get)
        animal_info = ANIMALS[winner_animal]
        
        print("🏆 РЕЗУЛЬТАТ ВИКТОРИНЫ")
        print("=" * 40)
        print(f"{animal_info['emoji']} Твое тотемное животное: {animal_info['name']} {animal_info['emoji']}")
        print()
        print("📝 Описание:")
        print(f"   {animal_info['description']}")
        print()
        print("🐾 Интересные факты:")
        print(f"   {animal_info['zoo_facts']}")
        print()
        print("💝 О программе опеки:")
        print(f"   {animal_info['guardian_info']}")
        print()
        
        # Показ всех баллов
        print("📊 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
        sorted_animals = sorted(animal_scores.items(), key=lambda x: x[1], reverse=True)
        for animal_key, score in sorted_animals:
            animal_name = ANIMALS[animal_key]['name']
            emoji = ANIMALS[animal_key]['emoji']
            print(f"   {emoji} {animal_name}: {score} баллов")
        
        return winner_animal
    else:
        print("❌ Не удалось определить результат")
        return None

def show_guardianship_info():
    """Показ информации о программе опеки"""
    print()
    print("🐾 ПРОГРАММА ОПЕКИ НАД ЖИВОТНЫМИ")
    print("=" * 50)
    
    # Форматируем информацию с реальными контактами
    guardianship_text = GUARDIANSHIP_INFO.format(
        email="contact@moscowzoo.ru",
        phone="+7(495)123-45-67"
    )
    
    print(guardianship_text)

def show_technical_details():
    """Показ технических деталей бота"""
    print()
    print("🔧 ТЕХНИЧЕСКИЕ ДЕТАЛИ БОТА")
    print("=" * 40)
    
    print(f"📊 Количество вопросов: {len(QUIZ_QUESTIONS)}")
    print(f"🐾 Количество животных: {len(ANIMALS)}")
    print(f"⏱️  Время прохождения: ~{len(QUIZ_QUESTIONS) * 30} секунд")
    print()
    
    print("📱 Основные команды бота:")
    print("   /start - Начать викторину")
    print("   /restart - Перезапустить викторину")
    print("   /help - Показать справку")
    print()
    
    print("🎯 Алгоритм определения тотемного животного:")
    print("   1. Система взвешивания ответов (1-3 балла)")
    print("   2. Подсчет баллов для каждого животного")
    print("   3. Выбор животного с максимальным количеством баллов")
    print()
    
    print("🖼️  Генерация изображений:")
    print("   - Детальное изображение с результатом")
    print("   - Квадратное изображение для соцсетей")
    print("   - Автоматическое форматирование текста")

def main():
    """Главная функция демонстрации"""
    print_header()
    
    # Симуляция викторины
    user_data = simulate_quiz()
    
    # Подсчет результатов
    winner = calculate_results(user_data)
    
    # Показ информации об опеке
    show_guardianship_info()
    
    # Показ технических деталей
    show_technical_details()
    
    print()
    print("=" * 60)
    print("🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    print("=" * 60)
    print()
    print("📱 Для запуска реального бота:")
    print("   1. Получите токен у @BotFather")
    print("   2. Создайте файл .env с токеном")
    print("   3. Запустите: python bot.py")
    print()
    print("🔗 Документация:")
    print("   - README.md - Основная документация")
    print("   - DEPLOYMENT.md - Инструкции по развертыванию")
    print("   - test_bot.py - Тесты функциональности")
    print()
    print("🌟 Спасибо за внимание к проекту!")

if __name__ == '__main__':
    main()
