"""
Client for the Brazilian National Water Agency (ANA) Hidroweb API.
Documentation: https://www.ana.gov.br/hidrowebservice/swagger-ui/index.html#/
"""

import os
import httpx
import asyncio
import pandas as pd
from datetime import datetime


BASE_URL = "https://www.ana.gov.br/hidrowebservice/EstacoesTelemetricas/"
HIDROWEB_USER = os.getenv("HIDROWEB_USER") or "user"
HIDROWEB_PASSWORD = os.getenv("HIDROWEB_PASSWORD") or "password"

ParamsType = (
    dict[str, int] | dict[str, str] | dict[str, datetime] | dict[str, None] | None
)


class ApiResponse:
    def __init__(self, response: httpx.Response):
        self.status_code = response.status_code
        self.json = response.json()
        self.status = self.json.get("status")
        self.message = self.json.get("message")
        self.items = self.json.get("items")

    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    def get_items(self) -> list | dict | None:
        return self.items

    def items_as_dataframe(self) -> pd.DataFrame:
        if isinstance(self.items, list):
            return pd.DataFrame(self.items)
        elif isinstance(self.items, dict):
            return pd.DataFrame([self.items])
        else:
            return pd.DataFrame()


def validate_df(df: pd.DataFrame, required_columns: list[str]) -> bool:
    """Validate if the DataFrame contains the required columns."""
    print(df.columns)
    print(df)
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    return True


class Client:
    def __init__(self, user=HIDROWEB_USER, password=HIDROWEB_PASSWORD):
        self.user: str = user
        self.password: str = password
        self.client = httpx.AsyncClient(base_url=BASE_URL)
        self.token = None

    async def authenticate(self):
        url = "OAUth/v1"
        headers = {"Identificador": self.user, "Senha": self.password}
        response = await self.client.get(url, headers=headers)
        if response.status_code != 200:
            message = response.json().get("message", "No message provided")
            raise Exception(
                f"Authentication failed: ({response.status_code}) {message}"
            )
        token = response.json().get("items", {}).get("tokenautenticacao")
        if not token:
            raise Exception("Authentication token not found in response")
        self.token = token

    async def _make_request(
        self, method: str = "GET", endpoint_suffix: str = "", **kwargs
    ):
        """Make an authenticated request to the Hidroweb API."""
        url = endpoint_suffix
        headers = kwargs.pop("headers", {})
        if not self.token:
            await self.authenticate()
        headers["Authorization"] = f"Bearer {self.token}"
        response = await self.client.request(method, url, headers=headers, **kwargs)
        if response.status_code == 401:
            await self.authenticate()
            headers["Authorization"] = f"Bearer {self.token}"
            response = await self.client.request(method, url, headers=headers, **kwargs)
        return response

    async def _df_from_api(
        self, endpoint_suffix: str, params: dict[object, object] = None
    ) -> pd.DataFrame:
        response = await self._make_request("GET", endpoint_suffix, params=params)
        if response.status_code != 200:
            message = response.json().get("message", response.text)
            raise Exception(
                f"Failed to fetch data from {endpoint_suffix}: ({response.status_code}) {message}"
            )
        return ApiResponse(response).items_as_dataframe()

    async def bacias(
        self,
        codigo: int | None = None,
        last_update_start: datetime | None = None,
        last_update_end: datetime | None = None,
    ) -> pd.DataFrame | None:
        endpoint_suffix = "HidroBacia/v1"
        params = {}
        if codigo is not None:
            params["Código da Bacia"] = codigo
        if last_update_start is not None:
            params["Data Atualização Inicial"] = last_update_start.strftime("%Y-%m-%d")
        if last_update_end is not None:
            params["Data Atualização Final"] = last_update_end.strftime("%Y-%m-%d")
        return await self._df_from_api(endpoint_suffix, params)

    async def entidades(
        self,
        codigo: int | None = None,
        last_update_start: datetime | None = None,
        last_update_end: datetime | None = None,
    ) -> pd.DataFrame | None:
        endpoint_suffix = "HidroEntidade/v1"
        params = {}
        if codigo is not None:
            params["Código da Entidade"] = codigo
        if last_update_start is not None:
            params["Data Atualização Inicial (yyyy-MM-dd)"] = (
                last_update_start.strftime("%Y-%m-%d")
            )
        if last_update_end is not None:
            params["Data Atualização Final (yyyy-MM-dd)"] = last_update_end.strftime(
                "%Y-%m-%d"
            )
        return await self._df_from_api(endpoint_suffix, params)

    async def estacoes(
        self,
        codigo: int | None = None,
        last_update_start: datetime | None = None,
        last_update_end: datetime | None = None,
        state: str | None = None,
        basin_code: int | None = None,
    ) -> pd.DataFrame | None:
        endpoint_suffix = "HidroInventarioEstacoes/v1"
        params = {}
        if codigo is not None:
            params["Código da Estação"] = codigo
        if last_update_start is not None:
            params["Data Atualização Inicial (yyyy-MM-dd)"] = (
                last_update_start.strftime("%Y-%m-%d")
            )
        if last_update_end is not None:
            params["Data Atualização Final (yyyy-MM-dd)"] = last_update_end.strftime(
                "%Y-%m-%d"
            )
        if state is not None:
            params["Unidade Federativa"] = state

        if basin_code is not None:
            params["Código da Bacia"] = basin_code
        return await self._df_from_api(endpoint_suffix, params)

    async def close(self):
        await self.client.aclose()
