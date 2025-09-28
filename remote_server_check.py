#!/usr/bin/env python3
"""
Скрипт для проверки состояния удаленного сервера
Запустите этот скрипт на вашем сервере vm-fc7b7f29.na4u.ru
"""

import requests
import json
import os
import subprocess
import sys
from datetime import datetime

def check_server_status():
    """Проверяет состояние сервера"""
    print("🔍 Проверка состояния сервера")
    print("=" * 50)
    
    # Проверяем, запущен ли сервер
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'uvicorn' in result.stdout:
            print("✅ Сервер uvicorn запущен")
        else:
            print("❌ Сервер uvicorn не запущен")
    except:
        print("⚠️ Не удалось проверить процессы")
    
    # Проверяем порт 8000
    try:
        result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
        if ':8000' in result.stdout:
            print("✅ Порт 8000 открыт")
        else:
            print("❌ Порт 8000 не открыт")
    except:
        print("⚠️ Не удалось проверить порты")

def check_webhook_status():
    """Проверяет статус webhook"""
    print("\n📊 Проверка статуса webhook")
    print("=" * 50)
    
    BOT_TOKEN = "8296584992:AAFmltay1-OZolKK0AoF8pdKF2kELfg4boA"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if result.get("ok"):
            webhook_info = result.get("result", {})
            print(f"URL: {webhook_info.get('url', 'Не установлен')}")
            print(f"Статус: {'Активен' if webhook_info.get('url') else 'Не установлен'}")
            print(f"Ошибки: {webhook_info.get('last_error_message', 'Нет')}")
            print(f"Количество ошибок: {webhook_info.get('last_error_count', 0)}")
            
            if webhook_info.get('url') == 'https://vm-fc7b7f29.na4u.ru/webhook':
                print("✅ Webhook настроен правильно!")
            else:
                print("❌ Webhook настроен неправильно!")
        else:
            print("❌ Ошибка получения информации о webhook")
            
    except Exception as e:
        print(f"❌ Ошибка проверки webhook: {e}")

def test_local_endpoints():
    """Тестирует локальные endpoints"""
    print("\n🧪 Тестирование локальных endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    endpoints = [
        "/",
        "/api/options/faculties",
        "/api/options/courses?faculty=5",
        "/api/options/groups?faculty=5&course=1"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

def test_webhook_endpoint():
    """Тестирует webhook endpoint"""
    print("\n🔗 Тестирование webhook endpoint")
    print("=" * 50)
    
    test_data = {
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
        response = requests.post("http://localhost:8000/webhook", json=test_data, timeout=5)
        print(f"✅ Webhook: {response.status_code}")
        print(f"Ответ: {response.json()}")
    except Exception as e:
        print(f"❌ Webhook: {e}")

def check_logs():
    """Проверяет логи сервера"""
    print("\n📝 Последние логи сервера")
    print("=" * 50)
    
    # Попробуем найти логи
    log_files = [
        "/var/log/nginx/error.log",
        "/var/log/nginx/access.log",
        "/var/log/syslog",
        "/var/log/messages"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            try:
                result = subprocess.run(['tail', '-n', '10', log_file], capture_output=True, text=True)
                print(f"📄 {log_file}:")
                print(result.stdout)
                break
            except:
                continue
    
    print("💡 Для просмотра логов uvicorn используйте:")
    print("   journalctl -u your-service-name -f")
    print("   или")
    print("   tail -f /path/to/your/logfile")

def check_disk_space():
    """Проверяет место на диске"""
    print("\n💾 Проверка места на диске")
    print("=" * 50)
    
    try:
        result = subprocess.run(['df', '-h'], capture_output=True, text=True)
        print(result.stdout)
    except:
        print("⚠️ Не удалось проверить место на диске")

def check_memory():
    """Проверяет использование памяти"""
    print("\n🧠 Проверка использования памяти")
    print("=" * 50)
    
    try:
        result = subprocess.run(['free', '-h'], capture_output=True, text=True)
        print(result.stdout)
    except:
        print("⚠️ Не удалось проверить использование памяти")

def generate_report():
    """Генерирует отчет"""
    print("\n📊 Генерация отчета")
    print("=" * 50)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "server": "vm-fc7b7f29.na4u.ru",
        "checks": {
            "server_status": "Проверено",
            "webhook_status": "Проверено",
            "endpoints": "Проверены",
            "webhook_endpoint": "Проверен"
        }
    }
    
    # Сохраняем отчет
    with open('/tmp/server_check_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("✅ Отчет сохранен в /tmp/server_check_report.json")

if __name__ == "__main__":
    print("🚀 Проверка удаленного сервера vm-fc7b7f29.na4u.ru")
    print("=" * 60)
    print(f"Время: {datetime.now()}")
    print(f"Python: {sys.version}")
    print(f"Рабочая директория: {os.getcwd()}")
    
    check_server_status()
    check_webhook_status()
    test_local_endpoints()
    test_webhook_endpoint()
    check_logs()
    check_disk_space()
    check_memory()
    generate_report()
    
    print("\n" + "=" * 60)
    print("✅ Проверка завершена!")
    print("\n📋 Следующие шаги:")
    print("1. Скопируйте результаты проверки")
    print("2. Отправьте их разработчику")
    print("3. При необходимости запустите сервер:")
    print("   uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("4. Проверьте настройки прокси (nginx/apache)")

