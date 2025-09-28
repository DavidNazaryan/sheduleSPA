#!/bin/bash
# Скрипт для остановки сервера
# Сохраните как stop_server.sh и сделайте исполняемым: chmod +x stop_server.sh

echo "🛑 Остановка сервера расписания МГУ"
echo "===================================="

# Проверяем, запущен ли сервер
if ! pgrep -f "uvicorn" > /dev/null; then
    echo "⚠️ Сервер не запущен!"
    exit 1
fi

# Получаем PID процесса
SERVER_PID=$(pgrep -f uvicorn)
echo "Найден процесс с PID: $SERVER_PID"

# Останавливаем сервер
echo "🛑 Останавливаем сервер..."
kill $SERVER_PID

# Ждем завершения процесса
sleep 2

# Проверяем, что процесс завершился
if pgrep -f "uvicorn" > /dev/null; then
    echo "⚠️ Процесс не завершился, принудительная остановка..."
    kill -9 $SERVER_PID
    sleep 1
fi

# Проверяем результат
if ! pgrep -f "uvicorn" > /dev/null; then
    echo "✅ Сервер успешно остановлен!"
    
    # Удаляем файл PID
    if [ -f "logs/server.pid" ]; then
        rm logs/server.pid
    fi
else
    echo "❌ Не удалось остановить сервер!"
    exit 1
fi

echo ""
echo "📋 Для запуска используйте: ./start_server.sh"

