"""
Cliente para a API Hidroweb da Agência Nacional de Águas (ANA).

Este módulo fornece classes e funções para interagir com a API Hidroweb da ANA,
permitindo acesso a dados hidrológicos e pluviométricos de estações de monitoramento.

Para mais informações sobre a API, consulte:
https://www.ana.gov.br/hidrowebservice/swagger-ui/index.html#/

Classes
-------
ApiResponse
    Representa uma resposta da API Hidroweb.
Client
    Classe principal do cliente para interagir com a API.

Funções
---------
validate_df(df, required_columns)
    Valida se um DataFrame contém as colunas necessárias.
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
    """Representa uma resposta da API Hidroweb.

    Esta classe encapsula a resposta HTTP e fornece métodos convenientes
    para acessar os dados retornados pela API.

    Atributos
    ----------
    status_code : int
        O código de status HTTP da resposta.
    json : dict
        A resposta JSON completa da API.
    status : str ou None
        O campo status da resposta JSON.
    message : str ou None
        O campo message da resposta JSON.
    items : list, dict, ou None
        O campo items da resposta JSON, contendo os dados reais.
    """

    def __init__(self, response: httpx.Response):
        """Inicializa ApiResponse com um objeto httpx.Response.

        Parâmetros
        ----------
        response : httpx.Response
            A resposta HTTP da API.
        """
        self.status_code = response.status_code
        self.json = response.json()
        self.status = self.json.get("status")
        self.message = self.json.get("message")
        self.items = self.json.get("items")

    def is_success(self) -> bool:
        """Verifica se a resposta indica uma solicitação bem-sucedida.

        Retorna
        -------
        bool
            True se status_code estiver entre 200 e 299, False caso contrário.
        """
        return 200 <= self.status_code < 300

    def get_items(self) -> list | dict | None:
        """Obtém os items da resposta.

        Retorna
        -------
        list, dict, ou None
            O campo items da resposta JSON.
        """
        return self.items

    def items_as_dataframe(self) -> pd.DataFrame:
        """Converte os items para um DataFrame do pandas.

        Retorna
        -------
        pd.DataFrame
            Um DataFrame contendo os dados dos items. Se items for uma lista de dicionários,
            cada dicionário se torna uma linha. Se items for um único dicionário, torna-se uma única linha.
            Se items for None ou não for lista/dicionário, retorna um DataFrame vazio.
        """
        if isinstance(self.items, list):
            return pd.DataFrame(self.items)
        elif isinstance(self.items, dict):
            return pd.DataFrame([self.items])
        else:
            return pd.DataFrame()


def validate_df(df: pd.DataFrame, required_columns: list[str]) -> bool:
    """Valida se o DataFrame contém as colunas necessárias.

    Parâmetros
    ----------
    df : pd.DataFrame
        O DataFrame a ser validado.
    required_columns : list de str
        Lista de nomes de colunas que devem estar presentes no DataFrame.

    Retorna
    -------
    bool
        True se todas as colunas necessárias estiverem presentes.

        Exceções
        --------
        ValueError
            Se alguma coluna necessária estiver faltando.
    """
    print(df.columns)
    print(df)
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    return True


class Client:
    """Classe principal do cliente para interagir com a API Hidroweb da ANA.

    Esta classe lida com a autenticação e fornece métodos para buscar vários
    tipos de dados da API Hidroweb, como informações de bacias, entidades
    e inventários de estações.

    Atributos
    ----------
    user : str
        O nome de usuário para autenticação da API.
    password : str
        A senha para autenticação da API.
    client : httpx.AsyncClient
        O cliente HTTP usado para fazer solicitações.
    token : str ou None
        O token de autenticação obtido após o login.
    """

    def __init__(self, user=HIDROWEB_USER, password=HIDROWEB_PASSWORD):
        """Inicializa o Cliente com credenciais de usuário.

        Parâmetros
        ----------
        user : str, opcional
            Nome de usuário para autenticação da API. Padrão para a variável de ambiente HIDROWEB_USER.
        password : str, opcional
            Senha para autenticação da API. Padrão para a variável de ambiente HIDROWEB_PASSWORD.
        """
        self.user: str = user
        self.password: str = password
        self.client = httpx.AsyncClient(base_url=BASE_URL)
        self.token = None

    async def authenticate(self):
        """Autentica com a API Hidroweb e obtém um token de acesso.

        Este método envia uma solicitação GET para o endpoint OAuth com as credenciais do usuário
        para recuperar um token de autenticação, que é armazenado no cliente.

        Exceções
        --------
            Se a autenticação falhar ou nenhum token for retornado.
        """
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
        """Faz uma solicitação autenticada para a API Hidroweb.

        Este é um método interno que lida com a autenticação e tentativas em erros 401.

        Parâmetros
        ----------
        method : str, opcional
            Método HTTP (ex.: 'GET'). Padrão para 'GET'.
        endpoint_suffix : str, opcional
            O sufixo do endpoint da API a ser anexado à URL base.
        **kwargs
            Argumentos adicionais passados para a solicitação HTTP.

        Retorna
        -------
        httpx.Response
            A resposta HTTP da API.
        """
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
        """Busca dados da API e retorna como um DataFrame.

        Este é um método interno usado pelos métodos públicos para recuperar dados.

        Parâmetros
        ----------
        endpoint_suffix : str
            O sufixo do endpoint da API.
        params : dict, opcional
            Parâmetros de consulta para a solicitação.

        Retorna
        -------
        pd.DataFrame
            Os dados retornados pela API como um DataFrame do pandas.

            Exceções
            --------
                Se a solicitação da API falhar.
        """
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
        """Busca informações sobre bacias hidrológicas.

        Parâmetros
        ----------
        codigo : int, opcional
            Código da bacia para filtrar resultados.
        last_update_start : datetime, opcional
            Data de início para filtro de última atualização.
        last_update_end : datetime, opcional
            Data de fim para filtro de última atualização.

        Retorna
        -------
        pd.DataFrame ou None
            DataFrame contendo informações da bacia, ou None se não houver dados.
        """
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
        """Busca informações sobre entidades.

        Parâmetros
        ----------
        codigo : int, opcional
            Código da entidade para filtrar resultados.
        last_update_start : datetime, opcional
            Data de início para filtro de última atualização (aaaa-MM-dd).
        last_update_end : datetime, opcional
            Data de fim para filtro de última atualização (aaaa-MM-dd).

        Retorna
        -------
        pd.DataFrame ou None
            DataFrame contendo informações da entidade, ou None se não houver dados.
        """
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
        """Busca inventário de estações de monitoramento.

        Parâmetros
        ----------
        codigo : int, opcional
            Código da estação para filtrar resultados.
        last_update_start : datetime, opcional
            Data de início para filtro de última atualização (aaaa-MM-dd).
        last_update_end : datetime, opcional
            Data de fim para filtro de última atualização (aaaa-MM-dd).
        state : str, opcional
            Estado (Unidade Federativa) para filtrar resultados.
        basin_code : int, opcional
            Código da bacia para filtrar resultados.

        Retorna
        -------
        pd.DataFrame ou None
            DataFrame contendo inventário da estação, ou None se não houver dados.
        """
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
        """Fecha a sessão do cliente HTTP.

        Este método deve ser chamado quando o cliente não for mais necessário
        para fechar adequadamente as conexões HTTP subjacentes.
        """
        await self.client.aclose()
