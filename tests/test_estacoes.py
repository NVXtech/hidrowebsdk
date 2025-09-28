import pytest_asyncio
import pytest

codigo = "73960000"
required_columns = [
    "Altitude",
    "Area_Drenagem",
    "Bacia_Nome",
    "Codigo_Adicional",
    "Codigo_Operadora_Unidade_UF",
    "Data_Periodo_Climatologica_Fim",
    "Data_Periodo_Climatologica_Inicio",
    "Data_Periodo_Desc_Liquida_Fim",
    "Data_Periodo_Desc_liquida_Inicio",
    "Data_Periodo_Escala_Fim",
    "Data_Periodo_Escala_Inicio",
    "Data_Periodo_Piezometria_Fim",
    "Data_Periodo_Piezometria_Inicio",
    "Data_Periodo_Pluviometro_Fim",
    "Data_Periodo_Pluviometro_Inicio",
    "Data_Periodo_Qual_Agua_Fim",
    "Data_Periodo_Qual_Agua_Inicio",
    "Data_Periodo_Registrador_Chuva_Fim",
    "Data_Periodo_Registrador_Chuva_Inicio",
    "Data_Periodo_Registrador_Nivel_Fim",
    "Data_Periodo_Registrador_Nivel_Inicio",
    "Data_Periodo_Sedimento_Inicio",
    "Data_Periodo_Sedimento_fim",
    "Data_Periodo_Tanque_Evapo_Fim",
    "Data_Periodo_Tanque_Evapo_Inicio",
    "Data_Periodo_Telemetrica_Fim",
    "Data_Periodo_Telemetrica_Inicio",
    "Data_Ultima_Atualizacao",
    "Estacao_Nome",
    "Latitude",
    "Longitude",
    "Municipio_Codigo",
    "Municipio_Nome",
    "Operadora_Codigo",
    "Operadora_Sigla",
    "Operadora_Sub_Unidade_UF",
    "Operando",
    "Responsavel_Codigo",
    "Responsavel_Sigla",
    "Responsavel_Unidade_UF",
    "Rio_Codigo",
    "Rio_Nome",
    "Sub_Bacia_Codigo",
    "Sub_Bacia_Nome",
    "Tipo_Estacao",
    "Tipo_Estacao_Climatologica",
    "Tipo_Estacao_Desc_Liquida",
    "Tipo_Estacao_Escala",
    "Tipo_Estacao_Piezometria",
    "Tipo_Estacao_Pluviometro",
    "Tipo_Estacao_Qual_Agua",
    "Tipo_Estacao_Registrador_Chuva",
    "Tipo_Estacao_Registrador_Nivel",
    "Tipo_Estacao_Sedimentos",
    "Tipo_Estacao_Tanque_evapo",
    "Tipo_Estacao_Telemetrica",
    "Tipo_Rede_Basica",
    "Tipo_Rede_Captacao",
    "Tipo_Rede_Classe_Vazao",
    "Tipo_Rede_Curso_Dagua",
    "Tipo_Rede_Energetica",
    "Tipo_Rede_Estrategica",
    "Tipo_Rede_Navegacao",
    "Tipo_Rede_Qual_Agua",
    "Tipo_Rede_Sedimentos",
    "UF_Estacao",
    "UF_Nome_Estacao",
    "codigobacia",
    "codigoestacao",
]


@pytest_asyncio.fixture(scope="module")
async def estacao_codigo_filter(client):
    """Fixture to fetch estacao by codigo."""
    return await client.estacoes(codigo=codigo)


@pytest.mark.asyncio
async def test_estacao_codigo_filter_not_empty(estacao_codigo_filter):
    """Test if filtering by codigo returns the correct estacao."""
    assert not estacao_codigo_filter.empty, f"No estacao found for codigo {codigo}"


@pytest.mark.asyncio
async def test_estacao_codigo_filter_correct(estacao_codigo_filter):
    assert estacao_codigo_filter.iloc[0]["codigoestacao"] == codigo, (
        f"Returned estacoes do not match codigo {codigo}"
    )


@pytest.mark.asyncio
async def test_estacao_required_columns(estacao_codigo_filter):
    """Test if the fetched estacao data contains the required fields."""
    for column in required_columns:
        assert column in estacao_codigo_filter.columns, f"Missing column: {column}"
