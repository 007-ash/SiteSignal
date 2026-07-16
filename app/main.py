from fastapi import FastAPI, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.database import check_database_connection

app = FastAPI(
    title="SiteSignal",
    version="0.1.0",
    description="PostGIS-backed solar parcel screening API.",
)


@app.get("/health")
def health_check() -> dict[str, str | bool]:
    """Return deterministic JSON indicating the API process is healthy."""
    return {
        "healthy": True,
        "status": "ok",
        "service": "SiteSignal",
        "version": "0.1.0",
    }


@app.get("/ready")
def readiness_check() -> dict[str, str | bool]:
    try:
        check_database_connection()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable.",
        ) from exc

    return {
        "ready": True,
        "status": "ok",
        "service": "SiteSignal",
    }
