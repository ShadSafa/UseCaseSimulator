import pytest
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import commonly used fixtures and utilities
from .fixtures.company_fixtures import *
from .fixtures.market_fixtures import *
from .fixtures.simulation_fixtures import *


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """Return the test data directory."""
    return project_root / "tests" / "test_data"


@pytest.fixture(autouse=True)
def clean_test_artifacts():
    """Clean up test artifacts after each test."""
    yield
    # Add cleanup logic here if needed


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment."""
    # Ensure test directories exist
    test_dirs = [
        "tests/test_data/saves",
        "tests/test_data/reports",
        "tests/test_data/charts",
        "tests/test_data/scenarios"
    ]

    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)


# Custom markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "analytics: marks tests related to analytics functionality")
    config.addinivalue_line("markers", "persistence: marks tests related to data persistence")
    config.addinivalue_line("markers", "scenarios: marks tests related to scenario management")