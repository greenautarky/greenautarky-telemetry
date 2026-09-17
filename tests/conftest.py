"""pytest-homeassistant-custom-component fixtures; the component is imported as
``greenautarky_telemetry`` from ``src`` (PYTHONPATH), as the CI install does."""

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield
