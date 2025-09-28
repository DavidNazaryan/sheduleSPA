#!/usr/bin/env python3
"""
Тестовый скрипт для проверки аутентификации через Telegram
"""

import requests
import json
import urllib.parse

def test_telegram_auth():
    """Тестирует аутентификацию через Telegram"""
    
    # Тестовые данные (замените на реальные данные от Telegram)
    test_init_data = "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22Test%22%2C%22last_name%22%3A%22User%22%2C%22username%22%3A%22testuser%22%7D&auth_date=1234567890&hash=test_hash"
    
    print("🧪 Тестирование аутентификации через Telegram")
    print("=" * 50)
    
    # Тестируем локальный сервер
    print("\n1. Тестируем локальный сервер...")
    try:
        response = requests.post(
            "http://localhost:8000/api/auth/telegram",
            data={
                "init_data": test_init_data,
                "group_id": "test-group"
            }
        )
        
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Локальная аутентификация работает!")
        else:
            print("❌ Ошибка локальной аутентификации")
            
    except Exception as e:
        print(f"❌ Ошибка подключения к локальному серверу: {e}")
    
    # Тестируем удаленный сервер
    print("\n2. Тестируем удаленный сервер...")
    try:
        response = requests.post(
            "https://vm-fc7b7f29.na4u.ru/api/auth/telegram",
            data={
                "init_data": test_init_data,
                "group_id": "test-group"
            }
        )
        
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Удаленная аутентификация работает!")
        else:
            print("❌ Ошибка удаленной аутентификации")
            
    except Exception as e:
        print(f"❌ Ошибка подключения к удаленному серверу: {e}")

def test_webhook():
    """Тестирует webhook"""
    
    print("\n3. Тестируем webhook...")
    
    # Тестовые данные webhook от Telegram
    test_webhook_data = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Test",
                "last_name": "User",
                "username": "testuser"
            },
            "chat": {
                "id": 123456789,
                "first_name": "Test",
                "last_name": "User",
                "username": "testuser",
                "type": "private"
            },
            "date": 1234567890,
            "text": "/start"
        }
    }
    
    try:
        response = requests.post(
            "https://vm-fc7b7f29.na4u.ru/webhook",
            json=test_webhook_data
        )
        
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Webhook работает!")
        else:
            print("❌ Ошибка webhook")
            
    except Exception as e:
        print(f"❌ Ошибка подключения к webhook: {e}")

def test_api_endpoints():
    """Тестирует API endpoints"""
    
    print("\n4. Тестируем API endpoints...")
    
    endpoints = [
        "/api/options/faculties",
        "/api/options/courses?faculty=5",
        "/api/options/groups?faculty=5&course=1",
        "/api/schedule?faculty=5&course=1&group=1"
    ]
    
    base_url = "https://vm-fc7b7f29.na4u.ru"
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

if __name__ == "__main__":
    print("🔍 Полное тестирование системы")
    print("=" * 50)
    
    test_telegram_auth()
    test_webhook()
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("📋 Результаты тестирования:")
    print("1. Проверьте результаты выше")
    print("2. Если есть ошибки, проверьте логи сервера")
    print("3. Убедитесь, что сервер запущен на вашем домене")
    print("4. Протестируйте в Telegram боте: https://t.me/scheduleSPAbot")