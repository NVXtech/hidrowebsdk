"""
Cliente para a API Hidroweb da Agência Nacional de Águas (ANA).

Este pacote fornece uma interface para acessar os dados hidrológicos
disponíveis no Hidroweb da Agência Nacional de Águas (ANA) via API oficial.

Para mais informações sobre a API, consulte:
https://www.ana.gov.br/hidrowebservice/swagger-ui/index.html#/

Classes
-------
ApiResponse
    Representa uma resposta da API Hidroweb.
Client
    Classe principal do cliente para interagir com a API.
"""

import os
import json
import httpx
import pandas as pd
from datetime import datetime
from enum import Enum


class DateFilter(Enum):
    MEASUREMENT_DATE = "DATA_LEITURA"
    LAST_UPDATE_DATE = "DATA_ULTIMA_ATUALIZACAO"


class RangeFilter(Enum):
    FIVE_MINUTES = "MINUTO_5"
    TEN_MINUTES = "MINUTO_10"
    FIFTEEN_MINUTES = "MINUTO_15"
    THIRTY_MINUTES = "MINUTO_30"
    ONE_HOUR = "HORA_1"
    TWO_HOURS = "HORA_2"
    THREE_HOURS = "HORA_3"
    FOUR_HOURS = "HORA_4"
    FIVE_HOURS = "HORA_5"
    SIX_HOURS = "HORA_6"
    SEVEN_HOURS = "HORA_7"
    EIGHT_HOURS = "HORA_8"
    NINE_HOURS = "HORA_9"
    TEN_HOURS = "HORA_10"
    ELEVEN_HOURS = "HORA_11"
    TWELVE_HOURS = "HORA_12"
    THIRTEEN_HOURS = "HORA_13"
    FOURTEEN_HOURS = "HORA_14"
    FIFTEEN_HOURS = "HORA_15"
    SIXTEEN_HOURS = "HORA_16"
    SEVENTEEN_HOURS = "HORA_17"
    EIGHTEEN_HOURS = "HORA_18"
    NINETEEN_HOURS = "HORA_19"
    TWENTY_HOURS = "HORA_20"
    TWENTY_ONE_HOURS = "HORA_21"
    TWENTY_TWO_HOURS = "HORA_22"
    TWENTY_THREE_HOURS = "HORA_23"
    TWENTY_FOUR_HOURS = "HORA_24"
    ONE_DAY = "HORA_24"
    TWO_DAYS = "DIA_2"
    SEVEN_DAYS = "DIA_7"
    FOURTEEN_DAYS = "DIA_14"
    TWENTY_ONE_DAYS = "DIA_21"
    THIRTY_DAYS = "DIA_30"


