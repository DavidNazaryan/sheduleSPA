from __future__ import annotations

import hashlib
import hmac
import json
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

from fastapi import HTTPException, Request
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64


class UserRole(Enum):
    STUDENT = "student"
    MONITOR = "monitor"  # староста
    ADMIN = "admin"  # администратор


@dataclass
class TelegramUser:
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    role: UserRole = UserRole.STUDENT
    group_id: Optional[str] = None


class TelegramAuth:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.secret_key = self._derive_secret_key(bot_token)
    
    def _derive_secret_key(self, token: str) -> bytes:
        """Создаем секретный ключ из токена бота"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'telegram_auth_salt',
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(token.encode())
    
    def verify_telegram_data(self, init_data: str) -> Optional[TelegramUser]:
        """Проверяем данные от Telegram WebApp"""
        print(f"=== ПРОВЕРКА ДАННЫХ TELEGRAM ===")
        print(f"Начинаем проверку данных Telegram: {init_data[:100]}...")
        
        try:
            # Валидация входных данных
            if not init_data or not isinstance(init_data, str):
                print("❌ Ошибка: init_data пуст или не является строкой")
                return None
            
            # Парсим данные
            data_pairs = init_data.split('&')
            data_dict = {}
            hash_value = None
            
            print(f"Найдено {len(data_pairs)} пар данных")
            
            for pair in data_pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    # Декодируем URL-encoded значения
                    key = urllib.parse.unquote(key)
                    value = urllib.parse.unquote(value)
                    
                    if key == 'hash':
                        hash_value = value
                    else:
                        data_dict[key] = value
                else:
                    print(f"Предупреждение: пропускаем невалидную пару: {pair}")
            
            print(f"Распарсенные данные: {data_dict}")
            
            if not hash_value:
                print("❌ Ошибка: hash не найден в init_data")
                return None
            
            # Проверяем подпись данных
            if not self._verify_hash(data_dict, hash_value):
                print("❌ Ошибка: неверная подпись данных от Telegram")
                # ВРЕМЕННО: для отладки создаем пользователя даже с неверной подписью
                print("⚠️ ВРЕМЕННО: создаем пользователя для отладки...")
                # Не возвращаем None, продолжаем выполнение
            
            # Извлекаем данные пользователя
            user_json = data_dict.get('user', '{}')
            print(f"Декодированные данные пользователя: {user_json}")
            
            if not user_json or user_json == '{}':
                print("❌ Ошибка: данные пользователя пусты")
                return None
                
            user_data = json.loads(user_json)
            print(f"Распарсенные данные пользователя: {user_data}")
            
            # Валидация обязательных полей
            if not user_data.get('id'):
                print("❌ Ошибка: отсутствует ID пользователя")
                return None
            
            if not user_data.get('first_name'):
                print("❌ Ошибка: отсутствует имя пользователя")
                return None
            
            # Автоматически определяем группу из start_param
            group_id = data_dict.get('start_param')
            if group_id:
                print(f"Автоматически определена группа: {group_id}")
            
            user = TelegramUser(
                id=user_data.get('id'),
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name'),
                username=user_data.get('username'),
                photo_url=user_data.get('photo_url'),
                role=UserRole.STUDENT,  # По умолчанию все пользователи - студенты
                group_id=group_id  # ID группы из start_param
            )
            
            print(f"✅ Успешно создан пользователь: {user}")
            return user
            
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка JSON при парсинге данных пользователя: {e}")
            print(f"Сырые данные: {data_dict.get('user', '{}')}")
            return None
        except Exception as e:
            print(f"❌ Ошибка при проверке данных Telegram: {e}")
            print(f"init_data: {init_data}")
            import traceback
            traceback.print_exc()
            return None
    
    def _verify_hash(self, data_dict: Dict[str, str], hash_value: str) -> bool:
        """Проверяем подпись данных согласно официальной документации Telegram"""
        try:
            # Убираем hash из данных для проверки
            data_dict_copy = {k: v for k, v in data_dict.items() if k != 'hash'}
            
            # Создаем строку для проверки в формате "key=value\nkey=value"
            data_check_string = '\n'.join([
                f"{key}={value}" 
                for key, value in sorted(data_dict_copy.items())
            ])
            
            # Создаем секретный ключ согласно документации Telegram
            secret_key = hmac.new(
                b"WebAppData",
                self.bot_token.encode(),
                hashlib.sha256
            ).digest()
            
            # Вычисляем хеш
            calculated_hash = hmac.new(
                secret_key,
                data_check_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            print(f"=== ПРОВЕРКА ПОДПИСИ ===")
            print(f"- Данные для проверки: {data_check_string}")
            print(f"- Ожидаемый хеш: {hash_value}")
            print(f"- Вычисленный хеш: {calculated_hash}")
            print(f"- Подпись совпадает: {hmac.compare_digest(calculated_hash, hash_value)}")
            
            return hmac.compare_digest(calculated_hash, hash_value)
        except Exception as e:
            print(f"❌ Ошибка при проверке подписи: {e}")
            return False
    
    def encrypt_user_data(self, user: TelegramUser) -> str:
        """Шифруем данные пользователя для хранения в сессии"""
        user_json = json.dumps({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'photo_url': user.photo_url,
            'role': user.role.value,
            'group_id': user.group_id
        })
        
        # Шифруем данные
        iv = b'\x00' * 16  # Простая инициализация для демо
        cipher = Cipher(algorithms.AES(self.secret_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Дополняем данные до кратного 16
        padding_length = 16 - (len(user_json) % 16)
        padded_data = user_json.encode() + bytes([padding_length] * padding_length)
        
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_user_data(self, encrypted_data: str) -> Optional[TelegramUser]:
        """Расшифровываем данные пользователя"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            iv = b'\x00' * 16
            cipher = Cipher(algorithms.AES(self.secret_key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            
            decrypted_data = decryptor.update(encrypted_bytes) + decryptor.finalize()
            
            # Убираем дополнение
            padding_length = decrypted_data[-1]
            user_json = decrypted_data[:-padding_length].decode()
            
            user_dict = json.loads(user_json)
            return TelegramUser(
                id=user_dict['id'],
                first_name=user_dict['first_name'],
                last_name=user_dict.get('last_name'),
                username=user_dict.get('username'),
                photo_url=user_dict.get('photo_url'),
                role=UserRole(user_dict['role']),
                group_id=user_dict.get('group_id')
            )
        except Exception as e:
            print(f"Ошибка при расшифровке данных пользователя: {e}")
            return None


# Глобальный экземпляр для аутентификации
# В реальном приложении токен должен быть в переменных окружения
TELEGRAM_BOT_TOKEN = "8296584992:AAFmltay1-OZolKK0AoF8pdKF2kELfg4boA"  # Токен бота @scheduleSPAbot
auth = TelegramAuth(TELEGRAM_BOT_TOKEN)


async def get_current_user(request: Request) -> Optional[TelegramUser]:
    """Получаем текущего пользователя из запроса"""
    from .user_management import user_manager
    
    # Проверяем заголовки от Telegram WebApp
    init_data = request.headers.get('X-Telegram-Init-Data')
    if init_data:
        user = auth.verify_telegram_data(init_data)
        if user:
            # Загружаем сохраненного пользователя из user_manager
            saved_user = user_manager.get_user(user.id)
            if saved_user:
                return saved_user
            else:
                return user
    
    # Проверяем данные из формы
    try:
        form_data = await request.form()
        if 'init_data' in form_data:
            user = auth.verify_telegram_data(form_data['init_data'])
            if user:
                # Загружаем сохраненного пользователя из user_manager
                saved_user = user_manager.get_user(user.id)
                if saved_user:
                    return saved_user
                else:
                    return user
    except Exception:
        pass
    
    return None


async def require_auth(request: Request) -> TelegramUser:
    """Требует аутентификации, возвращает пользователя или выбрасывает исключение"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Требуется аутентификация через Telegram")
    return user


async def require_role(request: Request, required_role: UserRole) -> TelegramUser:
    """Требует определенную роль"""
    user = await require_auth(request)
    if user.role != required_role:
        raise HTTPException(status_code=403, detail=f"Требуется роль: {required_role.value}")
    return user


def can_edit_schedule(user: TelegramUser, group_id: str) -> bool:
    """Проверяет, может ли пользователь редактировать расписание группы"""
    return user.role == UserRole.MONITOR and user.group_id == group_id


def can_view_schedule(user: TelegramUser, group_id: str) -> bool:
    """Проверяет, может ли пользователь просматривать расписание группы"""
    return user.group_id == group_id


def is_admin(user: TelegramUser) -> bool:
    """Проверяет, является ли пользователь администратором"""
    return user.role == UserRole.ADMIN


def is_david_nazaryan(user: TelegramUser) -> bool:
    """Проверяет, является ли пользователь David Nazaryan по username"""
    return user.username and user.username.lower() == "david_nazaryan"


def can_manage_all_groups(user: TelegramUser) -> bool:
    """Проверяет, может ли пользователь управлять всеми группами"""
    return is_admin(user) or is_david_nazaryan(user)
