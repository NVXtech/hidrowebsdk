import pytest_asyncio
import pytest

codigo = "10"
required_columns = [
    "Bacia_Codigo",
    "Data_Ultima_Alteracao",
    "Sub_Bacia_Nome",
    "codigosubbacia",
]


@pytest_asyncio.fixture(scope="module")
async def sub_bacias_result(client):
    """Fixture to fetch sub_bacias data once for all tests in this file."""
    return await client.sub_bacias()


@pytest.mark.asyncio
async def test_sub_bacias_columns(sub_bacias_result):
    """Test if sub_bacias result contains the required columns."""
    assert all(col in sub_bacias_result.columns for col in required_columns), (
        f"Missing columns in sub_bacias result: {set(required_columns) - set(sub_bacias_result.columns)}"
    )


@pytest.mark.asyncio
async def test_sub_bacias_not_empty(sub_bacias_result):
    """Test if sub_bacias result is not empty."""
    assert not sub_bacias_result.empty, "Bacias result is empty"


@pytest_asyncio.fixture(scope="module")
async def sub_bacias_codigo_filter(client):
    """Fixture to fetch bacia by codigo."""
    return await client.sub_bacias(codigo=codigo)


@pytest.mark.asyncio
async def test_sub_bacia_codigo_filter_not_empty(sub_bacias_codigo_filter):
    """Test if filtering by codigo returns the correct sub-bacia."""
    assert not sub_bacias_codigo_filter.empty, f"No sub_bacia found for codigo {codigo}"


@pytest.mark.asyncio
async def test_sub_bacia_codigo_filter_correct(sub_bacias_codigo_filter):
    codigo_returned = sub_bacias_codigo_filter.iloc[0]["codigosubbacia"]
    assert codigo_returned == codigo, (
        f"Returned sub_bacias do not match codigo {codigo}"
    )
