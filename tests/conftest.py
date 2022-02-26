"""pytest fixtures."""
import pytest
import json

from pytest_homeassistant_custom_component.common import load_fixture

@pytest.fixture(scope="session")
def laundry_test_data():
    """Load Laundry Data Mock"""
    return json.loads(load_fixture("test_laundry_data.json"))


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""
    yield