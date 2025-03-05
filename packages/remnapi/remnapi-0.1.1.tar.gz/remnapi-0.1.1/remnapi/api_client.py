import os
import requests
from dotenv import load_dotenv
import asyncio
import aiohttp

load_dotenv()  # Загружаем переменные окружения из .env


class APIClient:
    BASE_URL = os.getenv("PANEL_URL")  # Базовый URL API

    def __init__(self):
        self.token = os.getenv("API_TOKEN")  # Читаем токен из .env
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}" if self.token else None
        }

    async def request(self, method, endpoint, **kwargs):
        """Базовый метод для всех запросов."""
        url = f"{self.BASE_URL}{endpoint}"
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=self.headers, **kwargs) as response:
                if response.status == 401:
                    raise Exception("Unauthorized: Проверьте токен API")
                elif response.status >= 400:
                    raise Exception(f"Ошибка {response.status}: {await response.text()}")
                return await response.json()
