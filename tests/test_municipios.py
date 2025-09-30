import pytest_asyncio
import pytest

codigo = "1000500"
required_columns = [
    "Data_Ultima_Alteracao",
    "Estado_Codigo",
    "Municipio_Codigo_IBGE",
    "Municipio_Nome",
    "codigomunicipio",
]


@pytest_asyncio.fixture(scope="module")
async def municipios_result(client):
    """Fixture to fetch municipios data once for all tests in this file."""
    return await client.municipios()


@pytest.mark.asyncio
async def test_estados_columns(municipios_result):
    """Test if municipios result contains the required columns."""
    assert all(col in municipios_result.columns for col in required_columns), (
        f"Missing columns in Estado result: {set(required_columns) - set(municipios_result.columns)}"
    )


@pytest.mark.asyncio
async def test_estados_not_empty(municipios_result):
    """Test if municipios result is not empty."""
    assert not municipios_result.empty, "Estados result is empty"


@pytest_asyncio.fixture(scope="module")
async def municipios_codigo_filter(client):
    """Fixture to fetch municipios by codigo."""
    return await client.municipios(codigo=codigo)


@pytest.mark.asyncio
async def test_municipio_codigo_filter_not_empty(municipios_codigo_filter):
    """Test if filtering by codigo returns the correct municipios."""
    assert not municipios_codigo_filter.empty, (
        f"No municipios found for codigo {codigo}"
    )


@pytest.mark.asyncio
async def test_municipios_codigo_filter_correct(municipios_codigo_filter):
    assert municipios_codigo_filter.iloc[0]["codigomunicipio"] == codigo, (
        f"Returned estado do not match codigo {codigo}"
    )
