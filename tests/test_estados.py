import pytest_asyncio
import pytest

codigo = "2"
required_columns = [
    "Data_Ultima_Alteracao",
    "Estado_Codigo_IBGE",
    "Estado_Nome",
    "Estado_Sigla",
    "codigouf",
]


@pytest_asyncio.fixture(scope="module")
async def estados_result(client):
    """Fixture to fetch estados data once for all tests in this file."""
    return await client.estados()


@pytest.mark.asyncio
async def test_estados_columns(estados_result):
    """Test if estados result contains the required columns."""
    assert all(col in estados_result.columns for col in required_columns), (
        f"Missing columns in Estado result: {set(required_columns) - set(estados_result.columns)}"
    )


@pytest.mark.asyncio
async def test_estados_not_empty(estados_result):
    """Test if estados result is not empty."""
    assert not estados_result.empty, "Estados result is empty"


@pytest_asyncio.fixture(scope="module")
async def estados_codigo_filter(client):
    """Fixture to fetch estados by codigo."""
    return await client.estados(codigo=codigo)


@pytest.mark.asyncio
async def test_estados_codigo_filter_not_empty(estados_codigo_filter):
    """Test if filtering by codigo returns the correct estados."""
    assert not estados_codigo_filter.empty, f"No estados found for codigo {codigo}"


@pytest.mark.asyncio
async def test_estados_codigo_filter_correct(estados_codigo_filter):
    assert estados_codigo_filter.iloc[0]["codigouf"] == codigo, (
        f"Returned estado do not match codigo {codigo}"
    )
