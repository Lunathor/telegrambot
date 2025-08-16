"""
Модуль для генерации изображений с результатами викторины
"""

from PIL import Image, ImageDraw, ImageFont
import os
from typing import Dict, Any
from quiz_data import ANIMALS

class ResultImageGenerator:
    def __init__(self):
        self.font_path = "arial.ttf"  # В продакшене лучше использовать системные шрифты
        self.default_font_size = 24
        self.title_font_size = 36
        self.subtitle_font_size = 28
        
        # Цвета для оформления
        self.colors = {
            'background': (255, 255, 255),
            'text': (0, 0, 0),
            'title': (34, 139, 34),
            'subtitle': (70, 130, 180),
            'accent': (255, 140, 0)
        }
    
    def generate_result_image(self, animal_key: str, user_name: str = "Пользователь") -> str:
        """
        Генерирует изображение с результатом викторины
        
        Args:
            animal_key: Ключ животного из ANIMALS
            user_name: Имя пользователя
            
        Returns:
            Путь к сгенерированному изображению
        """
        if animal_key not in ANIMALS:
            raise ValueError(f"Unknown animal: {animal_key}")
        
        animal_info = ANIMALS[animal_key]
        
        # Создание изображения
        img_width = 800
        img_height = 1000
        
        # Создаем новое изображение
        img = Image.new('RGB', (img_width, img_height), self.colors['background'])
        draw = ImageDraw.Draw(img)
        
        try:
            # Загружаем шрифты (используем стандартные, если custom не найден)
            try:
                title_font = ImageFont.truetype(self.font_path, self.title_font_size)
                subtitle_font = ImageFont.truetype(self.font_path, self.subtitle_font_size)
                body_font = ImageFont.truetype(self.font_path, self.default_font_size)
            except:
                # Fallback на стандартные шрифты
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                body_font = ImageFont.load_default()
            
            # Заголовок
            title_text = f"Твое тотемное животное:"
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (img_width - title_width) // 2
            draw.text((title_x, 50), title_text, font=title_font, fill=self.colors['title'])
            
            # Название животного с эмодзи
            animal_title = f"{animal_info['emoji']} {animal_info['name']} {animal_info['emoji']}"
            animal_bbox = draw.textbbox((0, 0), animal_title, font=subtitle_font)
            animal_width = animal_bbox[2] - animal_bbox[0]
            animal_x = (img_width - animal_width) // 2
            draw.text((animal_x, 120), animal_title, font=subtitle_font, fill=self.colors['subtitle'])
            
            # Описание животного
            description = animal_info['description']
            description_lines = self._wrap_text(description, body_font, img_width - 100)
            
            y_position = 200
            for line in description_lines:
                draw.text((50, y_position), line, font=body_font, fill=self.colors['text'])
                y_position += 30
            
            # Интересные факты
            y_position += 20
            facts_title = "🐾 Интересные факты:"
            draw.text((50, y_position), facts_title, font=subtitle_font, fill=self.colors['accent'])
            y_position += 40
            
            facts = animal_info['zoo_facts']
            facts_lines = self._wrap_text(facts, body_font, img_width - 100)
            
            for line in facts_lines:
                draw.text((50, y_position), line, font=body_font, fill=self.colors['text'])
                y_position += 25
            
            # Информация об опеке
            y_position += 20
            guardian_title = "💝 О программе опеки:"
            draw.text((50, y_position), guardian_title, font=subtitle_font, fill=self.colors['accent'])
            y_position += 40
            
            guardian_info = animal_info['guardian_info']
            guardian_lines = self._wrap_text(guardian_info, body_font, img_width - 100)
            
            for line in guardian_lines:
                draw.text((50, y_position), line, font=body_font, fill=self.colors['text'])
                y_position += 25
            
            # Подпись
            y_position += 30
            signature = f"Сгенерировано для {user_name}"
            signature_bbox = draw.textbbox((0, 0), signature, font=body_font)
            signature_width = signature_bbox[2] - signature_bbox[0]
            signature_x = (img_width - signature_width) // 2
            draw.text((signature_x, y_position), signature, font=body_font, fill=self.colors['subtitle'])
            
            # Логотип зоопарка (текстовый)
            y_position += 40
            logo_text = "🐾 Московский зоопарк 🐾"
            logo_bbox = draw.textbbox((0, 0), logo_text, font=body_font)
            logo_width = logo_bbox[2] - logo_bbox[0]
            logo_x = (img_width - logo_width) // 2
            draw.text((logo_x, y_position), logo_text, font=body_font, fill=self.colors['title'])
            
            # Сохранение изображения
            filename = f"result_{animal_key}_{user_name.lower().replace(' ', '_')}.png"
            filepath = os.path.join("generated_images", filename)
            
            # Создаем папку, если её нет
            os.makedirs("generated_images", exist_ok=True)
            
            img.save(filepath, "PNG")
            return filepath
            
        except Exception as e:
            print(f"Error generating image: {e}")
            # Возвращаем пустое изображение в случае ошибки
            return None
    
    def _wrap_text(self, text: str, font, max_width: int) -> list:
        """
        Разбивает текст на строки, чтобы поместиться в заданную ширину
        
        Args:
            text: Исходный текст
            font: Шрифт для измерения
            max_width: Максимальная ширина строки
            
        Returns:
            Список строк
        """
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = font.getbbox(test_line)
            line_width = bbox[2] - bbox[0]
            
            if line_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def create_shareable_image(self, animal_key: str, user_name: str = "Пользователь") -> str:
        """
        Создает изображение для публикации в социальных сетях
        
        Args:
            animal_key: Ключ животного
            user_name: Имя пользователя
            
        Returns:
            Путь к изображению
        """
        if animal_key not in ANIMALS:
            raise ValueError(f"Unknown animal: {animal_key}")
        
        animal_info = ANIMALS[animal_key]
        
        # Создание изображения для соцсетей (квадратное)
        img_size = 1080
        img = Image.new('RGB', (img_size, img_size), self.colors['background'])
        draw = ImageDraw.Draw(img)
        
        try:
            # Загружаем шрифты
            try:
                title_font = ImageFont.truetype(self.font_path, 48)
                subtitle_font = ImageFont.truetype(self.font_path, 36)
                body_font = ImageFont.truetype(self.font_path, 24)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                body_font = ImageFont.load_default()
            
            # Центральный эмодзи животного
            emoji_size = 200
            emoji_x = (img_size - emoji_size) // 2
            emoji_y = 100
            
            # Рисуем большой эмодзи (используем текст как эмодзи)
            draw.text((emoji_x, emoji_y), animal_info['emoji'], font=title_font, fill=self.colors['accent'])
            
            # Название животного
            animal_name = animal_info['name']
            name_bbox = draw.textbbox((0, 0), animal_name, font=subtitle_font)
            name_width = name_bbox[2] - name_bbox[0]
            name_x = (img_size - name_width) // 2
            draw.text((name_x, emoji_y + 120), animal_name, font=subtitle_font, fill=self.colors['title'])
            
            # Краткое описание
            description = animal_info['description'][:100] + "..." if len(animal_info['description']) > 100 else animal_info['description']
            desc_lines = self._wrap_text(description, body_font, img_size - 100)
            
            y_position = emoji_y + 200
            for line in desc_lines:
                line_bbox = draw.textbbox((0, 0), line, font=body_font)
                line_width = line_bbox[2] - line_bbox[0]
                line_x = (img_size - line_width) // 2
                draw.text((line_x, y_position), line, font=body_font, fill=self.colors['text'])
                y_position += 30
            
            # Призыв к действию
            y_position += 40
            cta_text = "🐾 Узнай больше о программе опеки!"
            cta_bbox = draw.textbbox((0, 0), cta_text, font=body_font)
            cta_width = cta_bbox[2] - cta_bbox[0]
            cta_x = (img_size - cta_width) // 2
            draw.text((cta_x, y_position), cta_text, font=body_font, fill=self.colors['accent'])
            
            # Логотип и ссылка
            y_position += 60
            logo_text = "Московский зоопарк"
            logo_bbox = draw.textbbox((0, 0), logo_text, font=body_font)
            logo_width = logo_bbox[2] - logo_bbox[0]
            logo_x = (img_size - logo_width) // 2
            draw.text((logo_x, y_position), logo_text, font=body_font, fill=self.colors['subtitle'])
            
            # Сохранение
            filename = f"share_{animal_key}_{user_name.lower().replace(' ', '_')}.png"
            filepath = os.path.join("generated_images", filename)
            
            os.makedirs("generated_images", exist_ok=True)
            img.save(filepath, "PNG")
            return filepath
            
        except Exception as e:
            print(f"Error generating shareable image: {e}")
            return None

# Пример использования
if __name__ == "__main__":
    generator = ResultImageGenerator()
    
    # Генерируем изображение для теста
    try:
        result_path = generator.generate_result_image("lion", "Тестовый пользователь")
        print(f"Generated result image: {result_path}")
        
        share_path = generator.create_shareable_image("lion", "Тестовый пользователь")
        print(f"Generated shareable image: {share_path}")
    except Exception as e:
        print(f"Error: {e}")
