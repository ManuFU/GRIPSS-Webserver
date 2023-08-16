import pytest
from app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client



# Test for the /start_sitemap_scrap route
def test_start_processing(client):
    # Sample data to send with the POST request
    sample_data = {
        "urls": ["http://example.com", "http://test.com"],
        "industryName": "Tech"
    }

    # Sending POST request to start_processing endpoint with sample_data
    response = client.post('/start_sitemap_scrap', json=sample_data)

    # Parse the response data
    json_data = response.get_json()

    # Assert the status code and the returned message
    assert response.status_code == 200
    assert json_data["message"] == "Processing started, check back later for results."