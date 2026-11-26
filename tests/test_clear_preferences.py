"""An onboarding reset forgets the decision instead of recording the defaults.

``async_set_preferences`` records a decision: it stamps ``accepted_at`` and the
policy version. Used to put the tiers back to their starting values, it left a
record of a choice nobody made, and the OS gate acts on that record.
``async_clear_preferences`` removes the record instead.
"""

from __future__ import annotations

import pytest

from greenautarky_telemetry import (
    DOMAIN,
    STORAGE_KEY,
    TIER_1,
    TIER_2,
    async_clear_preferences,
    async_set_preferences,
    async_setup,
    websocket_get_preferences,
)

pytestmark = pytest.mark.asyncio


async def _setup(hass):
    assert await async_setup(hass, {})


async def test_clear_removes_the_stored_record(hass, hass_storage):
    await _setup(hass)
    await async_set_preferences(hass, tier1=False, tier2=True)
    assert STORAGE_KEY in hass_storage

    await async_clear_preferences(hass)
    await hass.async_block_till_done()

    assert STORAGE_KEY not in hass_storage, "a record survived the reset"


async def test_after_clear_nothing_reads_as_accepted(hass):
    await _setup(hass)
    await async_set_preferences(hass, tier1=False, tier2=True)

    data = await async_clear_preferences(hass)

    assert hass.data[DOMAIN]["preferences"] is data
    assert data["policy_version_accepted"] is None
    for tier in (TIER_1, TIER_2):
        assert data["tiers"][tier]["accepted_at"] is None
        assert data["tiers"][tier]["policy_version"] is None


async def test_after_clear_the_page_starts_from_the_defaults(hass):
    await _setup(hass)
    await async_set_preferences(hass, tier1=False, tier2=True)
    data = await async_clear_preferences(hass)
    assert data["tiers"][TIER_1]["value"] is True
    assert data["tiers"][TIER_2]["value"] is False


async def test_clear_is_the_same_state_as_a_fresh_device(hass, hass_storage):
    await _setup(hass)
    fresh = dict(hass.data[DOMAIN]["preferences"])
    await async_set_preferences(hass, tier2=True)
    assert await async_clear_preferences(hass) == fresh


async def test_a_new_decision_after_clear_is_recorded(hass, hass_storage):
    """Must-pass: clearing does not stop the next resident from deciding."""
    await _setup(hass)
    await async_clear_preferences(hass)
    record = await async_set_preferences(hass, tier1=False, tier2=False)
    await hass.async_block_till_done()
    assert record["policy_version_accepted"] is not None
    assert hass_storage[STORAGE_KEY]["data"]["tiers"][TIER_1]["value"] is False


async def test_clear_on_a_device_without_a_record_is_harmless(hass, hass_storage):
    await _setup(hass)
    await async_clear_preferences(hass)
    await async_clear_preferences(hass)
    assert STORAGE_KEY not in hass_storage


async def test_the_websocket_reports_no_decision_after_clear(hass):
    await _setup(hass)
    await async_set_preferences(hass, tier2=True)
    await async_clear_preferences(hass)
    sent = {}

    class _Conn:
        def send_result(self, _id, response):
            sent.update(response)

    websocket_get_preferences(hass, _Conn(), {"id": 1, "type": "greenautarky_telemetry/get"})
    assert sent["policy_version_accepted"] is None
    assert sent["consent_is_stale"] is False
