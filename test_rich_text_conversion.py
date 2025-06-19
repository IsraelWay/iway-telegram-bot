#!/usr/bin/env python3
"""
Простой тест для эндпоинта /convert-airtable-rich-text
"""

import requests
import json
import os

# Настройки
HOST = "http://localhost:5000"
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "your_token_here")

def test_rich_text_conversion():
    """Тестируем конвертацию Airtable Rich Text в HTML"""
    
    # Тестовый Rich Text контент
    test_rich_text = """# Главный заголовок

## Подзаголовок

### Подраздел

Обычный текст с переносом строки.

> Это важная цитата
> Многострочная цитата

Список дел:
- Первая задача
- Вторая задача
* Альтернативный маркер

Нумерованный план:
1. Этап первый
2. Этап второй
3. Финал

Код в тексте: `console.log("hello")`

Блок кода:
```
function example() {
    return "Rich Text works!";
}
```

Конец документа."""

    data = {
        "rich_text": test_rich_text
    }

    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    print("🧪 Тестируем конвертацию Rich Text в HTML...")
    print("\n📝 Исходный Rich Text:")
    print("-" * 50)
    print(test_rich_text)
    print("-" * 50)

    try:
        response = requests.post(
            f"{HOST}/convert-airtable-rich-text",
            headers=headers,
            json=data
        )
        
        print(f"\n📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('result'):
                html = result['payload']['html']
                print("\n✅ Конвертация успешна!")
                print("\n🌐 Результирующий HTML:")
                print("-" * 50)
                print(html)
                print("-" * 50)
                
                # Сохраняем в файл для просмотра
                with open('test_output.html', 'w', encoding='utf-8') as f:
                    f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Тест Rich Text конвертации</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        blockquote {{ border-left: 4px solid #ccc; padding-left: 16px; margin: 16px 0; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 16px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
{html}
</body>
</html>""")
                
                print("\n📄 HTML сохранен в файл test_output.html")
                
            else:
                print(f"\n❌ Ошибка: {result.get('message')}")
        else:
            print(f"\n❌ HTTP ошибка: {response.text}")

    except requests.exceptions.ConnectionError:
        print(f"\n❌ Не удается подключиться к {HOST}")
        print("Убедитесь что Flask сервер запущен")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")

def test_empty_input():
    """Тестируем пустой ввод"""
    
    data = {"rich_text": ""}
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    print("\n🧪 Тестируем пустой ввод...")
    
    try:
        response = requests.post(
            f"{HOST}/convert-airtable-rich-text",
            headers=headers,
            json=data
        )
        
        result = response.json()
        
        if not result.get('result'):
            print("✅ Правильно обработан пустой ввод")
            print(f"📝 Сообщение: {result.get('message')}")
        else:
            print("❌ Пустой ввод должен возвращать ошибку")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    if AUTH_TOKEN == "your_token_here":
        print("⚠️  Установите переменную окружения AUTH_TOKEN")
        print("Или замените значение в скрипте")
    else:
        test_rich_text_conversion()
        test_empty_input()
        print("\n�� Тесты завершены!") 