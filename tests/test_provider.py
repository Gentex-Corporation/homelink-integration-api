import pytest
import json
from .auth_mock import AuthMock
from homelink.provider import Provider
from homelink.settings import DISCOVER_URL, ENABLE_URL


@pytest.fixture
def authorized_provider():
    with (
        open("tests/fixtures/discover_post.json") as discover_post_json,
        open("tests/fixtures/enable_post.json") as enable_post_json,
    ):
        auth = AuthMock(
            {
                DISCOVER_URL: {
                    "POST": {
                        "DISCOVER": json.load(discover_post_json),
                        "ENABLE": json.load(enable_post_json),
                    }
                },
            }
        )
    provider = Provider(auth)
    return provider


@pytest.mark.asyncio
async def test_discover(authorized_provider):
    devices = await authorized_provider.discover()
    assert len(devices) == 1
    assert devices[0].name == "PhiDevice"
    assert len(devices[0].buttons) == 3
    assert [b.name for b in devices[0].buttons] == ["Button 1", "Button 2", "Button 3"]


@pytest.mark.asyncio
async def test_enable(authorized_provider):
    enable_data = await authorized_provider.enable()
    assert enable_data["success"] == True
