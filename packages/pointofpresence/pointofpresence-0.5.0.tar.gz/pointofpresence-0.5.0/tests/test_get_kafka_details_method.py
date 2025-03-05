import pytest
from unittest.mock import patch, MagicMock
from pointofpresence.get_kafka_details_method import APIClientKafkaDetails
from requests.exceptions import HTTPError, RequestException


@pytest.fixture
def client():
    """
    Fixture for APIClientKafkaDetails without triggering network calls.
    """
    with patch.object(APIClientKafkaDetails, "_check_api_availability"):
        return APIClientKafkaDetails(base_url="https://api.example.com")


@patch("pointofpresence.client_base.requests.Session.get")
@patch.object(APIClientKafkaDetails, "_check_api_availability")
def test_get_kafka_details_success(mock_check_api, mock_get, client):
    """Test the get_kafka_details method with a successful response."""
    mock_check_api.return_value = None

    # Mock the GET response for a successful request
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "kafka_host": "localhost",
        "kafka_port": 9092,
        "kafka_connection": True,
    }
    mock_get.return_value = mock_response

    # Call the get_kafka_details method
    response = client.get_kafka_details()

    # Assertions to verify correct behavior
    assert response == {
        "kafka_host": "localhost",
        "kafka_port": 9092,
        "kafka_connection": True,
    }
    mock_get.assert_called_once_with(
        "https://api.example.com/status/kafka-details"
    )


@patch("pointofpresence.client_base.requests.Session.get")
@patch.object(APIClientKafkaDetails, "_check_api_availability")
def test_get_kafka_details_http_error(mock_check_api, mock_get, client):
    """Test the get_kafka_details method with an HTTP error."""
    mock_check_api.return_value = None

    # Mock the GET response to raise an HTTPError
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = HTTPError("Server error")
    mock_get.return_value = mock_response

    # Call the get_kafka_details method and expect a ValueError
    with pytest.raises(ValueError) as exc_info:
        client.get_kafka_details()

    # Verify error message
    assert "Failed to fetch Kafka details: Server error" in str(exc_info.value)
    mock_get.assert_called_once_with(
        "https://api.example.com/status/kafka-details"
    )


@patch("pointofpresence.client_base.requests.Session.get")
@patch.object(APIClientKafkaDetails, "_check_api_availability")
def test_get_kafka_details_request_exception(mock_check_api, mock_get, client):
    """Test the get_kafka_details method with a RequestException."""
    mock_check_api.return_value = None

    # Mock the GET response to raise a generic RequestException
    mock_get.side_effect = RequestException("Connection error")

    # Call the get_kafka_details method and expect a ValueError
    with pytest.raises(ValueError) as exc_info:
        client.get_kafka_details()

    # Verify error message
    assert (
        "An error occurred while fetching Kafka details: Connection error"
        in str(exc_info.value)
    )
    mock_get.assert_called_once_with(
        "https://api.example.com/status/kafka-details"
    )


@patch("pointofpresence.client_base.requests.Session.get")
@patch.object(APIClientKafkaDetails, "_check_api_availability")
def test_get_kafka_details_invalid_json(mock_check_api, mock_get, client):
    """Test the get_kafka_details method with an invalid JSON response."""
    mock_check_api.return_value = None

    # Mock the GET response with invalid JSON
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_get.return_value = mock_response

    # Call the get_kafka_details method and expect a ValueError
    with pytest.raises(ValueError) as exc_info:
        client.get_kafka_details()

    # Verify error message
    assert (
        "An error occurred while parsing Kafka details: Invalid JSON"
        in str(exc_info.value)
    )
    mock_get.assert_called_once_with(
        "https://api.example.com/status/kafka-details"
    )
