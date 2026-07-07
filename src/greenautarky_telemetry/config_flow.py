"""Config flow for greenautarky_telemetry — single-entry, no user input.

Variant B (config_flow pattern): an installer or HAOS overlay creates a
config_entry in `.storage/core.config_entries` to trigger
`async_setup_entry`. We don't expose a UI; there's nothing meaningful for
a user to configure here at install time.

If somebody really tries to add this via the HA UI (Devices & Services →
Add Integration), we create a single entry with default preferences.
"""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from . import DOMAIN


class GreenautarkyTelemetryConfigFlow(ConfigFlow, domain=DOMAIN):
    """Trivial config flow — always creates one default entry."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """User-initiated (rare). Creates the single entry."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="greenautarky Telemetry", data={})

    async def async_step_import(self, import_data: dict[str, Any]) -> ConfigFlowResult:
        """Programmatic import (used by installer if needed)."""
        return await self.async_step_user(import_data)
