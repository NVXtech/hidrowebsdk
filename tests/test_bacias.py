import pytest_asyncio
import pytest

codigo = "1"
required_columns = ["codigobacia", "Nome_Bacia", "Data_Ultima_Alteracao"]


@pytest_asyncio.fixture(scope="module")
async def bacias_result(client):
    """Fixture to fetch bacias data once for all tests in this file."""
    return await client.bacias()


@pytest.mark.asyncio
async def test_bacias_columns(bacias_result):
    """Test if bacias result contains the required columns."""
    assert all(col in bacias_result.columns for col in required_columns), (
        f"Missing columns in bacias result: {set(required_columns) - set(bacias_result.columns)}"
    )


@pytest.mark.asyncio
async def test_bacias_not_empty(bacias_result):
    """Test if bacias result is not empty."""
    assert not bacias_result.empty, "Bacias result is empty"


@pytest_asyncio.fixture(scope="module")
async def bacia_codigo_filter(client):
    """Fixture to fetch bacia by codigo."""
    return await client.bacias(codigo=codigo)


@pytest.mark.asyncio
async def test_bacia_codigo_filter_not_empty(bacia_codigo_filter):
    """Test if filtering by codigo returns the correct bacia."""
    assert not bacia_codigo_filter.empty, f"No bacia found for codigo {codigo}"


@pytest.mark.asyncio
async def test_bacia_codigo_filter_correct(bacia_codigo_filter):
    codigo_returned = bacia_codigo_filter.iloc[0]["codigobacia"]
    assert codigo_returned == codigo, f"Returned bacias do not match codigo {codigo}"
