import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from crow_client.clients.rest_client import RestClient
from crow_client.models.app import AuthType, Stage
from crow_client.utils.auth import AuthTokenCache
from httpx import Client


@pytest.fixture
def temp_cache_dir():
    """Fixture to create a temporary directory for cache testing."""
    with (
        tempfile.TemporaryDirectory() as temp_dir,
        patch("pathlib.Path.home") as mock_home,
    ):
        mock_home.return_value = Path(temp_dir)
        yield Path(temp_dir) / ".crow" / "auth_cache"


@pytest.fixture
def auth_cache(temp_cache_dir):  # noqa: ARG001
    """Fixture to create an AuthTokenCache instance with a temporary directory."""
    return AuthTokenCache()


class TestAuthTokenCache:
    def test_init_creates_cache_directory(self, temp_cache_dir):
        AuthTokenCache()
        assert temp_cache_dir.exists()
        assert temp_cache_dir.is_dir()

    def test_store_and_get_token(self, auth_cache):
        service_uri = "https://dev.platform.futurehouse.org"
        auth_type = AuthType.PASSWORD
        token = "test-token-123"
        expiry = datetime.now() + timedelta(hours=1)

        auth_cache.store_token(service_uri, auth_type, token, expiry)

        retrieved_token = auth_cache.get_token(service_uri, auth_type)
        assert retrieved_token == token

    def test_expired_token_returns_none(self, auth_cache):
        service_uri = "https://dev.platform.futurehouse.org"
        auth_type = AuthType.PASSWORD
        token = "test-token-123"
        expiry = datetime.now() - timedelta(minutes=6)

        auth_cache.store_token(service_uri, auth_type, token, expiry)
        retrieved_token = auth_cache.get_token(service_uri, auth_type)
        assert retrieved_token is None

    def test_nonexistent_token_returns_none(self, auth_cache):
        retrieved_token = auth_cache.get_token("nonexistent", AuthType.PASSWORD)
        assert retrieved_token is None

    def test_clear_cache(self, auth_cache, temp_cache_dir):
        service_uri = "https://dev.platform.futurehouse.org"
        auth_type = AuthType.PASSWORD
        token = "test-token-123"
        expiry = datetime.now() + timedelta(hours=1)

        auth_cache.store_token(service_uri, auth_type, token, expiry)
        assert temp_cache_dir.joinpath("tokens.json").exists()

        auth_cache.clear()
        assert not temp_cache_dir.joinpath("tokens.json").exists()

    def test_corrupted_cache_file(self, auth_cache, temp_cache_dir):
        cache_file = temp_cache_dir / "tokens.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text("invalid json content")

        # Should return None instead of raising an error
        retrieved_token = auth_cache.get_token("test", AuthType.PASSWORD)
        assert retrieved_token is None

    def test_multiple_tokens(self, auth_cache):
        tokens = [
            (
                "https://dev.platform.futurehouse.org",
                AuthType.PASSWORD,
                "token1",
                datetime.now() + timedelta(hours=1),
            ),
            (
                "https://platform.futurehouse.org",
                AuthType.GOOGLE,
                "token2",
                datetime.now() + timedelta(hours=2),
            ),
        ]

        for service, auth_type, token, expiry in tokens:
            auth_cache.store_token(service, auth_type, token, expiry)

        for service, auth_type, token, _ in tokens:
            assert auth_cache.get_token(service, auth_type) == token


class TestRestClient:
    @pytest.fixture
    def mock_auth_response(self):
        return {"access_token": "test-token-123", "expires_in": 3600}

    @pytest.fixture
    def rest_client(self, mock_auth_response):
        with patch("crow_client.clients.rest_client.RestClient._run_auth") as mock_auth:
            mock_auth.return_value = mock_auth_response["access_token"]
            with patch(
                "crow_client.clients.rest_client.RestClient._fetch_my_orgs"
            ) as mock_orgs:
                mock_orgs.return_value = ["test-org"]
                client = RestClient(stage=Stage.DEV)
                yield client

    def test_get_client_caching(self, rest_client):
        client1 = rest_client.get_client()
        client2 = rest_client.get_client()

        # Should be the same instance
        assert client1 is client2
        assert isinstance(client1, Client)

    def test_get_client_different_content_types(self, rest_client):
        json_client = rest_client.get_client()
        multipart_client = rest_client.get_client(content_type="multipart/form-data")

        # Should be different instances
        assert json_client is not multipart_client
        assert "application/json" in json_client.headers["Content-Type"]
        assert "multipart/form-data" in multipart_client.headers["Content-Type"]

    def test_get_client_auth_headers(self, rest_client):
        auth_client = rest_client.get_client(with_auth=True)
        no_auth_client = rest_client.get_client(with_auth=False)

        assert "Authorization" in auth_client.headers
        assert "Authorization" not in no_auth_client.headers

    def test_client_cleanup(self, rest_client):
        rest_client.get_client("application/json", with_auth=True)
        rest_client.get_client("application/json", with_auth=False)
        rest_client.get_client(None, with_auth=True)  # For multipart

        for client_obj in rest_client._clients.values():
            client_obj.close = MagicMock()

        rest_client.__del__()  # noqa: PLC2801

        for client_obj in rest_client._clients.values():
            client_obj.close.assert_called_once()

    def test_get_client_base_url(self, rest_client):
        clients = [
            rest_client.get_client(),
            rest_client.get_client(content_type="multipart/form-data"),
            rest_client.get_client(with_auth=False),
        ]

        for client in clients:
            assert client.base_url == Stage.DEV.value