BASE_URL = "https://www.ana.gov.br/hidrowebservice/EstacoesTelemetricas/"
HIDROWEB_USER = os.getenv("HIDROWEB_USER") or "user"
HIDROWEB_PASSWORD = os.getenv("HIDROWEB_PASSWORD") or "password"


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
        self.json = self.json_from_response(response)
        self.status = self.json.get("status")
        self.message = self.json.get("message")
        self.items = self.json.get("items")

    def charset_from_response(self, response: httpx.Response) -> str:
        charset = "utf-8"  # default charset
        content_type = response.headers.get("Content-Type", "")
        if "charset=" in content_type:
            charset = content_type.split("charset=")[-1]
        return charset

    def json_from_response(self, response: httpx.Response) -> dict:
        return json.loads(response.content.decode(self.charset_from_response(response)))

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
        api_response = ApiResponse(response)
        if response.status_code != 200:
            raise Exception(
                f"Authentication failed: ({response.status_code}) {api_response.message}"
            )
        token = api_response.items.get("tokenautenticacao")
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
        api_response = ApiResponse(response)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch data from {endpoint_suffix}: ({response.status_code}) {api_response.message}"
            )
        return api_response.items_as_dataframe()

    async def estados(
        self,
        codigo: int | None = None,
        last_update_start: datetime | None = None,
        last_update_end: datetime | None = None,
    ) -> pd.DataFrame:
        """Busca informações sobre estados (Unidades Federativas).

        Parâmetros
        ----------
        codigo : int, opcional
            Código do estado para filtrar resultados.
        last_update_start : datetime, opcional
            Data de início para filtro de última atualização.
        last_update_end : datetime, opcional
            Data de fim para filtro de última atualização.

        Retorna
        -------
        pd.DataFrame
            DataFrame contendo informações dos estados.
        """
        endpoint_suffix = "HidroUF/v1"
        params = {}
        if codigo is not None:
            params["Código da UF"] = codigo
        if last_update_start is not None:
            params["Data Atualização Inicial"] = last_update_start.strftime("%Y-%m-%d")
        if last_update_end is not None:
            params["Data Atualização Final"] = last_update_end.strftime("%Y-%m-%d")
        return await self._df_from_api(endpoint_suffix, params)

    async def municipios(
        self,
        codigo: int | None = None,
        last_update_start: datetime | None = None,
        last_update_end: datetime | None = None,
    ) -> pd.DataFrame:
        """Busca informações sobre municípios.

        Parâmetros
        ----------
        codigo : int, opcional
            Código do município para filtrar resultados.
        last_update_start : datetime, opcional
            Data de início para filtro de última atualização.
        last_update_end : datetime, opcional
            Data de fim para filtro de última atualização.

        Retorna
        -------
        pd.DataFrame ou None
            DataFrame contendo informações do município
        """
        endpoint_suffix = "HidroMunicipio/v1"
        params = {}
        if codigo is not None:
            params["Código do Município"] = codigo
        if last_update_start is not None:
            params["Data Atualização Inicial"] = last_update_start.strftime("%Y-%m-%d")
        if last_update_end is not None:
            params["Data Atualização Final"] = last_update_end.strftime("%Y-%m-%d")
        return await self._df_from_api(endpoint_suffix, params)

    async def bacias(
        self,
        codigo: int | None = None,
        last_update_start: datetime | None = None,
        last_update_end: datetime | None = None,
    ) -> pd.DataFrame:
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
            DataFrame contendo informações da bacia
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

    async def sub_bacias(
        self,
        codigo: int | None = None,
        last_update_start: datetime | None = None,
        last_update_end: datetime | None = None,
    ) -> pd.DataFrame:
        """Busca informações sobre sub-bacias hidrológicas.

        Parâmetros
        ----------
        codigo : int, opcional
            Código da sub-bacia para filtrar resultados.
        last_update_start : datetime, opcional
            Data de início para filtro de última atualização.
        last_update_end : datetime, opcional
            Data de fim para filtro de última atualização.

        Retorna
        -------
        pd.DataFrame ou None
            DataFrame contendo informações da sub-bacia
        """
        endpoint_suffix = "HidroSubBacia/v1"
        params = {}
        if codigo is not None:
            params["Código da Sub-Bacia"] = codigo
        if last_update_start is not None:
            params["Data Atualização Inicial"] = last_update_start.strftime("%Y-%m-%d")
        if last_update_end is not None:
            params["Data Atualização Final"] = last_update_end.strftime("%Y-%m-%d")
        return await self._df_from_api(endpoint_suffix, params)

    async def rios(
        self,
        codigo: int | None = None,
        last_update_start: datetime | None = None,
        last_update_end: datetime | None = None,
    ) -> pd.DataFrame:
        """Busca informações sobre rios.

        Parâmetros
        ----------
        codigo : int, opcional
            Código do rio para filtrar resultados.
        last_update_start : datetime, opcional
            Data de início para filtro de última atualização.
        last_update_end : datetime, opcional
            Data de fim para filtro de última atualização.

        Retorna
        -------
        pd.DataFrame ou None
            DataFrame contendo informações do rio
        """
        endpoint_suffix = "HidroRio/v1"
        params = {}
        if codigo is not None:
            params["Código do Rio"] = codigo
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
    ) -> pd.DataFrame:
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
        pd.DataFrame
            DataFrame contendo informações da entidade
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
    ) -> pd.DataFrame:
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
            DataFrame contendo inventário da estação.
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

    async def estacoes_hidrosat(
        self,
        codigo: str = "",
        last_update_start: datetime | None = None,
        last_update_end: datetime | None = None,
    ) -> pd.DataFrame:
        """Busca inventário de estações de monitoramento.

        Parâmetros
        ----------
        codigo : str, opcional
            Código da estação para filtrar resultados.
        last_update_start : datetime, opcional
            Data de início para filtro de última atualização (aaaa-MM-dd).
        last_update_end : datetime, opcional
            Data de fim para filtro de última atualização (aaaa-MM-dd).

        Retorna
        -------
        pd.DataFrame
            DataFrame contendo inventário da estação.
        """
        endpoint_suffix = "HidrosatInventarioEstacoes/v1"
        params = {}
        if codigo:
            params["Código da Estação"] = codigo
        if last_update_start is not None:
            params["Data Atualização Inicial (yyyy-MM-dd)"] = (
                last_update_start.strftime("%Y-%m-%d")
            )
        if last_update_end is not None:
            params["Data Atualização Final (yyyy-MM-dd)"] = last_update_end.strftime(
                "%Y-%m-%d"
            )
        return await self._df_from_api(endpoint_suffix, params)

    async def _telemetry_method(
        self,
        endpoint_suffix: str,
        codigo: int,
        end_datetime: datetime | None = None,
        date_filter: DateFilter = DateFilter.MEASUREMENT_DATE,
        range_filter: RangeFilter = RangeFilter.ONE_DAY,
    ) -> pd.DataFrame:
        params = {
            "Código da Estação": codigo,
            "Tipo Filtro Data": date_filter.value,
            "Range Intervalo de busca": range_filter.value,
        }
        if end_datetime is not None:
            params["Data de Busca (yyyy-MM-dd)"] = (end_datetime.strftime("%Y-%m-%d"),)
        return await self._df_from_api(endpoint_suffix, params)

    async def _telemetry_multi_station(
        self,
        endpoint_suffix: str,
        codigos: list[int],
        end_datetime: datetime | None = None,
        date_filter: DateFilter = DateFilter.MEASUREMENT_DATE,
        range_filter: RangeFilter = RangeFilter.ONE_DAY,
    ) -> pd.DataFrame:
        params = {
            "Codigos_Estacoes": ",".join(map(str, codigos)),
            "Tipo Filtro Data": date_filter.value,
            "Range Intervalo de busca": range_filter.value,
        }
        if end_datetime is not None:
            params["Data de Busca (yyyy-MM-dd)"] = (end_datetime.strftime("%Y-%m-%d"),)
        print(params)
        return await self._df_from_api(endpoint_suffix, params)

    async def serie_telemetrica_detalhada(
        self,
        codigo: int,
        end_datetime: datetime | None = None,
        date_filter: DateFilter = DateFilter.MEASUREMENT_DATE,
        range_filter: RangeFilter = RangeFilter.ONE_DAY,
    ) -> pd.DataFrame:
        """Busca série histórica detalhada de dados telemétricos para uma estação específica.

        Parâmetros
        ----------
        codigo : int
            Código da estação para a qual buscar os dados.
        end_datetime : datetime
            Data e hora de final do intervalo para buscar os dados.
        filter_type : DateFilter, opcional
            Tipo de filtro de data a ser usado data da medição (FilterDate.MEASUREMENT_DATE) ou data da última atualização (FilterDate.LAST_UPDATE_DATE).
            Padrão para data da medição (FilterDate.MEASUREMENT_DATE).
        range_filter : RangeFilter, opcional
            Intervalo de busca termina no dia final (end_datetime) e inicia no dia final menos o intervalo.
            O padrão é o intevalo de um dia (RangeFilter.ONE_DAY), isto é, será buscado dados para o dia inteiro.
            O valor máximo permitido é de 30 dias (RangeFilter.THIRTY_DAYS) e o menor de 5 minutos (Rangefilter.FIVE_MINUTES).

        Retorna
        -------
        pd.DataFrame
            DataFrame contendo a série histórica detalhada de dados telemétricos.
        """
        endpoint_suffix = "HidroinfoanaSerieTelemetricaDetalhada/v1"
        return await self._telemetry_method(
            endpoint_suffix, codigo, end_datetime, date_filter, range_filter
        )

    async def serie_telemetrica_adotada(
        self,
        codigo: int,
        end_datetime: datetime | None = None,
        date_filter: DateFilter = DateFilter.MEASUREMENT_DATE,
        range_filter: RangeFilter = RangeFilter.ONE_DAY,
    ) -> pd.DataFrame:
        """Busca série histórica adotada de dados telemétricos para uma estação específica(cota, nível e vazão).


        Parâmetros
        ----------
        codigo : int
            Código da estação para a qual buscar os dados.
        end_datetime : datetime
            Data e hora de final do intervalo para buscar os dados.
        filter_type : DateFilter, opcional
            Tipo de filtro de data a ser usado data da medição (FilterDate.MEASUREMENT_DATE) ou data da última atualização (FilterDate.LAST_UPDATE_DATE).
            Padrão para data da medição (FilterDate.MEASUREMENT_DATE).
        range_filter : RangeFilter, opcional
            Intervalo de busca termina no dia final (end_datetime) e inicia no dia final menos o intervalo.
            O padrão é o intevalo de um dia (RangeFilter.ONE_DAY), isto é, será buscado dados para o dia inteiro.
            O valor máximo permitido é de 30 dias (RangeFilter.THIRTY_DAYS) e o menor de 5 minutos (Rangefilter.FIVE_MINUTES).

        Retorna
        -------
        pd.DataFrame
            DataFrame contendo a série histórica adotada de dados telemétricos.
        """
        endpoint_suffix = "HidroinfoanaSerieTelemetricaAdotada/v1"
        return await self._telemetry_method(
            endpoint_suffix, codigo, end_datetime, date_filter, range_filter
        )

    async def serie_telemetrica_adotada_multiplas_estacoes(
        self,
        codigos: list[int],
        end_datetime: datetime | None = None,
        date_filter: DateFilter = DateFilter.MEASUREMENT_DATE,
        range_filter: RangeFilter = RangeFilter.ONE_DAY,
    ) -> pd.DataFrame:
        """Busca série histórica detalhada de dados telemétricos para múltiplas estações específicas.

        Parâmetros
        ----------
        codigos : list[int]
            Lista de códigos das estações para as quais buscar os dados.
        end_datetime : datetime
            Data e hora de final do intervalo para buscar os dados.
        filter_type : DateFilter, opcional
            Tipo de filtro de data a ser usado data da medição (FilterDate.MEASUREMENT_DATE) ou data da última atualização (FilterDate.LAST_UPDATE_DATE).
            Padrão para data da medição (FilterDate.MEASUREMENT_DATE).
        range_filter : RangeFilter, opcional
            Intervalo de busca termina no dia final (end_datetime) e inicia no dia final menos o intervalo.
            O padrão é o intevalo de um dia (RangeFilter.ONE_DAY), isto é, será buscado dados para o dia inteiro.
            O valor máximo permitido é de 30 dias (RangeFilter.THIRTY_DAYS) e o menor de 5 minutos (Rangefilter.FIVE_MINUTES).

        Retorna
        -------
        pd.DataFrame
            DataFrame contendo a série histórica detalhada de dados telemétricos.
        """
        endpoint_suffix = "HidroinfoanaSerieTelemetricaAdotada/v2"
        return await self._telemetry_multi_station(
            endpoint_suffix, codigos, end_datetime, date_filter, range_filter
        )

    async def serie_telemetrica_detalhada_multiplas_estacoes(
        self,
        codigos: list[int],
        end_datetime: datetime | None = None,
        date_filter: DateFilter = DateFilter.MEASUREMENT_DATE,
        range_filter: RangeFilter = RangeFilter.ONE_DAY,
    ) -> pd.DataFrame:
        """Busca série histórica adotada de dados telemétricos para múltiplas estações específicas.

        Parâmetros
        ----------
        codigos : list[int]
            Lista de códigos das estações para as quais buscar os dados.
        end_datetime : datetime
            Data e hora de final do intervalo para buscar os dados.
        filter_type : DateFilter, opcional
            Tipo de filtro de data a ser usado data da medição (FilterDate.MEASUREMENT_DATE) ou data da última atualização (FilterDate.LAST_UPDATE_DATE).
            Padrão para data da medição (FilterDate.MEASUREMENT_DATE).
        range_filter : RangeFilter, opcional
            Intervalo de busca termina no dia final (end_datetime) e inicia no dia final menos o intervalo.
            O padrão é o intevalo de um dia (RangeFilter.ONE_DAY), isto é, será buscado dados para o dia inteiro.
            O valor máximo permitido é de 30 dias (RangeFilter.THIRTY_DAYS) e o menor de 5 minutos (Rangefilter.FIVE_MINUTES).

        Retorna
        -------
        pd.DataFrame
            DataFrame contendo a série histórica adotada de dados telemétricos.
        """
        endpoint_suffix = "HidroinfoanaSerieTelemetricaDetalhada/v2"
        return await self._telemetry_multi_station(
            endpoint_suffix, codigos, end_datetime, date_filter, range_filter
        )

    async def close(self):
        """Fecha a sessão do cliente HTTP.

        Este método deve ser chamado quando o cliente não for mais necessário
        para fechar adequadamente as conexões HTTP subjacentes.
        """
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()


