# Changelog

All notable changes to `greenautarky_telemetry` are documented here.
The version is the single source of truth in `pyproject.toml` and
`src/greenautarky_telemetry/manifest.json` (kept in lockstep; CI asserts it).

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
