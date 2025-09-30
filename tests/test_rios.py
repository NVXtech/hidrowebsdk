import pytest_asyncio
import pytest

codigo = "10000050"
required_columns = [
    "Bacia_Codigo",
    "Data_Ultima_Alteracao",
    "Nome_Rio",
    "Rio_Jurisdicao",
    "Sub_Bacia_Codigo",
    "codigorio",
]


@pytest_asyncio.fixture(scope="module")
async def rios_result(client):
    """Fixture to fetch rios data once for all tests in this file."""
    return await client.rios()


@pytest.mark.asyncio
async def test_estados_columns(rios_result):
    """Test if rios result contains the required columns."""
    assert all(col in rios_result.columns for col in required_columns), (
        f"Missing columns in Estado result: {set(required_columns) - set(rios_result.columns)}"
    )


@pytest.mark.asyncio
async def test_estados_not_empty(rios_result):
    """Test if rios result is not empty."""
    assert not rios_result.empty, "Estados result is empty"


@pytest_asyncio.fixture(scope="module")
async def rios_codigo_filter(client):
    """Fixture to fetch entidade by codigo."""
    return await client.rios(codigo=codigo)


@pytest.mark.asyncio
async def test_rios_codigo_filter_not_empty(rios_codigo_filter):
    """Test if filtering by codigo returns the correct entidade."""
    assert not rios_codigo_filter.empty, f"No rios found for codigo {codigo}"


@pytest.mark.asyncio
async def test_rios_codigo_filter_correct(rios_codigo_filter):
    assert rios_codigo_filter.iloc[0]["codigorio"] == codigo, (
        f"Returned estado do not match codigo {codigo}"
    )
