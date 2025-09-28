#!/bin/bash
# Скрипт для перезапуска сервера
# Сохраните как restart_server.sh и сделайте исполняемым: chmod +x restart_server.sh

echo "🔄 Перезапуск сервера расписания МГУ"
echo "===================================="

# Проверяем, запущен ли сервер
if pgrep -f "uvicorn" > /dev/null; then
    SERVER_PID=$(pgrep -f uvicorn)
    echo "🛑 Останавливаем текущий сервер (PID: $SERVER_PID)..."
    
    # Останавливаем сервер
    kill $SERVER_PID
    
    # Ждем завершения процесса
    sleep 3
    
    # Проверяем, что процесс завершился
    if pgrep -f "uvicorn" > /dev/null; then
        echo "⚠️ Процесс не завершился, принудительная остановка..."
        kill -9 $SERVER_PID
        sleep 1
    fi
    
    # Проверяем результат
    if ! pgrep -f "uvicorn" > /dev/null; then
        echo "✅ Сервер успешно остановлен!"
    else
        echo "❌ Не удалось остановить сервер!"
        exit 1
    fi
else
    echo "ℹ️ Сервер не запущен, пропускаем остановку"
fi

# Ждем немного перед запуском
echo "⏳ Ждем 2 секунды перед запуском..."
sleep 2

# Запускаем сервер
echo "🚀 Запускаем сервер..."
cd /var/www/schedule-spa

# Проверяем наличие файлов
if [ ! -f "app/main.py" ]; then
    echo "❌ Файл app/main.py не найден!"
    echo "Убедитесь, что вы находитесь в правильной директории"
    exit 1
fi

# Создаем директорию для логов
mkdir -p logs

# Запускаем сервер в фоновом режиме
echo "🌐 Запускаем сервер на порту 8000..."
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
echo "  Статус: ./status_server.sh"
echo "  Перезапуск: ./restart_server.sh"
