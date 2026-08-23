from datetime import date

from pydantic import BaseModel, field_validator


class PlantDeathRequest(BaseModel):
    """Request body for marking a plant as dead."""
    death_date: date
    death_reason: str
    death_comment: str | None = None

    @field_validator("death_comment", mode="before")
    @classmethod
    def empty_comment_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class PlantSummary(BaseModel):
    """Plant summary for list responses."""
    id: str
    variety_name: str
    latin_name: str
    planting_date: date | None = None
    death_date: date | None = None
    death_reason: str | None = None
    is_dead: bool = False


class PlantListResponse(BaseModel):
    """Response for plant list endpoints."""
    count: int
    plants: list[PlantSummary]


class PlantResponse(BaseModel):
    """Full plant details response."""
    id: str
    variety_name: str
    latin_name: str
    brand: str | None = None
    days_to_maturity: int | None = None
    germination_time: int | None = None
    planting_depth: str | None = None
    spacing: str | None = None
    sun_requirements: str | None = None
    indoor_start_time: int | None = None
    planting_date: date | None = None
    seed_packet_id: str | None = None
    genus_id: str | None = None
    death_date: date | None = None
    death_reason: str | None = None
    death_comment: str | None = None
    is_dead: bool = False


class PlantDeadResponse(BaseModel):
    """Response after marking a plant as dead."""
    id: str
    variety_name: str
    death_date: date | None = None
    death_reason: str | None = None
    death_comment: str | None = None
    is_dead: bool = False
