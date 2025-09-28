# 🚀 Инструкция по развертыванию на удаленном сервере

## 📋 **Пошаговая инструкция:**

### 1. **Подключение к серверу**
```bash
ssh your-username@vm-fc7b7f29.na4u.ru
```

### 2. **Загрузка файлов проекта**
```bash
# Создайте директорию для проекта
mkdir -p /home/your-username/schedule-spa
cd /home/your-username/schedule-spa

# Загрузите все файлы проекта (используйте scp, rsync или git)
# Например, через scp:
scp -r /path/to/local/project/* your-username@vm-fc7b7f29.na4u.ru:/home/your-username/schedule-spa/
```

### 3. **Установка зависимостей**
```bash
# Установите Python зависимости
pip install -r requirements.txt

# Или создайте виртуальное окружение
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. **Настройка скриптов**
```bash
# Сделайте скрипты исполняемыми
chmod +x start_server.sh
chmod +x stop_server.sh
chmod +x status_server.sh

# Отредактируйте start_server.sh и укажите правильный путь к проекту
nano start_server.sh
# Измените строку: cd /path/to/your/project
# На: cd /home/your-username/schedule-spa
```

### 5. **Запуск сервера**
```bash
# Запустите сервер
./start_server.sh

# Проверьте статус
./status_server.sh
```

### 6. **Проверка работоспособности**
```bash
# Запустите скрипт проверки
python remote_server_check.py

# Проверьте логи
tail -f logs/server.log
```

### 7. **Настройка автозапуска (опционально)**
```bash
# Создайте systemd сервис
sudo nano /etc/systemd/system/schedule-spa.service
```

Содержимое файла сервиса:
```ini
[Unit]
Description=Schedule SPA Server
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/schedule-spa
ExecStart=/home/your-username/schedule-spa/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# Активируйте сервис
sudo systemctl daemon-reload
sudo systemctl enable schedule-spa
sudo systemctl start schedule-spa
sudo systemctl status schedule-spa
```

## 🔧 **Полезные команды:**

### **Управление сервером:**
```bash
# Запуск
./start_server.sh

# Остановка
./stop_server.sh

# Проверка статуса
./status_server.sh

# Просмотр логов
tail -f logs/server.log

# Перезапуск
./stop_server.sh && ./start_server.sh
```

### **Проверка системы:**
```bash
# Проверка процессов
ps aux | grep uvicorn

# Проверка портов
netstat -tlnp | grep 8000

# Проверка использования ресурсов
htop
free -h
df -h
```

### **Проверка доступности:**
```bash
# Локальная проверка
curl http://localhost:8000

# Внешняя проверка
curl https://vm-fc7b7f29.na4u.ru

# Проверка API
curl https://vm-fc7b7f29.na4u.ru/api/options/faculties
```

## 🐛 **Отладка проблем:**

### **Проблема: Сервер не запускается**
```bash
# Проверьте логи
cat logs/server.log

# Проверьте зависимости
pip list

# Проверьте Python версию
python --version
```

### **Проблема: Порт занят**
```bash
# Найдите процесс, использующий порт 8000
lsof -i :8000

# Остановите процесс
kill -9 PID
```

### **Проблема: Внешний доступ не работает**
```bash
# Проверьте настройки прокси (nginx/apache)
sudo nginx -t
sudo systemctl status nginx

# Проверьте файрвол
sudo ufw status
```

## 📊 **Мониторинг:**

### **Создание скрипта мониторинга:**
```bash
# Создайте скрипт для регулярной проверки
nano monitor.sh
```

```bash
#!/bin/bash
# monitor.sh

while true; do
    if ! pgrep -f "uvicorn" > /dev/null; then
        echo "$(date): Сервер не запущен, перезапускаем..."
        ./start_server.sh
    fi
    sleep 60
done
```

```bash
# Запустите мониторинг в фоне
nohup ./monitor.sh > monitor.log 2>&1 &
```

## 📝 **Отправка результатов:**

После выполнения проверки отправьте результаты:

1. **Вывод команды:** `./status_server.sh`
2. **Результат проверки:** `python remote_server_check.py`
3. **Последние логи:** `tail -n 20 logs/server.log`
4. **Информация о системе:** `uname -a && python --version`

## 🆘 **Поддержка:**

При возникновении проблем:
1. Проверьте логи сервера
2. Убедитесь в правильности настроек
3. Проверьте доступность сервера
4. Обратитесь к разработчику: @david_nazaryan

