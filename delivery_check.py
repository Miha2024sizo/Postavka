import requests
import time
import datetime

# Данные для Telegram
TOKEN = "7244566765:AAEBaDs19hw7-VrlF48jSGcLAE8x2vMhK_k"
CHAT_ID = "7253468898"

# Функция для отправки сообщения в Telegram
def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': text
    }
    response = requests.post(url, json=payload)
    
    if response.status_code != 200:
        print(f"Ошибка при отправке сообщения: {response.status_code}, Ответ: {response.text}")
    else:
        print(f"Сообщение успешно отправлено: {response.status_code}")

# Функция для получения информации о поставках на 2 дня вперед
def check_upcoming_deliveries():
    date_from = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "Z"  # Текущая дата
    date_to = (datetime.datetime.now() + datetime.timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S") + "Z"  # Дата через два дня
    
    url = "https://suppliers-api.wildberries.ru/api/v3/supplies"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQxMDAxdjEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc0Mzg2ODkyNiwiaWQiOiIwMTkyNWFkNy04MjgyLTc0MWUtOTU0Mi01OGUzYzEzMDhjMTQiLCJpaWQiOjUyOTkzOTUzLCJvaWQiOjM5MzY2MjAsInMiOjM4MzgsInNpZCI6IjkwZmU4Yjk0LTA2YmMtNDhmMy1iZDQ1LTBiOTI3Mjg4MDY1OSIsInQiOmZhbHNlLCJ1aWQiOjUyOTkzOTUzfQ.HkIuCmDb_gfaiW2pFWjCW-ZPojupC1_zGnkPK6xuWoI2FzBaAMQMNV3Onw_hle_7M3D0sxY2x5V3yxm5NsyQWw"
    }
    
    supply_types = ["x1", "x2", "x20"]
    
    payload = {
        "dateFrom": date_from,
        "dateTo": date_to,
        "supplyTypes": supply_types
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        deliveries = response.json().get("data", [])
        if deliveries:
            for delivery in deliveries:
                supply_id = delivery['id']
                supply_type = delivery['supplyType']
                delivery_date = delivery['date']
                
                # Запрос на получение полной информации о поставке
                details_url = f"https://suppliers-api.wildberries.ru/api/v3/supplies/{supply_id}/orders"
                details_response = requests.get(details_url, headers=headers)

                if details_response.status_code == 200:
                    details = details_response.json()
                    
                    # Проверяем, содержит ли информация о поставке необходимые данные
                    if 'data' in details and details['data']:
                        delivery_info = details['data'][0]  # Берем первую запись, если есть несколько
                        warehouse_info = delivery_info.get('warehouse', 'Информация о складе недоступна')
                        acceptance_time = delivery_info.get('acceptanceTime', 'Время приёмки недоступно')
                        reservation_date = delivery_info.get('reservationDate', 'Дата бронирования недоступна')

                        # Форматируем сообщение с деталями
                        formatted_message = (
                            f"📦 Поставка найдена!\n"
                            f"ID поставки: {supply_id}\n"
                            f"Тип поставки: {supply_type}\n"
                            f"Дата поставки: {delivery_date}\n"
                            f"Склад: {warehouse_info}\n"  
                            f"Время приёмки: {acceptance_time}\n"
                            f"Дата бронирования: {reservation_date}\n"
                        )
                        send_message(formatted_message)
                    else:
                        send_message(f"Детали поставки для ID {supply_id} недоступны.")
                else:
                    send_message(f"Не удалось получить детали для ID {supply_id}: статус {details_response.status_code}, Ответ: {details_response.text}")
        else:
            send_message("Поставок на ближайшие два дня нет.")
    else:
        send_message(f"Ошибка: статус {response.status_code}, Ответ: {response.text}")

# Запуск проверки поставок
while True:
    check_upcoming_deliveries()
    time.sleep(60)  # Проверяем каждую минуту
