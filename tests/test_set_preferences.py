"""A consent decision made by another component must land in the TIERS.

THE DEFECT THIS FILE EXISTS FOR, measured on a bench device on 2026-09-16/17.

The onboarding wizard's telemetry step wrote the resident's two answers as flat
``error_logs`` / ``metrics`` keys straight into this component's preferences
dict and saved it. The v2 record keeps the truth in ``tiers.tier1.value`` /
``tiers.tier2.value`` — which the flat write never touched — and the OS gate
(``ga-telemetry-gate``) reads the tiers on a v2 record. Result: the resident
answered "yes" to Tier 2 and the store said ``tier2: false``; Tier 1 looked
right only because its default is ``True``.

The fix is an entry point another component can call, so the record is built
in exactly one place. These tests drive it, and the first one pins the trap
the wizard fell into so the next caller does not.
"""

from __future__ import annotations

import pytest

from greenautarky_telemetry import (
    DOMAIN,
    LEGACY_TIER2_KEY,
    TIER_1,
    TIER_2,
    async_set_preferences,
    async_setup,
)

pytestmark = pytest.mark.asyncio


async def _setup(hass):
    assert await async_setup(hass, {})
    return hass.data[DOMAIN]


async def test_a_flat_write_into_the_preferences_dict_does_not_reach_the_tiers(hass):
    """The trap, pinned: this is what the wizard did, and it is NOT a consent."""
    data = await _setup(hass)
    data["preferences"][LEGACY_TIER2_KEY] = True  # what the wizard wrote
    assert data["preferences"]["tiers"][TIER_2]["value"] is False


async def test_set_preferences_writes_the_tiers_and_saves(hass, hass_storage):
    await _setup(hass)
    record = await async_set_preferences(hass, metrics=True)

    assert record["tiers"][TIER_2]["value"] is True
    assert record["tiers"][TIER_1]["value"] is True  # untouched default
    assert record["legacy"][LEGACY_TIER2_KEY] is True
    assert hass.data[DOMAIN]["preferences"] is record
    stored = next(v for k, v in hass_storage.items() if k.endswith("telemetry"))
    assert stored["data"]["tiers"][TIER_2]["value"] is True


async def test_canonical_keys_win_over_legacy_aliases(hass):
    await _setup(hass)
    record = await async_set_preferences(hass, metrics=False, tier2=True)
    assert record["tiers"][TIER_2]["value"] is True


async def test_an_unset_tier_keeps_its_current_value(hass):
    await _setup(hass)
    await async_set_preferences(hass, tier1=False)
    record = await async_set_preferences(hass, tier2=True)
    assert record["tiers"][TIER_1]["value"] is False
    assert record["tiers"][TIER_2]["value"] is True


async def test_setting_preferences_records_the_policy_version(hass):
    """A decision made through this entry point is a real consent: it carries
    the policy version it was made under, so a later bump can mark it stale."""
    await _setup(hass)
    record = await async_set_preferences(hass, tier1=True, tier2=True)
    assert record["policy_version_accepted"] is not None
    assert record["tiers"][TIER_2]["accepted_at"] is not None
