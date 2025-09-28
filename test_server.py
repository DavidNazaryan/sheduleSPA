#!/usr/bin/env python3
"""
Скрипт для проверки доступности сервера
"""

import requests
import time

def test_server():
    """Проверяет доступность сервера"""
    url = "https://vm-fc7b7f29.na4u.ru"
    
    print(f"🔍 Проверяем доступность сервера: {url}")
    
    try:
        # Проверяем главную страницу
        response = requests.get(url, timeout=10)
        print(f"✅ Главная страница: {response.status_code}")
        
        # Проверяем API
        api_response = requests.get(f"{url}/api/options/faculties", timeout=10)
        print(f"✅ API факультетов: {api_response.status_code}")
        
        # Проверяем webhook endpoint
        webhook_response = requests.post(f"{url}/webhook", json={"test": "data"}, timeout=10)
        print(f"✅ Webhook endpoint: {webhook_response.status_code}")
        
        print("\n🎉 Сервер доступен и работает!")
        return True
        
    except requests.exceptions.Timeout:
        print("❌ Таймаут подключения к серверу")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения к серверу")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_telegram_webhook():
    """Проверяет статус webhook в Telegram"""
    import requests
    
    BOT_TOKEN = "8296584992:AAFmltay1-OZolKK0AoF8pdKF2kELfg4boA"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if result.get("ok"):
            webhook_info = result.get("result", {})
            print(f"\n📊 Статус webhook:")
            print(f"URL: {webhook_info.get('url', 'Не установлен')}")
            print(f"Статус: {'Активен' if webhook_info.get('url') else 'Не установлен'}")
            print(f"Ошибки: {webhook_info.get('last_error_message', 'Нет')}")
            print(f"Количество ошибок: {webhook_info.get('last_error_count', 0)}")
            
            if webhook_info.get('url') == 'https://vm-fc7b7f29.na4u.ru/webhook':
                print("✅ Webhook настроен правильно!")
                return True
            else:
                print("❌ Webhook настроен неправильно!")
                return False
        else:
            print("❌ Ошибка получения информации о webhook")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки webhook: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Тестирование сервера и webhook")
    print("=" * 50)
    
    # Проверяем сервер
    server_ok = test_server()
    
    # Проверяем webhook
    webhook_ok = test_telegram_webhook()
    
    print("\n" + "=" * 50)
    if server_ok and webhook_ok:
        print("🎉 Все проверки пройдены успешно!")
        print("\n📋 Следующие шаги:")
        print("1. Убедитесь, что сервер запущен на вашем домене")
        print("2. Откройте бота в Telegram: https://t.me/scheduleSPAbot")
        print("3. Отправьте команду /start")
        print("4. Нажмите кнопку 'Открыть расписание'")
        print("5. Проверьте логи сервера на наличие ошибок аутентификации")
    else:
        print("❌ Обнаружены проблемы:")
        if not server_ok:
            print("- Сервер недоступен")
        if not webhook_ok:
            print("- Webhook настроен неправильно")
        print("\n🔧 Рекомендации:")
        print("1. Убедитесь, что сервер запущен")
        print("2. Проверьте настройки домена")
        print("3. Запустите: python setup_webhook.py")

