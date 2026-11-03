from datetime import date
import httpx
import xml.etree.ElementTree as ET
from app.core.config import settings

TENORS = [
    ("1M", "BC_1MONTH", 1 / 12),
    ("1.5M", "BC_1_5MONTH", 1.5 / 12),
    ("2M", "BC_2MONTH", 2 / 12),
    ("3M", "BC_3MONTH", 0.25),
    ("4M", "BC_4MONTH", 4 / 12),
    ("6M", "BC_6MONTH", 0.5),
    ("1Y", "BC_1YEAR", 1.0),
    ("2Y", "BC_2YEAR", 2.0),
    ("3Y", "BC_3YEAR", 3.0),
    ("5Y", "BC_5YEAR", 5.0),
    ("7Y", "BC_7YEAR", 7.0),
    ("10Y", "BC_10YEAR", 10.0),
    ("20Y", "BC_20YEAR", 20.0),
    ("30Y", "BC_30YEAR", 30.0),
]

def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].split(":", 1)[-1]

def parse_treasury_xml(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    records = []

    # Treasury publishes an Atom feed. Values are commonly nested under
    # m:properties/d:FIELD; local-name matching avoids namespace coupling.
    for entry in root.iter():
        if _local(entry.tag) != "entry":
            continue
        fields = {}
        for node in entry.iter():
            name = _local(node.tag)
            if name in {"NEW_DATE", *(field for _, field, _ in TENORS)}:
                fields[name] = node.text

        raw_date = fields.get("NEW_DATE")
        if not raw_date:
            continue

        try:
            observation_date = date.fromisoformat(raw_date[:10])
        except ValueError:
            continue

        points = []
        for tenor, field, maturity in TENORS:
            raw = fields.get(field)
            if raw is None or not raw.strip() or raw.strip() in {"N/A", "NA"}:
                continue
            try:
                value = float(raw)
            except ValueError:
                continue
            points.append({
                "observation_date": observation_date,
                "tenor": tenor,
                "maturity_years": maturity,
                "yield_percent": value,
            })
        if points:
            records.extend(points)
    return records

async def fetch_month(year_month: str) -> list[dict]:
    params = {
        "data": "daily_treasury_yield_curve",
        "field_tdr_date_value_month": year_month,
    }
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(settings.treasury_base_url, params=params)
        response.raise_for_status()
    return parse_treasury_xml(response.text)
