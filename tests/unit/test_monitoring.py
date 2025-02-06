from fastapi.testclient import TestClient
import logging
from src.main import app

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure test client with base URL
client = TestClient(app, base_url="http://test")


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/monitoring/health")
    logger.debug(f"Response status: {response.status_code}")
    logger.debug(f"Response headers: {response.headers}")
    logger.debug(f"Response body: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert data["version"] == "1.0.1"


def test_metrics():
    """Test the metrics endpoint."""
    response = client.get("/monitoring/metrics")
    logger.debug(f"Response status: {response.status_code}")
    logger.debug(f"Response headers: {response.headers}")
    logger.debug(f"Response body: {response.text}")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]


def test_system_metrics():
    """Test the system metrics endpoint."""
    response = client.get("/monitoring/metrics/system")
    logger.debug(f"Response status: {response.status_code}")
    logger.debug(f"Response headers: {response.headers}")
    logger.debug(f"Response body: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "cpu" in data
    assert "memory" in data
    assert "disk" in data