def add_get_timeseries_method(
    endpoint_suffix: str, method_description: str, return_description: str
):
    async def _generic_func(
        self,
        codigo: int,
        start_datetime: datetime,
        end_datetime: datetime,
        date_filter: DateFilter = DateFilter.MEASUREMENT_DATE,
        ignore_time: bool = True,
    ) -> pd.DataFrame:
        params = {
            "Código da Estação": codigo,
            "Tipo Filtro Data": date_filter.value,
            "Data Inicial (yyyy-MM-dd)": start_datetime.strftime("%Y-%m-%d"),
            "Data Final (yyyy-MM-dd)": end_datetime.strftime("%Y-%m-%d"),
        }
        if not ignore_time:
            params["Horário Inicial (00:00:00)"] = start_datetime.strftime("%H:%M:%S")
            params["Horário Final (23:59:59)"] = end_datetime.strftime("%H:%M:%S")
        return await self._df_from_api(endpoint_suffix, params)

    _generic_func.__doc__ = f"""{method_description}

                Parâmetros
                ----------
                codigo : int
                    Código da estação para a qual buscar os dados.
                start_datetime : datetime
                    Data e hora de início do intervalo para buscar os dados.
                end_datetime : datetime
                    Data e hora de fim do intervalo para buscar os dados.
                filter_type : DateFilter, opcional
                    Tipo de filtro de data a ser usado data da medição (FilterDate.MEASUREMENT_DATE) ou data da última atualização (FilterDate.LAST_UPDATE_DATE).
                    Padrão para data da medição (FilterDate.MEASUREMENT_DATE).
                ignore_time : bool, opcional
                    Se True, ignora a parte do tempo e considera apenas a data.
                    Nesse caso, a API considera a hora 00:00:00 para data inicial e 23:59:59 para data final.

                Retorna
                -------
                pd.DataFrame
                    {return_description}
                """
    return _generic_func


