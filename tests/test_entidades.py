import pytest_asyncio
import pytest

codigo = "1"
required_columns = [
    "codigoentidade",
    "Entidade_Nome",
    "Entidade_Sigla",
    "Data_Ultima_Alteracao",
]


@pytest_asyncio.fixture(scope="module")
async def entidades_result(client):
    """Fixture to fetch entidades data once for all tests in this file."""
    return await client.entidades()


@pytest.mark.asyncio
async def test_entidades_columns(entidades_result):
    """Test if entidades result contains the required columns."""
    assert all(col in entidades_result.columns for col in required_columns), (
        f"Missing columns in entidades result: {set(required_columns) - set(entidades_result.columns)}"
    )


@pytest.mark.asyncio
async def test_entidades_not_empty(entidades_result):
    """Test if entidades result is not empty."""
    assert not entidades_result.empty, "Entidades result is empty"


@pytest_asyncio.fixture(scope="module")
async def entidade_codigo_filter(client):
    """Fixture to fetch entidade by codigo."""
    return await client.entidades(codigo=codigo)


@pytest.mark.asyncio
async def test_entidade_codigo_filter_not_empty(entidade_codigo_filter):
    """Test if filtering by codigo returns the correct entidade."""
    assert not entidade_codigo_filter.empty, f"No entidade found for codigo {codigo}"


@pytest.mark.asyncio
async def test_entidade_codigo_filter_correct(entidade_codigo_filter):
    assert entidade_codigo_filter.iloc[0]["codigoentidade"] == codigo, (
        f"Returned entidades do not match codigo {codigo}"
    )
