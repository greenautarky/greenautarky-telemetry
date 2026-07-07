# greenautarky-telemetry

Home Assistant custom integration (`greenautarky_telemetry`) that stores the
tenant's **telemetry-consent preferences** under the GreenAutarky Privacy-Tier
model, and exposes them over the HA WebSocket API for the onboarding wizard and
the fleet-side privacy tooling.

It is a **storage backend only** — it holds consent flags, not telemetry data,
and collects no PII. See [`src/greenautarky_telemetry/PRIVACY.md`](src/greenautarky_telemetry/PRIVACY.md)
and `ga-ihost-docs/PRIVACY_TIERS.md` for the tier semantics:

- **Tier 0** (Vertragserfüllung + berechtigtes Interesse) — always-on at the OS
  layer, no toggle here.
- **Tier 1** (berechtigtes Interesse) — default **ON**, opt-out.
- **Tier 2** (Einwilligung) — default **OFF**, opt-in.
- **Tier 3** (zeitbegrenzte Einwilligung) — not stored here; handled per-incident
  by case-management.

## Delivery (Tier-2 component, ADR-0007)

This is **not** installed via HACS and is **not** baked into a Core fork. It ships
as a self-contained OCI artifact, mirroring `greenautarky-onboarding` and
`ga-frontend-bundle`:

1. A tagged release (`vX.Y.Z`) runs [`.github/workflows/release.yml`](.github/workflows/release.yml),
   which tarballs `src/greenautarky_telemetry/` and `oras push`es it to
   `ghcr.io/greenautarky/greenautarky-telemetry:X.Y.Z`.
2. `ha-operating-system` pins the version in `version.yaml` under `components:`;
   `scripts/sync-components.sh` pulls the artifact into the buildroot overlay at
   OS build time.
3. On-device, `ga-bootstrap` stages it and the `ga_manager` **converge** worker
   copies it into `/config/custom_components/` and enables the `greenautarky_telemetry:`
   integration in `configuration.yaml`, where stock Core loads it.

## Development

```bash
pip install -e .[dev]
pytest tests/ -v
ruff check src/ tests/
```

The `manifest.json` version, `pyproject.toml` version, and the release tag must
all match — CI (`build-consistency`) and the release workflow both assert this.
