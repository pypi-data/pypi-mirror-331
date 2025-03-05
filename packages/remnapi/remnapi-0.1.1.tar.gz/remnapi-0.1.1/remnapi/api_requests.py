import json
import uuid
import shortuuid
from datetime import datetime, timedelta
from controllers.users import UsersController
import asyncio

class UserManager:
    """
    Класс для управления пользователями через API.

    Основные методы:
    - add_user(username, **kwargs): Создает нового пользователя с указанным именем и параметрами.
    - get_users(): Возвращает список всех пользователей.
    - get_user(username, **kwargs): Получает информацию о пользователе по имени и фильтрует данные.
    - remove_user(username)

    Пример использования:
    manager = UserManager()
    manager.add_user('example', description='Новый пользователь', trafficLimitBytes=1073741824)
    manager.get_users()
    manager.get_user('example', username_filter=True, status_filter=True)
    """

    def __init__(self):
        self.users = UsersController()

    def _generate_dates(self, days=60):
        """
        Генерирует даты создания и истечения срока действия.

        Параметры:
        days (int): Количество дней до истечения срока. По умолчанию 60.

        Возвращает:
        tuple: (created_at, expire_at) в формате ISO 8601 с миллисекундами и 'Z' (UTC).
        """
        created_at = datetime.utcnow().isoformat(timespec='milliseconds') + "Z"
        expire_at = (datetime.utcnow() + timedelta(days=days)
                     ).isoformat(timespec='milliseconds') + "Z"
        return created_at, expire_at

    async def add_user(self, username, days, **kwargs):
        """
        Создает нового пользователя с указанным именем пользователя и дополнительными параметрами.

        Параметры:
        username (str): Имя пользователя для создания.

        **kwargs: Дополнительные параметры для создания пользователя. Если параметры не указаны, будут использованы значения по умолчанию.
            Возможные параметры:
            - subscriptionUuid (str): UUID подписки. По умолчанию генерируется автоматически.
            - shortUuid (str): Короткий UUID. По умолчанию генерируется автоматически.
            - trojanPassword (str): Пароль для Trojan. По умолчанию равен shortUuid.
            - vlessUuid (str): UUID для VLESS. По умолчанию равен subscriptionUuid.
            - ssPassword (str): Пароль для Shadowsocks. По умолчанию равен shortUuid.
            - trafficLimitBytes (int): Лимит трафика в байтах. По умолчанию 0 (без лимита).
            - trafficLimitStrategy (str): Стратегия лимита трафика. По умолчанию "NO_RESET".
            - expireAt (str): Дата истечения срока действия в формате ISO 8601. По умолчанию +60 дней от текущей даты.
            - createdAt (str): Дата создания в формате ISO 8601. По умолчанию текущая дата и время.
            - lastTrafficResetAt (str): Дата последнего сброса трафика. По умолчанию None.
            - description (str): Описание пользователя. По умолчанию пустая строка.
            - activateAllInbounds (bool): Активировать все inbound подключения. По умолчанию True.

        Возвращает:
        dict: Созданный пользователь.

        Пример:
        add_user('example', description='Новый пользователь', trafficLimitBytes=1073741824)
        Это создаст пользователя с именем 'example', описанием 'Новый пользователь' и лимитом трафика 1 ГБ.
        """
        # Генерация значений по умолчанию
        vless_uuid = str(uuid.uuid4())
        short_uuid = str(shortuuid.uuid())
        traffic_limit_bytes = 0
        # Получаем даты
        created_at, expire_at = self._generate_dates(kwargs.pop('days', days))

        # Параметры по умолчанию
        default_params = {
            "subscriptionUuid": vless_uuid,
            "shortUuid": short_uuid,
            "trojanPassword": short_uuid,
            "vlessUuid": vless_uuid,
            "ssPassword": short_uuid,
            "trafficLimitBytes": traffic_limit_bytes,
            "trafficLimitStrategy": "NO_RESET",
            "expireAt": expire_at,
            "createdAt": created_at,
            "lastTrafficResetAt": None,
            "description": "",
            "activateAllInbounds": True
        }

        # Обновляем параметры по умолчанию переданными значениями из kwargs
        default_params.update(kwargs)

        # Создаем пользователя
        user = await self.users.create_user(username, **default_params)
        return user

    async def get_users(self):
        """
        Возвращает список всех пользователей.

        Возвращает:
        list: Список пользователей.
        """
        users = await self.users.get_users()
        print("Список пользователей:", users)
        return users

    
    async def get_user(self, username, all=False, **kwargs):
        """
        Получает информацию о пользователе по имени пользователя.

        Параметры:
            username (str): Имя пользователя для получения информации.
            all (bool, необязательно): Если True, возвращает полный ответ от сервера.

        **kwargs: Фильтры для извлечения определённых данных.
        Возможные параметры (устанавливаются в True):
            - username_filter (bool): Возвращает имя пользователя.
            - status_filter (bool): Возвращает статус пользователя.
            - expireAt_filter (bool): Возвращает дату истечения подписки.
            - createdAt_filter (bool): Возвращает дату создания пользователя.
            - updatedAt_filter (bool): Возвращает дату последнего обновления пользователя.
            - usedTrafficBytes_filter (bool): Возвращает использованный трафик.
            - lifetimeUsedTrafficBytes_filter (bool): Возвращает общий использованный трафик.
            - trafficLimitBytes_filter (bool): Возвращает лимит трафика.
            - subscriptionUuid_filter (bool): Возвращает UUID подписки.
            - shortUuid_filter (bool): Возвращает короткий UUID.
            - uuid_filter (bool): Возвращает полный UUID.
            - activeUserInbounds_filter (bool): Возвращает активные inbound-подключения.
            - description_filter (bool): Возвращает описание пользователя.

        Пример:
            get_user('nvwrist')  # Вернёт весь ответ
            get_user('nvwrist', all=True)  # Вернёт весь ответ
            get_user('nvwrist', username_filter=True, status_filter=True)  # Вернёт только имя пользователя и статус.

        Возвращает:
        dict: Полный ответ от сервера или отфильтрованные данные.
        """
        # Получаем полный ответ от API
        response = await self.users.get_user_by_username(username)
        user = response.get('response', {})

        # Если all=True или не переданы фильтры, возвращаем полный ответ
        if all or not kwargs:
            return user

        # Фильтруем данные по переданным параметрам
        filtered_data = {
            key.replace('_filter', ''): user.get(key.replace('_filter', ''))
            for key, value in kwargs.items() if value
        }

        return filtered_data

    async def remove_user(self, username):
        """
        Удаляет пользователя по имени пользователя.

        Параметры:
        username (str): Имя пользователя, которого необходимо удалить.

        Исключения:
        ValueError: Выбрасывается, если UUID пользователя не найден.

        Пример:
        remove_user_by_username('testers')
        """
        user_data = await UserManager().get_user(username, uuid_filter=True)

        if not user_data or "uuid" not in user_data:
            raise ValueError(f"UUID для пользователя {username} не найден")

        return await self.users.delete_user(str(user_data["uuid"]))

async def main():
    manager = UserManager()
    
    # Создание пользователя
    new_user = await manager.add_user("testuser", days=30)
    print("Создан пользователь:", new_user) 

    # Получение информации
    #username = await manager.get_user("testuser")
    #username = await manager.get_user("testuser", username_filter = True, shortUuid_filter=True, status_filter = True)
    #print("Информация о пользователе:\n", username)
#
    ## Список всех пользователей
    #users = await manager.get_users()
    #print("Список пользователей:", users)
#
    ## Удаление пользователя
    #delete_response = await manager.remove_user("testuser")
    #print("Удаление пользователя:", delete_response)

asyncio.run(main())