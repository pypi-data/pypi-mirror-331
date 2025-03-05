import pytest
from unittest.mock import patch, MagicMock
from pointofpresence.client_base import APIClientBase
import requests


@pytest.fixture
def client_no_auth():
    """Fixture for APIClientBase without authentication."""
    with patch.object(APIClientBase, "_check_api_availability"):
        return APIClientBase(base_url="https://api.example.com")


@patch("pointofpresence.client_base.requests.Session.post")
@patch.object(APIClientBase, "_check_api_availability")
def test_init_with_auth(mock_check_api, mock_post):
    """
    Test initialization with username and password, ensuring get_token
    is called.
    """
    mock_check_api.return_value = None
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "fake-access-token"}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    client_with_auth = APIClientBase(
        base_url="https://api.example.com", username="user", password="pass"
    )

    assert client_with_auth.token == "fake-access-token"
    assert (
        client_with_auth.session.headers["Authorization"]
        == "Bearer fake-access-token"
    )
    mock_post.assert_called_once_with(
        "https://api.example.com/token",
        data={"username": "user", "password": "pass"},
    )


def test_init_no_auth(client_no_auth):
    """Test initialization without username and password."""
    assert client_no_auth.base_url == "https://api.example.com"
    assert client_no_auth.token is None
    assert "Authorization" not in client_no_auth.session.headers


def test_base_url_missing_protocol():
    """
    Test initialization when base_url is missing the protocol.
    Ensure 'http://' is prepended.
    """
    with patch.object(APIClientBase, "_check_api_availability"):
        client = APIClientBase(base_url="api.example.com")
        assert client.base_url == "http://api.example.com"


def test_base_url_with_http_protocol():
    """
    Test initialization when base_url already includes 'http://'.
    Ensure the base_url remains unchanged.
    """
    with patch.object(APIClientBase, "_check_api_availability"):
        client = APIClientBase(base_url="http://api.example.com")
        assert client.base_url == "http://api.example.com"


def test_base_url_with_https_protocol():
    """
    Test initialization when base_url already includes 'https://'.
    Ensure the base_url remains unchanged.
    """
    with patch.object(APIClientBase, "_check_api_availability"):
        client = APIClientBase(base_url="https://api.example.com")
        assert client.base_url == "https://api.example.com"


@patch("pointofpresence.client_base.requests.Session.post")
@patch.object(APIClientBase, "_check_api_availability")
def test_get_token_success(mock_check_api, mock_post):
    """Test the get_token method with successful authentication."""
    mock_check_api.return_value = None
    mock_response = MagicMock()
    mock_response.json.return_value = {"access_token": "success-access-token"}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    client = APIClientBase(base_url="https://api.example.com")
    client.get_token("user", "pass")

    assert client.token == "success-access-token"
    assert (
        client.session.headers["Authorization"]
        == "Bearer success-access-token"
    )
    mock_post.assert_called_once_with(
        "https://api.example.com/token",
        data={"username": "user", "password": "pass"},
    )


@patch("pointofpresence.client_base.requests.Session.post")
@patch.object(APIClientBase, "_check_api_availability")
def test_get_token_failure(mock_check_api, mock_post):
    """Test the get_token method with failed authentication."""
    mock_check_api.return_value = None
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "Authentication failed"
    )
    mock_post.return_value = mock_response

    client = APIClientBase(base_url="https://api.example.com")

    with pytest.raises(ValueError) as exc_info:
        client.get_token("user", "wrongpass")

    assert "HTTP error occurred: Authentication failed" in str(exc_info.value)
    mock_post.assert_called_once_with(
        "https://api.example.com/token",
        data={"username": "user", "password": "wrongpass"},
    )


@patch("pointofpresence.client_base.requests.Session.post")
@patch.object(APIClientBase, "_check_api_availability")
def test_get_token_no_access_token(mock_check_api, mock_post):
    """
    Test the get_token method when access_token is missing in the response.
    """
    mock_check_api.return_value = None
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    client = APIClientBase(base_url="https://api.example.com")

    with pytest.raises(ValueError) as exc_info:
        client.get_token("user", "pass")

    assert (
        str(exc_info.value)
        == "Authentication failed: No access token received."
    )
    mock_post.assert_called_once_with(
        "https://api.example.com/token",
        data={"username": "user", "password": "pass"},
    )


def test_init_with_token():
    """
    Test initialization with a token provided.
    Ensure the session is configured with the token.
    """
    client_with_token = APIClientBase(
        base_url="https://api.example.com", token="test-token"
    )

    assert client_with_token.base_url == "https://api.example.com"
    assert client_with_token.token == "test-token"
    assert (
        client_with_token.session.headers["Authorization"]
        == "Bearer test-token"
    )


def test_init_token_conflict():
    """
    Test initialization with both token and username/password.
    Ensure it raises a ValueError.
    """
    with pytest.raises(ValueError) as exc_info:
        APIClientBase(
            base_url="https://api.example.com",
            token="test-token",
            username="user",
            password="pass",
        )

    assert (
        str(exc_info.value)
        == "Provide either a token or username/password, not both."
    )
