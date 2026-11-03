"""Japanese government-bond yield history from Japan's Ministry of Finance."""

import csv
from datetime import date, datetime, timedelta
from io import StringIO

import httpx

JGB_HISTORY_URL = (
    "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/"
    "historical/jgbcme_all.csv"
)
SUPPORTED_TENORS = {"1Y", "2Y", "5Y", "10Y"}


class JapanGsecDataError(Exception):
    pass


def parse_jgb_csv(csv_text: str, tenor: str) -> list[dict]:
    """Parse Ministry of Finance constant-maturity JGB CSV data."""
    rows = csv.reader(StringIO(csv_text))
    next(rows, None)  # Title and unit row.
    header = next(rows, None)
    if not header or "Date" not in header or tenor not in header:
        raise JapanGsecDataError("The Ministry of Finance data format is not recognised.")

    tenor_index = header.index(tenor)
    points = []
    for row in rows:
        if len(row) <= tenor_index or row[tenor_index].strip() in {"", "-"}:
            continue
        try:
            observation_date = datetime.strptime(row[0].strip(), "%Y/%m/%d").date()
            yield_percent = float(row[tenor_index].strip())
        except (ValueError, IndexError):
            continue
        points.append({"date": observation_date, "yield_percent": yield_percent})
    return points


async def fetch_japan_gsec_history(tenor: str) -> dict:
    """Return a one-year daily JGB history for the selected maturity."""
    if tenor not in SUPPORTED_TENORS:
        raise ValueError("Tenor must be one of: 1Y, 2Y, 5Y, 10Y.")

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(JGB_HISTORY_URL)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise JapanGsecDataError("The Japan Ministry of Finance data service is currently unavailable.") from exc

    points = parse_jgb_csv(response.text, tenor)
    cutoff = date.today() - timedelta(days=365)
    points = [point for point in points if point["date"] >= cutoff]
    if not points:
        raise JapanGsecDataError("The Ministry of Finance service returned no usable observations for this maturity.")

    return {
        "source": "Japan Ministry of Finance — JGB Interest Rate",
        "tenor": tenor,
        "data_status": "Daily constant-maturity yield; most recent 12 months.",
        "points": points,
    }
