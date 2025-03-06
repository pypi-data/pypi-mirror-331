# RemnAPI

Клиент для работы с API пользователей.

## Установка
pip install -r requirements.txt

```python
certifi==2025.1.31
charset-normalizer==3.4.1
idna==3.10
python-dotenv==1.0.1
requests==2.32.3
shortuuid==1.0.13
urllib3==2.3.0
```

pip install remnapi

## Использование
```python
from remnapi import UserManager

async def main():
    manager = UserManager()
    
    # Создание пользователя
    new_user = await manager.add_user("testuser", days=30) # return JSON


    # Получение информации
    username = await manager.get_user("testuser") # return JSON
    username_filter = await manager.get_user("testuser", username_filter = True, shortUuid_filter=True, status_filter = True) # return filtred JSON

    # Список всех пользователей
    users = await manager.get_users() # return JSON


    ## Удаление пользователя
    delete_response = await manager.remove_user("testuser") # return JSON

asyncio.run(main())