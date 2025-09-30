hidrowebsdk/README.md
# HidroWebSDK

[![PyPI version](https://badge.fury.io/py/hidrowebsdk.svg)](https://pypi.org/project/hidrowebsdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-sphinx-blue.svg)](https://nvxtech.github.io/hidrowebsdk/)

> **⚠️ Aviso: Este projeto está em desenvolvimento ativo e está em estágio alfa. As APIs podem mudar sem aviso prévio.**

HidroWebSDK é um SDK Python para simplificar e automatizar o download de dados hidrológicos das estações de monitoramento da Agência Nacional de Águas (ANA) via sua API oficial (HidroWeb).

## Índice

- [Recursos](#recursos)
- [Instalação](#instalação)
- [Uso](#uso)
- [Referência da API](#referência-da-api)
- [Contribuição](#contribuição)
- [Testes](#testes)
- [Licença](#licença)
- [Agradecimentos](#agradecimentos)

## Recursos

- Solicitações HTTP assíncronas usando `httpx` para melhor desempenho
- Atualização automática de token OAuth
- Métodos fáceis de usar para buscar dados de bacias, entidades e estações
- Retorna dados como DataFrames do Pandas para fácil análise
- Conjunto abrangente de testes

## Instalação

Instale o HidroWebSDK usando pip:

```bash
pip install hidrowebsdk
```

Para desenvolvimento, clone o repositório e instale com dependências de desenvolvimento:

```bash
git clone https://github.com/yourusername/hidrowebsdk.git
cd hidrowebsdk
pip install -e ".[dev]"
```

## Uso

### Uso Básico

```python
import asyncio
from hidrowebsdk import Client

async def main():
    # Inicialize o cliente
    client = Client(user="your_user", password="your_password")

    # Autentique (opcional, feito automaticamente na primeira solicitação)
    await client.authenticate()

    # Busque todas as bacias
    basins = await client.bacias()
    print(basins.head())

    # Busque entidades com filtros
    from datetime import datetime
    entities = await client.entidades(
        last_update_start=datetime(2023, 1, 1),
        last_update_end=datetime(2023, 12, 31)
    )
    print(entities.head())

    # Busque estações de um estado específico
    stations = await client.estacoes(state="SP")
    print(stations.head())

    # Feche o cliente
    await client.close()

# Execute a função assíncrona
asyncio.run(main())
```

### Variáveis de Ambiente

Você pode definir suas credenciais usando variáveis de ambiente:

```bash
export HIDROWEB_USER="your_user"
export HIDROWEB_PASSWORD="your_password"
```

Então, inicialize o cliente sem parâmetros:

```python
client = Client()
```

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para enviar um Pull Request.

1. Fork o repositório
2. Crie sua branch de recurso (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Testes

Execute o conjunto de testes:

```bash
pytest
```

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Agradecimentos

- Agência Nacional de Águas (ANA) por fornecer a API HidroWeb
- Construído com [httpx](https://www.python-httpx.org/) para solicitações HTTP assíncronas
- Construído com [pandas](https://pandas.pydata.org/) para manipulação de dados
- Construído com [pytest](https://pytest.org/) para testes
