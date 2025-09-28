"""
Система авторизации на уровне бота
"""

from typing import Optional, Dict, Any
from .auth import TelegramUser, UserRole, is_admin, is_david_nazaryan, can_manage_all_groups
from .user_management import user_manager


class BotAuthorization:
    """Класс для управления авторизацией на уровне бота"""
    
    def __init__(self):
        self.authorized_users: Dict[int, TelegramUser] = {}
    
    def authorize_user(self, user: TelegramUser) -> bool:
        """Авторизует пользователя в боте"""
        try:
            # Сохраняем пользователя в системе
            user_manager.add_user(user)
            
            # Добавляем в список авторизованных
            self.authorized_users[user.id] = user
            
            return True
        except Exception as e:
            print(f"Ошибка авторизации пользователя {user.id}: {e}")
            return False
    
    def is_user_authorized(self, user_id: int) -> bool:
        """Проверяет, авторизован ли пользователь"""
        return user_id in self.authorized_users
    
    def get_user_permissions(self, user_id: int) -> Dict[str, bool]:
        """Получает права пользователя"""
        user = self.authorized_users.get(user_id)
        if not user:
            return {
                "can_view": False,
                "can_edit": False,
                "can_manage_users": False,
                "can_manage_all_groups": False,
                "is_admin": False
            }
        
        return {
            "can_view": True,  # Все авторизованные пользователи могут просматривать
            "can_edit": user.role == UserRole.MONITOR,
            "can_manage_users": user.role == UserRole.MONITOR or can_manage_all_groups(user),
            "can_manage_all_groups": can_manage_all_groups(user),
            "is_admin": can_manage_all_groups(user)
        }
    
    def get_user_role_display(self, user_id: int) -> str:
        """Получает отображаемое название роли пользователя"""
        user = self.authorized_users.get(user_id)
        if not user:
            return "Не авторизован"
        
        role_names = {
            UserRole.STUDENT: "Студент",
            UserRole.MONITOR: "Староста",
            UserRole.ADMIN: "Администратор",
            UserRole.GUEST: "Гость"
        }
        
        return role_names.get(user.role, "Пользователь")
    
    def get_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает информацию о пользователе"""
        user = self.authorized_users.get(user_id)
        if not user:
            return None
        
        permissions = self.get_user_permissions(user_id)
        
        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "role": user.role.value,
            "role_display": self.get_user_role_display(user_id),
            "group_id": user.group_id,
            "permissions": permissions
        }
    
    def update_user_role(self, user_id: int, new_role: UserRole, group_id: Optional[str] = None) -> bool:
        """Обновляет роль пользователя"""
        user = self.authorized_users.get(user_id)
        if not user:
            return False
        
        # Обновляем роль
        user.role = new_role
        if group_id:
            user.group_id = group_id
        
        # Сохраняем в системе
        user_manager.add_user(user)
        
        return True
    
    def deauthorize_user(self, user_id: int) -> bool:
        """Деавторизует пользователя"""
        if user_id in self.authorized_users:
            del self.authorized_users[user_id]
            return True
        return False
    
    def get_authorized_users_count(self) -> int:
        """Получает количество авторизованных пользователей"""
        return len(self.authorized_users)
    
    def get_authorized_users_list(self) -> list:
        """Получает список авторизованных пользователей"""
        return [
            {
                "id": user.id,
                "name": f"{user.first_name} {user.last_name or ''}".strip(),
                "username": user.username,
                "role": self.get_user_role_display(user.id),
                "group_id": user.group_id
            }
            for user in self.authorized_users.values()
        ]


# Глобальный экземпляр системы авторизации
bot_auth = BotAuthorization()


def check_bot_permission(user_id: int, permission: str) -> bool:
    """Проверяет права пользователя в боте"""
    permissions = bot_auth.get_user_permissions(user_id)
    return permissions.get(permission, False)


def require_bot_permission(permission: str):
    """Декоратор для проверки прав в боте"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Здесь можно добавить проверку прав
            # Пока просто вызываем функцию
            return func(*args, **kwargs)
        return wrapper
    return decorator

