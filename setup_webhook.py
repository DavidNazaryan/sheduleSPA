#!/usr/bin/env python3
"""
Скрипт для настройки webhook для Telegram бота
"""

import requests
import json
import os
from pathlib import Path

# Конфигурация
BOT_TOKEN = "8296584992:AAFmltay1-OZolKK0AoF8pdKF2kELfg4boA"

# Определяем URL webhook в зависимости от окружения
def get_webhook_url():
    """Определяет URL webhook в зависимости от окружения"""
    # Проверяем переменные окружения
    if os.getenv('PRODUCTION'):
        # Продакшен - используем домен
        domain = os.getenv('DOMAIN', 'vm-fc7b7f29.na4u.ru')
        return f"https://{domain}/webhook"
    else:
        # Локальная разработка
        return "http://localhost:8000/webhook"

WEBHOOK_URL = get_webhook_url()

def set_webhook():
    """Устанавливает webhook для бота"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    data = {"url": WEBHOOK_URL}
    
    try:
        response = requests.post(url, data=data)
        result = response.json()
        
        if result.get("ok"):
            print("✅ Webhook успешно установлен!")
            print(f"URL: {WEBHOOK_URL}")
        else:
            print("❌ Ошибка установки webhook:")
            print(result.get("description", "Неизвестная ошибка"))
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

def get_webhook_info():
    """Получает информацию о текущем webhook"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if result.get("ok"):
            webhook_info = result.get("result", {})
            print("📊 Информация о webhook:")
            print(f"URL: {webhook_info.get('url', 'Не установлен')}")
            print(f"Статус: {'Активен' if webhook_info.get('url') else 'Не установлен'}")
            print(f"Ошибки: {webhook_info.get('last_error_message', 'Нет')}")
            print(f"Количество ошибок: {webhook_info.get('last_error_count', 0)}")
            print(f"Дата последней ошибки: {webhook_info.get('last_error_date', 'Нет')}")
        else:
            print("❌ Ошибка получения информации о webhook")
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

def delete_webhook():
    """Удаляет webhook"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
    
    try:
        response = requests.post(url)
        result = response.json()
        
        if result.get("ok"):
            print("✅ Webhook удален!")
        else:
            print("❌ Ошибка удаления webhook")
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

def set_commands():
    """Устанавливает команды бота"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
    
    commands = [
        {"command": "start", "description": "🚀 Запустить бота и открыть приложение"},
        {"command": "login", "description": "🔐 Войти в приложение расписания"},
        {"command": "help", "description": "❓ Показать справку по боту"},
        {"command": "status", "description": "📊 Проверить статус бота"},
        {"command": "myinfo", "description": "👤 Показать информацию о пользователе"}
    ]
    
    data = {"commands": commands}
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get("ok"):
            print("✅ Команды бота установлены!")
            for cmd in commands:
                print(f"  - /{cmd['command']}: {cmd['description']}")
        else:
            print("❌ Ошибка установки команд")
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

def set_webapp_url():
    """Устанавливает URL WebApp для бота"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebAppUrl"
    
    # Определяем URL WebApp
    if os.getenv('PRODUCTION'):
        domain = os.getenv('DOMAIN', 'vm-fc7b7f29.na4u.ru')
        webapp_url = f"https://{domain}"
    else:
        webapp_url = "http://localhost:8000"
    
    data = {"url": webapp_url}
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get("ok"):
            print(f"✅ URL WebApp установлен: {webapp_url}")
        else:
            print("❌ Ошибка установки URL WebApp")
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

def test_bot():
    """Тестирует бота"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if result.get("ok"):
            bot_info = result.get("result", {})
            print("🤖 Информация о боте:")
            print(f"Имя: {bot_info.get('first_name', 'Неизвестно')}")
            print(f"Username: @{bot_info.get('username', 'Неизвестно')}")
            print(f"ID: {bot_info.get('id', 'Неизвестно')}")
            print(f"Может присоединяться к группам: {'Да' if bot_info.get('can_join_groups') else 'Нет'}")
            print(f"Может читать сообщения: {'Да' if bot_info.get('can_read_all_group_messages') else 'Нет'}")
            print(f"Поддерживает inline-запросы: {'Да' if bot_info.get('supports_inline_queries') else 'Нет'}")
        else:
            print("❌ Ошибка получения информации о боте")
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

if __name__ == "__main__":
    print("🤖 Настройка Telegram бота @scheduleSPAbot")
    print("=" * 50)
    
    print(f"🌐 Режим: {'Продакшен' if os.getenv('PRODUCTION') else 'Локальная разработка'}")
    print(f"🔗 Webhook URL: {WEBHOOK_URL}")
    
    print("\n1. Тестируем бота...")
    test_bot()
    
    print("\n2. Устанавливаем команды бота...")
    set_commands()
    
    print("\n3. Устанавливаем URL WebApp...")
    set_webapp_url()
    
    print("\n4. Устанавливаем webhook...")
    set_webhook()
    
    print("\n5. Проверяем статус webhook...")
    get_webhook_info()
    
    print("\n✅ Настройка завершена!")
    print("\n📋 Следующие шаги:")
    print("1. Запустите сервер: uvicorn app.main:app --reload")
    print("2. Откройте бота в Telegram: https://t.me/scheduleSPAbot")
    print("3. Отправьте команду /start")
    print("4. Нажмите кнопку 'Открыть расписание'")
    print("\n🔧 Для продакшена:")
    print("1. Установите переменную окружения PRODUCTION=1")
    print("2. Установите переменную окружения DOMAIN=yourdomain.com")
    print("3. Запустите скрипт снова")