methods_to_add = [
    {
        "endpoint_suffix": "HidroSerieChuva/v1",
        "method_name": "serie_chuva",
        "method_description": "Busca série histórica de dados de chuva para uma estação específica.",
        "return_description": "DataFrame contendo a série histórica de dados de chuva.",
    },
    {
        "endpoint_suffix": "HidroSerieCotas/v1",
        "method_name": "serie_cotas",
        "method_description": "Busca série histórica de dados de cotas para uma estação específica.",
        "return_description": "DataFrame contendo a série histórica de dados de cotas.",
    },
    {
        "endpoint_suffix": "HidroSerieVazao/v1",
        "method_name": "serie_vazao",
        "method_description": "Busca série histórica de dados de vazão para uma estação específica.",
        "return_description": "DataFrame contendo a série histórica de dados de vazão.",
    },
    {
        "endpoint_suffix": "HidroSerieSedimentos/v1",
        "method_name": "serie_sedimentos",
        "method_description": "Busca série histórica de dados de sedimentos para uma estação específica.",
        "return_description": "DataFrame contendo a série histórica de dados de sedimentos.",
    },
    {
        "endpoint_suffix": "HidroSerieResumoDescarga/v1",
        "method_name": "serie_resumo_descarga",
        "method_description": "Busca série histórica de dados de resumo de descarga para uma estação específica.",
        "return_description": "DataFrame contendo a série histórica de dados de resumo de descarga.",
    },
    {
        "endpoint_suffix": "HidroSerieQualidadeAgua/v1",
        "method_name": "serie_qualidade_agua",
        "method_description": "Busca série histórica de dados de qualidade da água para uma estação específica.",
        "return_description": "DataFrame contendo a série histórica de dados de qualidade da água.",
    },
    {
        "endpoint_suffix": "HidroSerieQA/v1",
        "method_name": "serie_qualidade_agua",
        "method_description": "Busca série histórica de dados de qualidade da água para uma estação específica.",
        "return_description": "DataFrame contendo a série histórica de dados de qualidade da água.",
    },
    {
        "endpoint_suffix": "HidroSeriePerfilTransversal/v1",
        "method_name": "serie_perfil_transversal",
        "method_description": "Busca série histórica de dados de perfil transversal para uma estação específica.",
        "return_description": "DataFrame contendo a série histórica de dados de perfil transversal.",
    },
    {
        "endpoint_suffix": "HidroSerieCurvaDescarga/v1",
        "method_name": "serie_curva_descarga",
        "method_description": "Busca série histórica de dados de curva de descarga para uma estação específica.",
        "return_description": "DataFrame contendo a série histórica de dados de curva de descarga.",
    },
    {
        "endpoint_suffix": "HidrosatSerieDados/v1",
        "method_name": "serie_hidrosat",
        "method_description": "Busca série histórica de dados do Hidrosat para uma estação virtual específica.",
        "return_description": "DataFrame contendo a série histórica de dados do Hidrosat.",
    },
]
for method in methods_to_add:
    setattr(
        Client,
        method["method_name"],
        add_get_timeseries_method(
            method["endpoint_suffix"],
            method["method_description"],
            method["return_description"],
        ),
    )


if __name__ == "__main__":
    import asyncio

    async def main():
        async with Client() as client:
            await client.authenticate()
            df = await client.sub_bacias()
            print(df)
            print(df.columns.tolist())

    asyncio.run(main())
