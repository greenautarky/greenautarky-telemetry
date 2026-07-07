"""Smoke tests: manifest/pyproject consistency + component shape.

These are deliberately HA-free (they only read JSON/TOML) so they run fast and
green from a bare checkout. The heavier behavioural tests can grow alongside the
extracted storage/WS code; for the initial standalone release we assert the
invariants the delivery chain depends on: domain == directory name, and the
version is in lockstep across manifest + pyproject + tag.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENT = ROOT / "src" / "greenautarky_telemetry"


def _manifest() -> dict:
    return json.loads((COMPONENT / "manifest.json").read_text())


def _pyproject_version() -> str:
    text = (ROOT / "pyproject.toml").read_text()
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    assert m, "no version in pyproject.toml"
    return m.group(1)


def test_domain_matches_directory() -> None:
    assert _manifest()["domain"] == COMPONENT.name == "greenautarky_telemetry"


def test_manifest_has_config_flow_and_ws_dep() -> None:
    mf = _manifest()
    assert mf["config_flow"] is True
    assert "websocket_api" in mf["dependencies"]


def test_version_lockstep() -> None:
    assert _manifest()["version"] == _pyproject_version()


def test_component_files_present() -> None:
    for f in ("__init__.py", "config_flow.py", "manifest.json"):
        assert (COMPONENT / f).is_file(), f"missing {f}"
