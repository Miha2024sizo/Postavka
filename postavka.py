
import requests
from datetime import datetime, timedelta
import time

# Ваш токен Telegram
TOKEN = "7244566765:AAEBaDs19hw7-VrlF48jSGcLAE8x2vMhK_k"
CHAT_ID = "7253468898"

# Ваш токен для Wildberries API
headers = {
    'Authorization': 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQxMDAxdjEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc0Mzg2ODkyNiwiaWQiOiIwMTkyNWFkNy04MjgyLTc0MWUtOTU0Mi01OGUzYzEzMDhjMTQiLCJpaWQiOjUyOTkzOTUzLCJvaWQiOjM5MzY2MjAsInMiOjM4MzgsInNpZCI6IjkwZmU4Yjk0LTA2YmMtNDhmMy1iZDQ1LTBiOTI3Mjg4MDY1OSIsInQiOmZhbHNlLCJ1aWQiOjUyOTkzOTUzfQ.HkIuCmDb_gfaiW2pFWjCW-ZPojupC1_zGnkPK6xuWoI2FzBaAMQMNV3Onw_hle_7M3D0sxY2x5V3yxm5NsyQWw'
}

# Параметры запроса (пример для складов с ID 507 и 117501)
params = {
    'warehouseIDs': '507,117501,226,10109,223'
}

def send_telegram_message(message):
    """Отправка сообщения в Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'  # Форматирование в HTML (по желанию)
    }
    requests.post(url, json=payload)

def fetch_supplies():
    """Получение поставок и отправка сообщений при их наличии"""
    # Определяем даты от 2 до 14 дней вперёд
    future_dates = [(datetime.utcnow() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(2, 15)]

    # Выполнение GET запроса
    response = requests.get('https://supplies-api.wildberries.ru/api/v1/acceptance/coefficients', headers=headers, params=params)

    # Проверка результата запроса
    if response.status_code == 200:
        data = response.json()

        # Форматирование ответа
        formatted_output = ""

        for entry in data:
            date = entry['date'][:10]  # Извлечение только даты
            warehouse_name = entry['warehouseName']
            box_type_name = entry['boxTypeName']
            coefficient = entry['coefficient']

            # Фильтрация по коэффициентам и дате
            if coefficient in [1, 2, 20] and date in future_dates:
                # Форматирование строки для вывода
                formatted_output += (
                    f"🗓 Дата: {date}\n"
                    f"🏭 Склад: {warehouse_name}\n"
                    f"📦 Тип коробки: {box_type_name}\n"
                    f"📊 Коэффициент: {coefficient}\n\n"
                )

        # Если есть новые поставки, отправляем сообщение
        if formatted_output:
            send_telegram_message(formatted_output)
        else:
            print("Нет поставок с коэффициентами 1 или 2 на указанные даты.")
    else:
        print(f"Ошибка: {response.status_code}, {response.json()}")

# Основной цикл, который выполняет запрос каждую минуту
while True:
    fetch_supplies()
    time.sleep(60)  # Пауза на 60 секунд
