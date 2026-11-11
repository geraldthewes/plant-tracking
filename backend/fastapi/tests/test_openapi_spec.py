import json
from pathlib import Path

import pytest

from plant_tracking_api.main import app

SPEC_PATH = Path(__file__).resolve().parent.parent / "openapi.json"

DEAD_PATH = "/api/plants/{plant_id}/dead"


@pytest.fixture(scope="module")
def file_spec():
    with SPEC_PATH.open() as f:
        return json.load(f)


@pytest.fixture(scope="module")
def app_spec():
    return app.openapi()


def test_openapi_json_paths_match_live_app(file_spec, app_spec):
    """The committed spec must not drift from the routes the app actually serves."""
    assert set(file_spec["paths"]) == set(app_spec["paths"])


def test_openapi_json_mark_plant_dead_request_body_is_json(file_spec):
    """The dead endpoint takes a Pydantic body model; the spec must declare JSON."""
    operation = file_spec["paths"].get(DEAD_PATH, {}).get("patch", {})
    content = operation.get("requestBody", {}).get("content", {})
    assert list(content) == ["application/json"]
