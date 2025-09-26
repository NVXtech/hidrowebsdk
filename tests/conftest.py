import pytest_asyncio
import hidrowebsdk


@pytest_asyncio.fixture(scope="module")
async def client():
    """Fixture to initialize the HidroWebClient once for all tests."""
    client = hidrowebsdk.Client()
    yield client
    await client.close()
