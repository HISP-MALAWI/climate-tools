import csv
import io
from dhis2_client import DHIS2Client
from dhis2_client.settings import ClientSettings

def prepare_data(base_url, username, password, dx, ou_level, pe):
    """
    Fetch DHIS2 analytics for a single indicator (dx) and period (pe),
    join with org units at the specified level, and return CSV as string.
    
    Args:
        base_url (str): DHIS2 instance URL
        username (str): DHIS2 username
        password (str): DHIS2 password
        dx (str): Data element or indicator UID
        ou_level (int): Organisation unit level
        pe (str): Period (YYYYMM)
    
    Returns:
        str: CSV output as string
    """

    # --- Configure DHIS2 client ---
    cfg = ClientSettings(
        base_url=base_url,
        username=username,
        password=password
    )
    client = DHIS2Client(settings=cfg)

    # --- Fetch org units GeoJSON ---
    org = client.get_org_units_geojson_by_level(ou_level)

    # --- Fetch analytics for the given dx and period ---
    ana = client.get_analytics(
        table="analytics",
        dimension=[f"dx:{dx}", f"ou:LEVEL-{ou_level}", f"pe:{pe}"]
    )

    # --- Build header-based records ---
    headers = [h["name"] for h in ana["headers"]]
    records = [dict(zip(headers, row)) for row in ana.get("rows", [])]

    # --- Build a lookup map for quick access ---
    ana_map = {r["ou"]: {"value": r["value"], "pe": r["pe"]} for r in records}

    # --- Prepare CSV output ---
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['facility', 'id', 'lat', 'lon', 'year', 'month', 'cases'])

    # --- Merge analytics with org units ---
    for ou in org.get("features", []):
        uid = ou.get('id')
        props = ou.get('properties', {})
        geom = ou.get('geometry', {})

        name = props.get("name", "").replace(" ", "_")
        coords = geom.get("coordinates")
        if not coords or not uid:
            continue

        lon, lat = coords

        entry = ana_map.get(uid)
        if not entry:
            continue

        v = entry["value"]
        period_val = entry["pe"]
        writer.writerow([
            name,
            uid,
            lat,
            lon,
            period_val[:4],    # year
            period_val[4:],    # month
            v
        ])

    return output.getvalue()
