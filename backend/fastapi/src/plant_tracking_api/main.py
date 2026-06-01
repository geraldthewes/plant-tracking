import uvicorn

from fastapi import FastAPI

from plant_tracking_api.config import settings
from plant_tracking_api.routes import health, plants

app = FastAPI(
    title="Plant Tracking API",
    description="Backend API for plant tracking home page",
    version="0.1.0",
)

app.include_router(health.router, tags=["health"])
app.include_router(plants.router, prefix="/api/plants", tags=["plants"])


if __name__ == "__main__":
    uvicorn.run(
        "plant_tracking_api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level,
    )
