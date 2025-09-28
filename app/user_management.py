from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from .auth import TelegramUser, UserRole


@dataclass
class UserGroup:
    group_id: str
    group_name: str
    monitor_user_id: Optional[int] = None
    student_user_ids: List[int] = None
    
    def __post_init__(self):
        if self.student_user_ids is None:
            self.student_user_ids = []


class UserManager:
    def __init__(self, data_file: str = "data/users.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(exist_ok=True)
        self._users: Dict[int, TelegramUser] = {}
        self._groups: Dict[str, UserGroup] = {}
        self._load_data()
    
    def _load_data(self):
        """Загружаем данные пользователей и групп из файла"""
        if not self.data_file.exists():
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Загружаем пользователей
            users_data = data.get('users', {})
            if isinstance(users_data, list):
                # Старый формат (список)
                users_list = users_data
            else:
                # Новый формат (словарь)
                users_list = users_data.values()
            
            for user_data in users_list:
                try:
                    # Проверяем обязательные поля
                    if 'id' not in user_data or 'first_name' not in user_data or 'role' not in user_data:
                        print(f"Пропускаем пользователя с неполными данными: {user_data}")
                        continue
                    
                    # Проверяем, что роль валидна
                    try:
                        role = UserRole(user_data['role'])
                    except ValueError:
                        print(f"Неверная роль пользователя {user_data.get('id', 'unknown')}: {user_data.get('role')}")
                        role = UserRole.STUDENT  # Устанавливаем роль по умолчанию
                    
                    user = TelegramUser(
                        id=user_data['id'],
                        first_name=user_data['first_name'],
                        last_name=user_data.get('last_name'),
                        username=user_data.get('username'),
                        photo_url=user_data.get('photo_url'),
                        role=role,
                        group_id=user_data.get('group_id')
                    )
                    self._users[user.id] = user
                except Exception as user_error:
                    print(f"Ошибка при загрузке пользователя {user_data.get('id', 'unknown')}: {user_error}")
                    continue
            
            # Загружаем группы
            groups_data = data.get('groups', {})
            if isinstance(groups_data, list):
                # Старый формат (список)
                groups_list = groups_data
            else:
                # Новый формат (словарь)
                groups_list = groups_data.values()
            
            for group_data in groups_list:
                try:
                    # Проверяем обязательные поля
                    if 'group_id' not in group_data or 'group_name' not in group_data:
                        print(f"Пропускаем группу с неполными данными: {group_data}")
                        continue
                    
                    group = UserGroup(
                        group_id=group_data['group_id'],
                        group_name=group_data['group_name'],
                        monitor_user_id=group_data.get('monitor_user_id'),
                        student_user_ids=group_data.get('student_user_ids', [])
                    )
                    self._groups[group.group_id] = group
                except Exception as group_error:
                    print(f"Ошибка при загрузке группы {group_data.get('group_id', 'unknown')}: {group_error}")
                    continue
                
        except json.JSONDecodeError as e:
            print(f"Ошибка JSON при загрузке данных пользователей: {e}")
            print(f"Файл: {self.data_file}")
            # Создаем резервную копию поврежденного файла
            backup_file = self.data_file.with_suffix('.json.backup')
            try:
                self.data_file.rename(backup_file)
                print(f"Создана резервная копия: {backup_file}")
            except Exception as backup_error:
                print(f"Не удалось создать резервную копию: {backup_error}")
            
            # Сбрасываем файл к начальному состоянию
            self.reset_data_file()
        except Exception as e:
            print(f"Ошибка при загрузке данных пользователей: {e}")
            # При критических ошибках также сбрасываем файл
            self.reset_data_file()
    
    def _save_data(self):
        """Сохраняем данные пользователей и групп в файл"""
        try:
            data = {
                'users': [asdict(user) for user in self._users.values()],
                'groups': [asdict(group) for group in self._groups.values()]
            }
            
            # Создаем временный файл для безопасной записи
            temp_file = self.data_file.with_suffix('.tmp')
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Проверяем, что временный файл содержит валидный JSON
            with open(temp_file, 'r', encoding='utf-8') as f:
                json.load(f)  # Проверяем валидность JSON
            
            # Если все хорошо, заменяем оригинальный файл
            temp_file.replace(self.data_file)
            print(f"Данные пользователей сохранены в {self.data_file}")
                
        except json.JSONDecodeError as e:
            print(f"Ошибка кодирования JSON при сохранении: {e}")
            # Удаляем временный файл при ошибке
            if temp_file.exists():
                temp_file.unlink()
        except Exception as e:
            print(f"Ошибка при сохранении данных пользователей: {e}")
            # Удаляем временный файл при ошибке
            if temp_file.exists():
                temp_file.unlink()
    
    def add_user(self, user: TelegramUser) -> TelegramUser:
        """Добавляем или обновляем пользователя"""
        self._users[user.id] = user
        self._save_data()
        return user
    
    def get_user(self, user_id: int) -> Optional[TelegramUser]:
        """Получаем пользователя по ID"""
        return self._users.get(user_id)
    
    def set_user_role(self, user_id: int, role: UserRole, group_id: Optional[str] = None) -> bool:
        """Устанавливаем роль пользователя"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        user.role = role
        user.group_id = group_id
        
        # Обновляем информацию в группе
        if group_id:
            if group_id not in self._groups:
                # Создаем новую группу, если её нет
                self._groups[group_id] = UserGroup(
                    group_id=group_id,
                    group_name=f"Группа {group_id}"
                )
            
            group = self._groups[group_id]
            
            if role == UserRole.MONITOR:
                # Убираем предыдущего старосту, если есть
                if group.monitor_user_id and group.monitor_user_id != user_id:
                    old_monitor = self.get_user(group.monitor_user_id)
                    if old_monitor:
                        old_monitor.role = UserRole.STUDENT
                
                group.monitor_user_id = user_id
                # Убираем из списка студентов, если был там
                if user_id in group.student_user_ids:
                    group.student_user_ids.remove(user_id)
            
            elif role == UserRole.STUDENT:
                # Убираем из старост, если был
                if group.monitor_user_id == user_id:
                    group.monitor_user_id = None
                
                # Добавляем в студентов, если ещё не там
                if user_id not in group.student_user_ids:
                    group.student_user_ids.append(user_id)
        
        self._save_data()
        return True
    
    def get_group(self, group_id: str) -> Optional[UserGroup]:
        """Получаем группу по ID"""
        return self._groups.get(group_id)
    
    def get_group_monitor(self, group_id: str) -> Optional[TelegramUser]:
        """Получаем старосту группы"""
        group = self.get_group(group_id)
        if not group or not group.monitor_user_id:
            return None
        return self.get_user(group.monitor_user_id)
    
    def get_group_students(self, group_id: str) -> List[TelegramUser]:
        """Получаем список студентов группы"""
        group = self.get_group(group_id)
        if not group:
            return []
        
        students = []
        for user_id in group.student_user_ids:
            user = self.get_user(user_id)
            if user:
                students.append(user)
        return students
    
    def is_user_in_group(self, user_id: int, group_id: str) -> bool:
        """Проверяем, состоит ли пользователь в группе"""
        group = self.get_group(group_id)
        if not group:
            return False
        
        return (group.monitor_user_id == user_id or 
                user_id in group.student_user_ids)
    
    def remove_user_from_group(self, user_id: int, group_id: str) -> bool:
        """Удаляем пользователя из группы"""
        group = self.get_group(group_id)
        if not group:
            return False
        
        # Убираем из старост
        if group.monitor_user_id == user_id:
            group.monitor_user_id = None
        
        # Убираем из студентов
        if user_id in group.student_user_ids:
            group.student_user_ids.remove(user_id)
        
        # Обновляем роль пользователя
        user = self.get_user(user_id)
        if user:
            user.role = UserRole.STUDENT
            user.group_id = None
        
        self._save_data()
        return True
    
    def create_group(self, group_id: str, group_name: str, monitor_user_id: int) -> bool:
        """Создаем новую группу со старостой"""
        if group_id in self._groups:
            return False
        
        group = UserGroup(
            group_id=group_id,
            group_name=group_name,
            monitor_user_id=monitor_user_id
        )
        self._groups[group_id] = group
        
        # Устанавливаем роль старосты
        self.set_user_role(monitor_user_id, UserRole.MONITOR, group_id)
        
        self._save_data()
        return True
    
    def reset_data_file(self):
        """Сбрасываем файл данных к начальному состоянию"""
        try:
            # Создаем пустую структуру
            data = {
                'users': [],
                'groups': []
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Очищаем память
            self._users.clear()
            self._groups.clear()
            
            print(f"Файл данных сброшен: {self.data_file}")
            return True
            
        except Exception as e:
            print(f"Ошибка при сбросе файла данных: {e}")
            return False


# Глобальный экземпляр менеджера пользователей
user_manager = UserManager()
