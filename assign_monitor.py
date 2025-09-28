#!/usr/bin/env python3
"""
Скрипт для назначения старосты через API
"""

import requests
import json
import sys

# URL вашего приложения
BASE_URL = "http://localhost:8000"

def assign_monitor(user_id, group_id, bot_token=None):
    """Назначает пользователя старостой группы"""
    
    # Данные для запроса
    data = {
        'user_id': user_id,
        'role': 'monitor',
        'group_id': group_id
    }
    
    # Если есть токен бота, добавляем его для аутентификации
    if bot_token:
        data['init_data'] = f'bot_token={bot_token}'
    
    try:
        print(f"Назначаем пользователя {user_id} старостой группы {group_id}...")
        
        response = requests.post(f"{BASE_URL}/api/users/role", data=data)
        
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Успешно: {result.get('message', 'Роль изменена')}")
            return True
        else:
            print(f"❌ Ошибка: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка: Не удается подключиться к серверу")
        print("Убедитесь, что приложение запущено: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Использование: python assign_monitor.py <user_id> <group_id> [bot_token]")
        print("")
        print("Примеры:")
        print("  python assign_monitor.py 123456789 test-group")
        print("  python assign_monitor.py 123456789 test-group your_bot_token")
        print("")
        print("Где:")
        print("  user_id   - ID пользователя Telegram")
        print("  group_id  - ID группы")
        print("  bot_token - токен бота (опционально)")
        sys.exit(1)
    
    user_id = sys.argv[1]
    group_id = sys.argv[2]
    bot_token = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Проверяем, что user_id - это число
    try:
        user_id = int(user_id)
    except ValueError:
        print("❌ Ошибка: user_id должен быть числом")
        sys.exit(1)
    
    success = assign_monitor(user_id, group_id, bot_token)
    
    if success:
        print("\n🎉 Пользователь успешно назначен старостой!")
        print("Теперь он может:")
        print("- Добавлять домашние задания")
        print("- Управлять пользователями группы")
        print("- Редактировать расписание")
    else:
        print("\n💥 Не удалось назначить старосту")
        sys.exit(1)

if __name__ == "__main__":
    main()

