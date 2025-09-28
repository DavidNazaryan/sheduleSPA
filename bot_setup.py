#!/usr/bin/env python3
"""
Настройка Telegram бота для авторизации через WebApp
"""

import requests
import json
import os
from typing import Dict, Any

class TelegramBotSetup:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def set_webhook(self, webhook_url: str) -> Dict[str, Any]:
        """Устанавливает webhook для бота"""
        url = f"{self.base_url}/setWebhook"
        data = {
            "url": webhook_url,
            "allowed_updates": ["message", "callback_query"]
        }
        
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def set_commands(self) -> Dict[str, Any]:
        """Устанавливает команды бота"""
        url = f"{self.base_url}/setMyCommands"
        
        commands = [
            {"command": "start", "description": "🚀 Запустить бота и войти в приложение"},
            {"command": "help", "description": "❓ Показать справку по боту"},
            {"command": "login", "description": "🔐 Войти в приложение расписания"},
            {"command": "status", "description": "📊 Проверить статус бота"}
        ]
        
        data = {"commands": commands}
        
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def set_webapp_menu(self, webapp_url: str) -> Dict[str, Any]:
        """Устанавливает меню с WebApp кнопкой"""
        url = f"{self.base_url}/setChatMenuButton"
        
        data = {
            "menu_button": {
                "type": "web_app",
                "text": "📅 Открыть расписание",
                "web_app": {
                    "url": webapp_url
                }
            }
        }
        
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def get_webhook_info(self) -> Dict[str, Any]:
        """Получает информацию о webhook"""
        url = f"{self.base_url}/getWebhookInfo"
        
        try:
            response = requests.get(url)
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def delete_webhook(self) -> Dict[str, Any]:
        """Удаляет webhook"""
        url = f"{self.base_url}/deleteWebhook"
        
        try:
            response = requests.post(url)
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def send_message(self, chat_id: int, text: str, reply_markup: Dict = None) -> Dict[str, Any]:
        """Отправляет сообщение пользователю"""
        url = f"{self.base_url}/sendMessage"
        
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        
        if reply_markup:
            data["reply_markup"] = reply_markup
        
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def send_webapp_button(self, chat_id: int, webapp_url: str) -> Dict[str, Any]:
        """Отправляет сообщение с кнопкой WebApp"""
        text = """
🎓 *Добро пожаловать в приложение расписания ФГУ МГУ!*

Здесь вы можете:
• 📅 Просматривать расписание пар
• 📝 Добавлять домашние задания (для старост)
• 👥 Управлять пользователями (для старост)
• ⚙️ Настраивать профиль

Нажмите кнопку ниже, чтобы открыть приложение:
        """
        
        reply_markup = {
            "inline_keyboard": [[
                {
                    "text": "📅 Открыть расписание",
                    "web_app": {"url": webapp_url}
                }
            ]]
        }
        
        return self.send_message(chat_id, text, reply_markup)
    
    def send_help_message(self, chat_id: int) -> Dict[str, Any]:
        """Отправляет справку"""
        text = """
🤖 *Справка по боту расписания*

*Доступные команды:*
/start - 🚀 Запустить бота и войти в приложение
/login - 🔐 Войти в приложение расписания
/help - ❓ Показать эту справку
/status - 📊 Проверить статус бота

*Функции приложения:*
• 📅 Просмотр расписания пар
• 📝 Добавление домашних заданий (для старост)
• 👥 Управление пользователями (для старост)
• ⚙️ Настройки и профиль

*Для использования:*
1. Нажмите /start или /login
2. Выберите "Открыть расписание"
3. Войдите в приложение через Telegram

*Поддержка:* @david_nazaryan
        """
        
        return self.send_message(chat_id, text)
    
    def send_status_message(self, chat_id: int) -> Dict[str, Any]:
        """Отправляет статус бота"""
        webhook_info = self.get_webhook_info()
        
        if webhook_info.get("ok"):
            result = webhook_info.get("result", {})
            status = "✅ Активен" if result.get("url") else "❌ Не настроен"
            url = result.get("url", "Не установлен")
            errors = result.get("last_error_message", "Нет")
        else:
            status = "❌ Ошибка"
            url = "Неизвестно"
            errors = "Не удалось получить информацию"
        
        text = f"""
📊 *Статус бота расписания*

*Webhook:* {status}
*URL:* `{url}`
*Ошибки:* {errors}

*Бот готов к работе!* 🚀
        """
        
        return self.send_message(chat_id, text)


def main():
    """Основная функция настройки"""
    # Конфигурация
    BOT_TOKEN = "8296584992:AAFmltay1-OZolKK0AoF8pdKF2kELfg4boA"
    WEBHOOK_URL = "http://localhost:8000/webhook"
    WEBAPP_URL = "http://localhost:8000"
    
    print("🤖 Настройка Telegram бота @scheduleSPAbot")
    print("=" * 50)
    
    # Создаем экземпляр бота
    bot = TelegramBotSetup(BOT_TOKEN)
    
    # 1. Устанавливаем команды
    print("\n1. Устанавливаем команды бота...")
    result = bot.set_commands()
    if result.get("ok"):
        print("✅ Команды установлены успешно!")
    else:
        print(f"❌ Ошибка установки команд: {result.get('error')}")
    
    # 2. Устанавливаем WebApp меню
    print("\n2. Устанавливаем WebApp меню...")
    result = bot.set_webapp_menu(WEBAPP_URL)
    if result.get("ok"):
        print("✅ WebApp меню установлено!")
    else:
        print(f"❌ Ошибка установки меню: {result.get('error')}")
    
    # 3. Устанавливаем webhook
    print("\n3. Устанавливаем webhook...")
    result = bot.set_webhook(WEBHOOK_URL)
    if result.get("ok"):
        print("✅ Webhook установлен успешно!")
    else:
        print(f"❌ Ошибка установки webhook: {result.get('error')}")
    
    # 4. Проверяем статус
    print("\n4. Проверяем статус webhook...")
    result = bot.get_webhook_info()
    if result.get("ok"):
        webhook_info = result.get("result", {})
        print(f"📊 URL: {webhook_info.get('url', 'Не установлен')}")
        print(f"📊 Статус: {'Активен' if webhook_info.get('url') else 'Не установлен'}")
    else:
        print(f"❌ Ошибка получения информации: {result.get('error')}")
    
    print("\n✅ Настройка завершена!")
    print("\nТеперь:")
    print("1. Запустите сервер: uvicorn app.main:app --reload")
    print("2. Откройте бота: https://t.me/scheduleSPAbot")
    print("3. Отправьте команду /start")
    print("4. Нажмите кнопку 'Открыть расписание'")


if __name__ == "__main__":
    main()

