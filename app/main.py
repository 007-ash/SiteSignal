from fastapi import FastAPI

app = FastAPI(title="SiteSignal", version="0.1.0",
              description="PostGIS-backed solar parcel screening API.",)


@app.get("/health")
def health_check() -> dict[str, str | bool]:
    """Return deterministic JSON indicating the API process is healthy."""
    return {
        "healthy": True,
        "status": "OK",
        "service": "SiteSignal",
        "version": "0.1.0"
    }
