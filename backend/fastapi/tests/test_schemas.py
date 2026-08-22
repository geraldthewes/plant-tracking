import pytest

from plant_tracking_api.schemas import PlantDeathRequest

_REQUIRED = {"death_date": "2026-08-07", "death_reason": "Drought"}


@pytest.mark.parametrize(
    "extra",
    [
        pytest.param({}, id="omitted"),
        pytest.param({"death_comment": ""}, id="empty_string"),
        pytest.param({"death_comment": "   "}, id="whitespace"),
        pytest.param({"death_comment": "\t\n"}, id="whitespace_chars"),
        pytest.param({"death_comment": None}, id="null"),
    ],
)
def test_plant_death_request_empty_comment_is_none(extra):
    req = PlantDeathRequest(**_REQUIRED, **extra)
    assert req.death_comment is None


def test_plant_death_request_preserves_non_empty_comment():
    req = PlantDeathRequest(**_REQUIRED, death_comment="Too hot")
    assert req.death_comment == "Too hot"
