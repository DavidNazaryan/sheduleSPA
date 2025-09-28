#!/bin/bash
# Скрипт для проверки статуса сервера (исправленная версия)
# Сохраните как status_server.sh и сделайте исполняемым: chmod +x status_server.sh

echo "📊 Статус сервера расписания МГУ"
echo "================================="

# Проверяем, запущен ли сервер
if pgrep -f "uvicorn" > /dev/null; then
    SERVER_PID=$(pgrep -f uvicorn | head -1)
    echo "✅ Сервер запущен"
    echo "PID: $SERVER_PID"
    
    # Проверяем порт
    if netstat -tlnp 2>/dev/null | grep -q ":8000"; then
        echo "✅ Порт 8000 открыт"
    else
        echo "❌ Порт 8000 не открыт"
    fi
    
    # Проверяем использование памяти (исправленная версия)
    echo ""
    echo "🧠 Использование ресурсов:"
    if [ ! -z "$SERVER_PID" ]; then
        ps -p $SERVER_PID -o pid,ppid,cmd,%mem,%cpu,etime 2>/dev/null || echo "Не удалось получить информацию о процессе"
    else
        echo "PID не найден"
    fi
    
    # Проверяем доступность
    echo ""
    echo "🌐 Проверка доступности:"
    if curl -s http://localhost:8000 > /dev/null; then
        echo "✅ Локальный доступ работает"
    else
        echo "❌ Локальный доступ не работает"
    fi
    
    if curl -s https://vm-fc7b7f29.na4u.ru > /dev/null; then
        echo "✅ Внешний доступ работает"
    else
        echo "❌ Внешний доступ не работает"
    fi
    
    # Показываем последние логи
    echo ""
    echo "📝 Последние логи:"
    if [ -f "logs/server.log" ]; then
        tail -n 5 logs/server.log
    else
        echo "Логи не найдены"
    fi
    
else
    echo "❌ Сервер не запущен"
    echo ""
    echo "📋 Для запуска используйте: ./start_server.sh"
fi

echo ""
echo "🔗 Полезные ссылки:"
echo "  Локальный сервер: http://localhost:8000"
echo "  Внешний сервер: https://vm-fc7b7f29.na4u.ru"
echo "  Webhook: https://vm-fc7b7f29.na4u.ru/webhook"
echo "  Telegram бот: https://t.me/scheduleSPAbot"

