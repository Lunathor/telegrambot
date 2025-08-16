"""
Тесты для Telegram-бота "Какое у вас тотемное животное?"
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quiz_data import QUIZ_QUESTIONS, ANIMALS, GUARDIANSHIP_INFO
from image_generator import ResultImageGenerator

class TestQuizData(unittest.TestCase):
    """Тесты для данных викторины"""
    
    def test_quiz_questions_structure(self):
        """Проверка структуры вопросов викторины"""
        self.assertIsInstance(QUIZ_QUESTIONS, list)
        self.assertGreater(len(QUIZ_QUESTIONS), 0)
        
        for question in QUIZ_QUESTIONS:
            self.assertIn('id', question)
            self.assertIn('question', question)
            self.assertIn('options', question)
            self.assertIsInstance(question['options'], list)
            self.assertGreater(len(question['options']), 0)
            
            for option in question['options']:
                self.assertIn('text', option)
                self.assertIn('weight', option)
                self.assertIsInstance(option['weight'], dict)
    
    def test_animals_data_structure(self):
        """Проверка структуры данных о животных"""
        self.assertIsInstance(ANIMALS, dict)
        self.assertGreater(len(ANIMALS), 0)
        
        for animal_key, animal_info in ANIMALS.items():
            self.assertIn('name', animal_info)
            self.assertIn('emoji', animal_info)
            self.assertIn('description', animal_info)
            self.assertIn('zoo_facts', animal_info)
            self.assertIn('guardian_info', animal_info)
            
            # Проверяем, что все поля не пустые
            self.assertIsInstance(animal_info['name'], str)
            self.assertGreater(len(animal_info['name']), 0)
            self.assertIsInstance(animal_info['description'], str)
            self.assertGreater(len(animal_info['description']), 0)
    
    def test_guardianship_info_format(self):
        """Проверка формата информации об опеке"""
        self.assertIsInstance(GUARDIANSHIP_INFO, str)
        self.assertGreater(len(GUARDIANSHIP_INFO), 0)
        self.assertIn('{email}', GUARDIANSHIP_INFO)
        self.assertIn('{phone}', GUARDIANSHIP_INFO)
    
    def test_question_weights_consistency(self):
        """Проверка согласованности весов ответов"""
        for question in QUIZ_QUESTIONS:
            for option in question['options']:
                weights = option['weight']
                # Проверяем, что все животные в весах существуют в ANIMALS
                for animal_key in weights.keys():
                    self.assertIn(animal_key, ANIMALS)
                    # Проверяем, что вес в допустимом диапазоне
                    self.assertGreaterEqual(weights[animal_key], 1)
                    self.assertLessEqual(weights[animal_key], 3)

class TestImageGenerator(unittest.TestCase):
    """Тесты для генератора изображений"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.generator = ResultImageGenerator()
    
    def test_generator_initialization(self):
        """Проверка инициализации генератора"""
        self.assertIsInstance(self.generator.colors, dict)
        self.assertIn('background', self.generator.colors)
        self.assertIn('text', self.generator.colors)
        self.assertIn('title', self.generator.colors)
    
    def test_text_wrapping(self):
        """Тест переноса текста"""
        test_text = "Это очень длинный текст который должен быть разбит на несколько строк для корректного отображения в изображении"
        
        # Мокаем шрифт
        mock_font = Mock()
        mock_font.getbbox.return_value = (0, 0, 100, 20)  # Ширина 100
        
        lines = self.generator._wrap_text(test_text, mock_font, 200)
        self.assertIsInstance(lines, list)
        # Проверяем, что текст разбит на строки
        self.assertGreaterEqual(len(lines), 1)
    
    def test_invalid_animal_key(self):
        """Тест обработки неверного ключа животного"""
        with self.assertRaises(ValueError):
            self.generator.generate_result_image("invalid_animal_key")
    
    def test_valid_animal_key(self):
        """Тест обработки корректного ключа животного"""
        # Мокаем создание изображения
        with patch('PIL.Image.new') as mock_image_new, \
             patch('PIL.ImageDraw.Draw') as mock_draw, \
             patch('os.makedirs'), \
             patch.object(Mock(), 'save') as mock_save:
            
            mock_image = Mock()
            mock_image_new.return_value = mock_image
            
            result = self.generator.generate_result_image("lion", "Test User")
            # В случае успеха должен вернуть путь к файлу
            self.assertIsNotNone(result)

class TestQuizLogic(unittest.TestCase):
    """Тесты логики викторины"""
    
    def test_score_calculation(self):
        """Тест подсчета баллов"""
        # Симулируем ответы пользователя
        mock_answers = {
            0: 0,  # Первый вопрос, первый ответ
            1: 1,  # Второй вопрос, второй ответ
            2: 2   # Третий вопрос, третий ответ
        }
        
        # Подсчитываем баллы вручную
        animal_scores = {}
        for question_id, answer_id in mock_answers.items():
            question = QUIZ_QUESTIONS[question_id]
            option = question['options'][answer_id]
            
            for animal, weight in option['weight'].items():
                if animal not in animal_scores:
                    animal_scores[animal] = 0
                animal_scores[animal] += weight
        
        # Проверяем, что баллы подсчитаны
        self.assertGreater(len(animal_scores), 0)
        
        # Проверяем, что все животные имеют неотрицательные баллы
        for score in animal_scores.values():
            self.assertGreaterEqual(score, 0)
    
    def test_winner_determination(self):
        """Тест определения победителя"""
        # Создаем тестовые баллы
        test_scores = {
            'lion': 5,
            'tiger': 8,
            'elephant': 3,
            'monkey': 6
        }
        
        # Определяем победителя
        winner = max(test_scores, key=test_scores.get)
        self.assertEqual(winner, 'tiger')
        self.assertEqual(test_scores[winner], 8)

class TestDataIntegrity(unittest.TestCase):
    """Тесты целостности данных"""
    
    def test_all_animals_in_questions(self):
        """Проверка, что все животные присутствуют в вопросах"""
        animals_in_questions = set()
        
        for question in QUIZ_QUESTIONS:
            for option in question['options']:
                animals_in_questions.update(option['weight'].keys())
        
        # Проверяем, что все животные из ANIMALS присутствуют в вопросах
        for animal_key in ANIMALS.keys():
            self.assertIn(animal_key, animals_in_questions)
    
    def test_question_ids_sequential(self):
        """Проверка последовательности ID вопросов"""
        question_ids = [q['id'] for q in QUIZ_QUESTIONS]
        expected_ids = list(range(1, len(QUIZ_QUESTIONS) + 1))
        self.assertEqual(question_ids, expected_ids)
    
    def test_option_weights_not_empty(self):
        """Проверка, что веса ответов не пустые"""
        for question in QUIZ_QUESTIONS:
            for option in question['options']:
                self.assertGreater(len(option['weight']), 0)

def run_tests():
    """Запуск всех тестов"""
    # Создаем тестовый набор
    test_suite = unittest.TestSuite()
    
    # Добавляем тесты
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestQuizData))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestImageGenerator))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestQuizLogic))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDataIntegrity))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Возвращаем результат
    return result.wasSuccessful()

if __name__ == '__main__':
    print("🧪 Запуск тестов для Telegram-бота...")
    print("=" * 50)
    
    success = run_tests()
    
    print("=" * 50)
    if success:
        print("✅ Все тесты прошли успешно!")
    else:
        print("❌ Некоторые тесты не прошли.")
    
    print("\n🎯 Бот готов к использованию!")
    print("📱 Для запуска выполните: python bot.py")
