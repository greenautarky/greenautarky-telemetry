# Changelog

All notable changes to `greenautarky_telemetry` are documented here.
The version is the single source of truth in `pyproject.toml` and
`src/greenautarky_telemetry/manifest.json` (kept in lockstep; CI asserts it).

## v0.2.4 — 2026-09-17

### feat: `async_set_preferences(hass, …)` — one entry point for a consent decision

The onboarding wizard's telemetry step wrote `error_logs` / `metrics` as flat
keys straight into this component's preferences dict and saved that. A v2
record keeps the truth in `tiers.<tier>.value`, which the flat write never
touched, and the OS gate reads the tiers — so a resident who said yes to
Tier 2 was stored as `tier2: false` (bench device, 2026-09-16; Tier 1 looked
right only because its default is `True`).

`async_set_preferences(hass, tier1=…, tier2=…, error_logs=…, metrics=…)` builds
the record in the one place that knows the schema, keeps it in `hass.data` and
saves it. The WebSocket `set` command now goes through it. Tests: the flat-write
trap is pinned as a must-not-be-a-consent, plus four for the entry point.

## v0.2.3 — 2026-07-07

First standalone release as a **Tier-2 OCI component** (ADR-0007), extracted
from `greenautarky/ha-greenautarky-onboarding` where it previously shipped as
`custom_components/greenautarky_telemetry/`. No code changes vs. the extracted
`v0.2.3` — this release only repackages it for the standalone delivery chain:

- Adds the src-layout, `pyproject.toml`, and the `release.yml` OCI-publish
  workflow (mirrors `greenautarky-onboarding` / `ga-frontend-bundle`).
- `manifest.json` `documentation` now points at this repository.
- Storage schema v2 (consent Tiers 1/2 with `accepted_at` + `policy_version`),
  WebSocket API for reading/writing consent, `config_flow` single-entry setup.
