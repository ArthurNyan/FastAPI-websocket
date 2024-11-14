from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from observer import Subject
import httpx
import asyncio

app = FastAPI()
subject = Subject()

latest_rates = None

@app.get("/")
async def get():
    with open("templates/index.html", "r") as f:
        return HTMLResponse(f.read())

# Функция для отправки данных клиенту
async def send_data_to_client(websocket: WebSocket, data: dict):
    try:
        await websocket.send_json(data)
    except Exception as e:
        print(f"Ошибка отправки данных клиенту: {e}")

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    global latest_rates
    await websocket.accept()

    def observer(data: dict):
        asyncio.create_task(send_data_to_client(websocket, data))

    subject.attach(observer)

    # Отправить последние известные курсы сразу после подключения
    if latest_rates:
        await send_data_to_client(websocket, latest_rates)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subject.detach(observer)
        print(f"Client {client_id} disconnected")

# Получение данных от API
async def fetch_currency_rates():
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

# Мониторинг изменений курсов
async def monitor_currency_rates():
    global latest_rates
    previous_rates = None
    while True:
        data = await fetch_currency_rates()
        current_rates = data['Valute']

        if previous_rates is None or current_rates != previous_rates:
            latest_rates = current_rates
            subject.notify(current_rates)

        previous_rates = current_rates
        await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(monitor_currency_rates())
