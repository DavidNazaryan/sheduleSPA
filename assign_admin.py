#!/usr/bin/env python3
"""
Скрипт для назначения пользователя @david_nazaryan администратором
"""

import requests
import sys

def assign_admin():
    """Назначает пользователя @david_nazaryan администратором"""
    
    # ID пользователя @david_nazaryan (нужно получить из Telegram)
    # Для тестирования используем фиктивный ID
    user_id = 123456789  # Замените на реальный ID пользователя
    
    # API endpoint
    API_URL = "http://localhost:8000/api/users/role"
    
    payload = {
        "user_id": user_id,
        "role": "admin",
        "group_id": None  # Администратор не привязан к конкретной группе
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        
        result = response.json()
        if result.get("success"):
            print(f"✅ Пользователь {user_id} успешно назначен администратором!")
            print("Теперь @david_nazaryan может:")
            print("- Управлять всеми группами")
            print("- Назначать старост для любых групп")
            print("- Просматривать все группы в системе")
        else:
            print(f"❌ Ошибка: {result.get('message', 'Неизвестная ошибка')}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения к API: {e}")
        print("Убедитесь, что сервер запущен на http://localhost:8000")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def get_user_id_by_username():
    """Получает ID пользователя по username через Telegram API"""
    print("Для получения ID пользователя @david_nazaryan:")
    print("1. Отправьте боту команду /start")
    print("2. Откройте мини-приложение")
    print("3. В консоли браузера выполните: console.log(window.Telegram.WebApp.initData)")
    print("4. Найдите user.id в данных")
    print("5. Замените user_id в этом скрипте на полученный ID")
    print()
    print("Или используйте тестовый режим в приложении для создания тестового пользователя")

if __name__ == "__main__":
    print("🔧 Назначение администратора")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        get_user_id_by_username()
    else:
        print("⚠️  Внимание: Замените user_id на реальный ID пользователя @david_nazaryan")
        print("Для получения ID выполните: python assign_admin.py --help")
        print()
        
        confirm = input("Продолжить с тестовым ID? (y/N): ")
        if confirm.lower() == 'y':
            assign_admin()
        else:
            print("Отменено. Обновите user_id в скрипте и запустите снова.")

