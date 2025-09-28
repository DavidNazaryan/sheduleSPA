# 🚀 Инструкция по развертыванию на сервере

## 📋 Настройка webhook завершена!

✅ **Webhook успешно настроен:**
- URL: `https://vm-fc7b7f29.na4u.ru/webhook`
- Статус: Активен
- Ошибки: Нет

## 🔧 Что нужно сделать на сервере:

### 1. Загрузить код на сервер

```bash
# Скопируйте все файлы проекта на ваш сервер
# Убедитесь, что структура папок сохранена:
# /path/to/your/project/
# ├── app/
# │   ├── auth.py
# │   ├── main.py
# │   ├── user_management.py
# │   └── templates/
# │       └── index.html
# ├── data/
# ├── parser/
# ├── requirements.txt
# └── setup_webhook.py
```

### 2. Установить зависимости

```bash
# На сервере выполните:
pip install -r requirements.txt
```

### 3. Запустить сервер

```bash
# Для продакшена используйте:
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Или с Gunicorn (рекомендуется для продакшена):
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 4. Настроить прокси (если нужно)

Если у вас есть Nginx или другой веб-сервер, настройте прокси:

```nginx
server {
    listen 443 ssl;
    server_name vm-fc7b7f29.na4u.ru;
    
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🧪 Тестирование

### 1. Проверьте доступность сервера

```bash
curl https://vm-fc7b7f29.na4u.ru
```

### 2. Проверьте API

```bash
curl https://vm-fc7b7f29.na4u.ru/api/options/faculties
```

### 3. Проверьте webhook

```bash
curl -X POST https://vm-fc7b7f29.na4u.ru/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## 🤖 Тестирование в Telegram

1. **Откройте бота:** https://t.me/scheduleSPAbot
2. **Отправьте команду:** `/start`
3. **Нажмите кнопку:** "📅 Открыть расписание"
4. **Проверьте логи сервера** на наличие сообщений аутентификации

## 📊 Ожидаемые логи

При успешной аутентификации в логах должны появиться:

```
✅ Успешно создан пользователь: TelegramUser(id=123456, first_name='Имя', ...)
Автоматически определена группа: group_id
```

## 🔍 Отладка проблем

### Проблема: 502 Bad Gateway

**Причина:** Сервер не запущен или недоступен

**Решение:**
1. Проверьте, что сервер запущен: `ps aux | grep uvicorn`
2. Проверьте порт: `netstat -tlnp | grep 8000`
3. Проверьте логи сервера

### Проблема: Webhook не получает данные

**Причина:** Проблемы с SSL или доступностью

**Решение:**
1. Проверьте SSL сертификат
2. Убедитесь, что сервер доступен из интернета
3. Проверьте настройки файрвола

### Проблема: Ошибка аутентификации

**Причина:** Проблемы с проверкой подписи

**Решение:**
1. Проверьте токен бота
2. Убедитесь, что webhook настроен правильно
3. Проверьте логи на наличие ошибок проверки подписи

## 📝 Команды для управления

### Перезапуск webhook

```bash
python setup_webhook.py
```

### Проверка статуса webhook

```bash
python -c "
import requests
BOT_TOKEN = '8296584992:AAFmltay1-OZolKK0AoF8pdKF2kELfg4boA'
response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo')
print(response.json())
"
```

### Удаление webhook (если нужно)

```bash
python -c "
import requests
BOT_TOKEN = '8296584992:AAFmltay1-OZolKK0AoF8pdKF2kELfg4boA'
response = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook')
print(response.json())
"
```

## 🎯 Следующие шаги

1. **Запустите сервер** на вашем домене
2. **Протестируйте** доступность через браузер
3. **Откройте бота** в Telegram и протестируйте аутентификацию
4. **Проверьте логи** на наличие ошибок
5. **Настройте мониторинг** для отслеживания работы

## 🆘 Поддержка

При возникновении проблем:
1. Проверьте логи сервера
2. Убедитесь в правильности настроек
3. Протестируйте доступность сервера
4. Обратитесь к разработчику: @david_nazaryan

