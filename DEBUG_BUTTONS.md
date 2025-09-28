# Отладка кнопок домашнего задания

## Проблема
Кнопки "Добавить ДЗ" не отображаются в тестовом режиме.

## Исправления

### 1. **Добавлен вызов `updatePermissionBasedUI` после создания расписания**
```javascript
// В функции создания расписания
setTimeout(() => {
    if (typeof authManager !== 'undefined' && authManager.updatePermissionBasedUI) {
        authManager.updatePermissionBasedUI();
    }
}, 50);
```

### 2. **Добавлен вызов в `testMode()`**
```javascript
testMode() {
    // ... код инициализации ...
    setTimeout(() => {
        this.updatePermissionBasedUI();
    }, 100);
}
```

### 3. **Добавлен вызов при загрузке из localStorage**
```javascript
// При загрузке сохраненного тестового пользователя
setTimeout(() => {
    this.updatePermissionBasedUI();
}, 100);
```

### 4. **Добавлена отладочная информация**
```javascript
updatePermissionBasedUI() {
    console.log('Updating permission-based UI...', {
        canEdit: this.permissions.canEdit,
        currentUser: this.currentUser
    });
    
    const homeworkButtons = document.querySelectorAll('.add-homework-btn');
    console.log('Found homework buttons:', homeworkButtons.length);
    // ...
}
```

## Как проверить

### 1. **Откройте консоль браузера (F12)**

### 2. **Войдите в тестовый режим**
- Нажмите "Тестовый режим"
- Проверьте консоль на сообщения отладки

### 3. **Загрузите расписание**
- Выберите факультет, курс и группу
- Проверьте консоль на сообщения о найденных кнопках

### 4. **Проверьте элементы DOM**
```javascript
// В консоли браузера
document.querySelectorAll('.add-homework-btn').length
```

## Тестовый файл

Откройте `test_buttons.html` в браузере для изолированного тестирования кнопок.

## Возможные причины

1. **Кнопки не созданы** - расписание не загружено
2. **Функция вызывается слишком рано** - DOM еще не готов
3. **Селектор не находит элементы** - неправильный CSS селектор
4. **Права доступа не установлены** - `canEdit` = false

## Решение

1. Убедитесь, что расписание загружено
2. Проверьте консоль на ошибки
3. Убедитесь, что пользователь имеет роль "monitor"
4. Проверьте, что `authManager.permissions.canEdit` = true

