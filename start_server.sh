#!/bin/bash
# Скрипт для запуска сервера на удаленном сервере
# Сохраните как start_server.sh и сделайте исполняемым: chmod +x start_server.sh

echo "🚀 Запуск сервера расписания МГУ"
echo "=================================="

# Проверяем, запущен ли уже сервер
if pgrep -f "uvicorn" > /dev/null; then
    echo "⚠️ Сервер уже запущен!"
    echo "PID: $(pgrep -f uvicorn)"
    echo "Для перезапуска выполните: ./restart_server.sh"
    exit 1
fi

# Переходим в директорию проекта
cd /path/to/your/project  # ЗАМЕНИТЕ НА ПУТЬ К ВАШЕМУ ПРОЕКТУ

# Проверяем наличие файлов
if [ ! -f "app/main.py" ]; then
    echo "❌ Файл app/main.py не найден!"
    echo "Убедитесь, что вы находитесь в правильной директории"
    exit 1
fi

# Устанавливаем зависимости (если нужно)
if [ -f "requirements.txt" ]; then
    echo "📦 Проверяем зависимости..."
    pip install -r requirements.txt
fi

# Создаем директорию для логов
mkdir -p logs

# Запускаем сервер
echo "🌐 Запускаем сервер на порту 8000..."
echo "Логи будут сохранены в logs/server.log"

# Запуск в фоновом режиме с логированием
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/server.log 2>&1 &

# Получаем PID процесса
SERVER_PID=$!
echo "✅ Сервер запущен!"
echo "PID: $SERVER_PID"
echo "Логи: logs/server.log"

# Сохраняем PID для остановки
echo $SERVER_PID > logs/server.pid

# Проверяем, что сервер запустился
sleep 3
if pgrep -f "uvicorn" > /dev/null; then
    echo "✅ Сервер успешно запущен и работает!"
    echo "🌐 Доступен по адресу: http://localhost:8000"
    echo "🔗 Webhook: https://vm-fc7b7f29.na4u.ru/webhook"
else
    echo "❌ Ошибка запуска сервера!"
    echo "Проверьте логи: cat logs/server.log"
    exit 1
fi

echo ""
echo "📋 Полезные команды:"
echo "  Просмотр логов: tail -f logs/server.log"
echo "  Остановка: ./stop_server.sh"
echo "  Перезапуск: ./restart_server.sh"
echo "  Статус: ./status_server.sh"

