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

    async def create_user(self, username, status="ACTIVE", **kwargs):
        """Создание нового пользователя."""
        data = {"username": username, "status": status, **kwargs}
        return await self.request("POST", "/users", json=data)

    async def get_users(self, params=None):
        """Получение списка пользователей."""
        return await self.request("GET", "/users/v2", params=params)

    async def get_user(self, user_id):
        """Получение информации о конкретном пользователе."""
        return await self.request("GET", f"/users/{user_id}")
    
    async def get_user_by_username(self, username):
        return await self.request("GET", f"/users/username/{username}")

    async def update_user(self, user_id, **kwargs):
        """Обновление данных пользователя."""
        return await self.request("PATCH", f"/users/{user_id}", json=kwargs)

    async def delete_user(self, user_uuid):
        """Удаление пользователя."""
        return await self.request("DELETE", f"/users/delete/{user_uuid}")
