import json
from collections.abc import Sequence
from hashlib import sha256
from typing import Any

import httpx

PARCEL_QUERY_URL = (
    "https://services3.arcgis.com/0dC3T96jvK0z64NH/"
    "arcgis/rest/services/parcelsActive_view/FeatureServer/0/query"
)

NEW_HAVEN_WHERE = "MUNI = 'New Haven'"

APPROVED_FIELDS = (
    "OBJECTID,GlobalID,rpsjoin,PRINT_KEY,SWIS,MUNI,"
    "TAX_STATUS,ACRES,PRP_CLS_CODE,PROP_CLASS"
)

EXPECTED_PARCEL_COUNT = 1_636
BATCH_SIZE = 1_000


class ArcGISQueryError(RuntimeError):
    """Raised when ArcGIS returns an application-level query error."""


def _raise_for_arcgis_error(payload: dict[str, Any]) -> None:
    """Raise when an HTTP-successful ArcGIS response contains an error."""
    error = payload.get("error")

    if error is None:
        return

    if isinstance(error, dict):
        code = error.get("code", "unknown")
        message = error.get("message", "Unknown ArcGIS error")
        details = error.get("details", [])
        raise ArcGISQueryError(
            f"ArcGIS query failed: code={code}, message={message}, details={details}"
        )

    raise ArcGISQueryError(f"ArcGIS query failed: {error}")


def fetch_object_ids(client: httpx.Client) -> list[int]:
    """Return sorted ArcGIS object IDs for the New Haven subset."""
    response = client.post(
        PARCEL_QUERY_URL,
        data={
            "f": "json",
            "where": NEW_HAVEN_WHERE,
            "returnIdsOnly": "true",
        },
    )
    response.raise_for_status()

    payload = response.json()
    _raise_for_arcgis_error(payload)

    raw_object_ids = payload.get("objectIds")

    if not isinstance(raw_object_ids, list):
        raise ArcGISQueryError("ArcGIS response did not contain objectIds")

    object_ids = sorted(int(value) for value in raw_object_ids)

    if len(object_ids) != EXPECTED_PARCEL_COUNT:
        raise ArcGISQueryError(
            f"Expected {EXPECTED_PARCEL_COUNT} object IDs, received {len(object_ids)}"
        )

    return object_ids


def fetch_parcel_batch(
    client: httpx.Client,
    object_ids: Sequence[int],
) -> list[dict[str, Any]]:
    """Fetch one bounded batch of parcel features and geometry."""
    if not object_ids:
        return []

    response = client.post(
        PARCEL_QUERY_URL,
        data={
            "f": "json",
            "objectIds": ",".join(str(value) for value in object_ids),
            "outFields": APPROVED_FIELDS,
            "returnGeometry": "true",
            "outSR": "2261",
        },
    )
    response.raise_for_status()

    payload = response.json()
    _raise_for_arcgis_error(payload)

    features = payload.get("features")

    if not isinstance(features, list):
        raise ArcGISQueryError("ArcGIS response did not contain features")

    return features


def fetch_new_haven_parcels() -> list[dict[str, Any]]:
    """Fetch and validate the complete deterministic New Haven subset."""
    features: list[dict[str, Any]] = []

    with httpx.Client(timeout=60.0) as client:
        object_ids = fetch_object_ids(client)

        for start in range(0, len(object_ids), BATCH_SIZE):
            batch_ids = object_ids[start : start + BATCH_SIZE]
            features.extend(fetch_parcel_batch(client, batch_ids))

    if len(features) != EXPECTED_PARCEL_COUNT:
        raise ArcGISQueryError(
            f"Expected {EXPECTED_PARCEL_COUNT} features, received {len(features)}"
        )

    global_ids: list[str] = []

    for feature in features:
        attributes = feature.get("attributes")

        if not isinstance(attributes, dict):
            raise ArcGISQueryError("Parcel feature is missing attributes")

        global_id = attributes.get("GlobalID")

        if not isinstance(global_id, str) or not global_id.strip():
            raise ArcGISQueryError("Parcel feature has no valid GlobalID")

        global_ids.append(global_id)

    if len(set(global_ids)) != len(global_ids):
        raise ArcGISQueryError("Duplicate GlobalID values were returned")

    return sorted(
        features,
        key=lambda feature: str(feature["attributes"]["GlobalID"]),
    )


def global_id_signature(features: list[dict[str, Any]]) -> str:
    """Create a reproducibility signature from ordered source GlobalIDs."""
    global_ids = [str(feature["attributes"]["GlobalID"]) for feature in features]

    encoded_ids = "\n".join(global_ids).encode("utf-8")
    return sha256(encoded_ids).hexdigest()


def source_snapshot_sha256(features: list[dict[str, Any]]) -> str:
    """Hash the complete ordered source snapshot, including geometry."""
    canonical_json = json.dumps(
        features,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return sha256(canonical_json.encode("utf-8")).hexdigest()


def main() -> None:
    features = fetch_new_haven_parcels()
    global_ids = [feature["attributes"]["GlobalID"] for feature in features]

    print(f"features={len(features)}")
    print(f"unique_global_ids={len(set(global_ids))}")
    print(f"global_id_signature={global_id_signature(features)}")
    print(f"source_snapshot_sha256={source_snapshot_sha256(features)}")


if __name__ == "__main__":
    main()
