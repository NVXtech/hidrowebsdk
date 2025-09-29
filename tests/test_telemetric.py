import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from hidrowebsdk import RangeFilter

test_configs = [
    {
        "method_name": "serie_telemetrica_detalhada",
        "codigo": 13445000,
        "end_datetime": datetime(2025, 8, 28),
        "range_filter": RangeFilter.ONE_HOUR,
        "required_fields": [
            "Chuva_Adotada",
            "Chuva_Adotada_Status",
            "Cota_Adotada",
            "Cota_Adotada_Status",
            "Data_Atualizacao",
            "Data_Hora_Medicao",
            "Vazao_Adotada",
            "Vazao_Adotada_Status",
            "codigoestacao",
        ],
    },
    {
        "method_name": "serie_telemetrica_detalhada",
        "codigo": 13445000,
        "end_datetime": datetime(2025, 8, 28),
        "range_filter": RangeFilter.ONE_HOUR,
        "required_fields": [
            "Bateria",
            "Chuva_Acumulada",
            "Chuva_Acumulada_Status",
            "Chuva_Adotada",
            "Chuva_Adotada_Status",
            "Cota_Adotada",
            "Cota_Adotada_Status",
            "Cota_Display",
            "Cota_Display_Status",
            "Cota_Manual",
            "Cota_Manual_Status",
            "Cota_Sensor",
            "Cota_Sensor_Status",
            "Data_Atualizacao",
            "Data_Hora_Medicao",
            "Pressao_Atmosferica",
            "Pressao_Atmosferica_Status",
            "Temperatura_Agua",
            "Temperatura_Agua_Status",
            "Temperatura_Interna",
            "Vazao_Adotada",
            "Vazao_Adotada_Status",
            "codigoestacao",
        ],
    },
]


@pytest_asyncio.fixture(
    scope="module", params=test_configs, ids=[c["method_name"] for c in test_configs]
)
async def series_data(request, client):
    config = request.param
    df = await getattr(client, config["method_name"])(
        codigo=config["codigo"],
        end_datetime=config["end_datetime"],
        range_filter=config["range_filter"],
    )
    return config, df


@pytest.mark.asyncio
async def test_not_empty(series_data):
    config, df = series_data
    assert not df.empty, (
        f"No data found for {config['method_name']} with codigo {config['codigo']}"
    )


@pytest.mark.asyncio
async def test_code_filter(series_data):
    config, df = series_data
    assert all(df["codigoestacao"] == str(config["codigo"])), (
        f"Some rows do not match codigo {config['codigo']}"
    )


@pytest.mark.asyncio
async def test_date_range(series_data):
    config, df = series_data
    field_name = "Data_Hora_Medicao"
    for date_str in df[field_name]:
        date = datetime.strptime(date_str[:19], "%Y-%m-%d %H:%M:%S")
        end_date = config["end_datetime"].replace(hour=23, minute=59, second=59)
        start_date = end_date - timedelta(hours=1)
        assert start_date <= date <= end_date, (
            f"Date {date} is out of rangei({start_date} - {end_date})"
        )


@pytest.mark.asyncio
async def test_required_fields(series_data):
    config, df = series_data
    for field in config["required_fields"]:
        assert field in df.columns, f"Field {field} is missing"
