import pytest_asyncio
import pytest

codigo = "3122S05150W0"
required_columns = [
    "Corpo_Hidrico",
    "Estacao_Nome",
    "Estacao_Status",
    "Latitude",
    "Longitude",
    "Pais",
    "UF",
    "codigoestacao",
]


@pytest_asyncio.fixture(scope="module")
async def estacao_hidrosat_codigo_filter(client):
    """Fixture to fetch estacao by codigo."""
    return await client.estacoes_hidrosat(codigo=codigo)


@pytest.mark.asyncio
async def test_estacao_hidrosat_codigo_filter_not_empty(estacao_hidrosat_codigo_filter):
    """Test if filtering by codigo returns the correct estacao."""
    assert not estacao_hidrosat_codigo_filter.empty, (
        f"No estacao found for codigo {codigo}"
    )


@pytest.mark.asyncio
async def test_estacao_hidrosat_codigo_filter_correct(estacao_hidrosat_codigo_filter):
    assert estacao_hidrosat_codigo_filter.iloc[0]["codigoestacao"] == codigo, (
        f"Returned estacoes do not match codigo {codigo}"
    )


@pytest.mark.asyncio
async def test_estacao_hidrosat_required_columns(estacao_hidrosat_codigo_filter):
    """Test if the fetched estacao data contains the required fields."""
    for column in required_columns:
        assert column in estacao_hidrosat_codigo_filter.columns, (
            f"Missing column: {column}"
        )
