import pytest
from sqlalchemy import text

from app.database import engine


# Integration test for the real PostGIS database connection.
# Uses the application engine from app.database so this test exercises
# the same database configuration as the app runtime.
@pytest.mark.integration
def test_postgis_support_and_area_calculation() -> None:
    with engine.connect() as connection:
        # Ensure PostGIS is installed and available on the database.
        version = connection.execute(
            text("SELECT postgis_version()")
        ).scalar_one()

        # Calculate the area of a 10x10 polygon using a PostGIS geometry function.
        area = connection.execute(
            text(
                """
                SELECT ST_Area(
                    ST_GeomFromText(
                        'POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))',
                        3857
                    )
                )
                """
            )
        ).scalar_one()

    assert isinstance(version, str)
    assert version, "PostGIS version should be returned as a non-empty string"
    assert area == pytest.approx(100.0)
