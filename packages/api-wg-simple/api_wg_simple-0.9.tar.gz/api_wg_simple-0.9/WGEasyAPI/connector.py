import json
import logging
import aiohttp
from pydantic import BaseModel
from typing import Union, List, Optional


class NotAuthenticatedError(Exception):
    pass


class ClientRequest(BaseModel):
    name: str
    expired_date: str = ""


class WGEasyAPIConnector:
    def __init__(self, base_url: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api"
        self.password = password
        self.session: Optional[aiohttp.ClientSession] = None
        self.cookies = None
        self._client_cache: Optional[List[dict]] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self.authenticate()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def authenticate(self):
        """Авторизация на сервере, установка cookies"""
        async with self.session.post(f"{self.api_url}/session", data={"password": self.password}) as resp:
            if resp.status != 200:
                raise NotAuthenticatedError("Authentication failed")
            self.cookies = resp.cookies

    async def get_client_id_by_name(self, name: str, cache: bool = True) -> Optional[str]:
        """Получает ID клиента по имени"""
        if cache and self._client_cache:
            clients = self._client_cache
        else:
            clients = await self.get_clients()
            self._client_cache = clients

        if not clients:
            logging.warning("Client list is empty.")
            return None

        for client in clients:
            if client.get("name") == name:
                return client.get("id")

        logging.warning(f"Client with name '{name}' not found")
        return None

    async def _request(self, method: str, path: str, data: Union[BaseModel, dict, None] = None, params: dict = None):
        """Универсальный метод для работы с API"""
        url = f"{self.api_url}/{path}"
        headers = {"Content-Type": "application/json"}

        if isinstance(data, BaseModel):
            data = data.model_dump()

        try:
            async with self.session.request(method, url, json=data, params=params, headers=headers, cookies=self.cookies) as resp:
                text = await resp.text()
                content_type = resp.headers.get("Content-Type", "")

                if "application/json" in content_type:
                    return json.loads(text)

                return text

        except aiohttp.ClientError as e:
            logging.error(f"HTTP request failed: {e}")
            raise Exception("Internal server error") from e

    async def get_clients(self) -> List[dict]:
        """Получение списка клиентов"""
        try:
            return await self._request("GET", "wireguard/client") or []
        except Exception as e:
            logging.error(f"Failed to get clients: {e}")
            return []

    async def create_client(self, client_request: ClientRequest) -> bool:
        """Создание клиента"""
        response = await self._request("POST", "wireguard/client", data=client_request)
        if response.get("success", False):
            self._client_cache = None
            return True
        return False

    async def get_client_config(self, client_name: str) -> Optional[str]:
        """Получение конфигурации клиента"""
        client_id = await self.get_client_id_by_name(client_name)
        if not client_id:
            return None
        return await self._request("GET", f"wireguard/client/{client_id}/configuration")

    async def disable_config(self, client_name: str) -> Optional[str]:
        """Отключение конфигурации клиента"""
        client_id = await self.get_client_id_by_name(client_name)
        if not client_id:
            return None
        return await self._request("POST", f"wireguard/client/{client_id}/disable")

    async def enable_config(self, client_name: str) -> Optional[str]:
        """Включение конфигурации клиента"""
        client_id = await self.get_client_id_by_name(client_name)
        if not client_id:
            return None
        return await self._request("POST", f"wireguard/client/{client_id}/enable")
