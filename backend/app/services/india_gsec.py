"""Indian sovereign yield history from the public RBI DBIE data mirror."""
from calendar import monthrange
from datetime import date
import re
import httpx

DBIE_ROWS_URL = "https://data-api.dbie.rbihub.in/api/tables/financial_markets/r217_month_end_yield_of_sgl_transactions_in_government_dated_se/rows"
MONTHS = (4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3)
class IndiaGsecDataError(Exception): pass

async def fetch_india_gsec_history(tenor: str) -> dict:
    """Return RBI month-end YTM history for the selected whole-year maturity."""
    if tenor not in {"1Y", "2Y", "5Y", "10Y"}: raise ValueError("Tenor must be one of: 1Y, 2Y, 5Y, 10Y.")
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(DBIE_ROWS_URL, params={"limit": 1000}); response.raise_for_status(); rows = response.json().get("rows", [])
    except (httpx.HTTPError, ValueError) as exc:
        raise IndiaGsecDataError("The RBI DBIE data service is currently unavailable.") from exc
    points, financial_year = [], None
    for row in rows:
        first = str(row[4] or "").strip(); match = re.fullmatch(r"(\d{4})-\d{2}", first)
        if match: financial_year = int(match.group(1)); continue
        if financial_year is None or first != tenor[:-1]: continue
        for index, month in enumerate(MONTHS, start=5):
            value = row[index] if index < len(row) else None
            if value in (None, "", " -", "-"): continue
            try: yield_percent = float(str(value).strip())
            except ValueError: continue
            year = financial_year if month >= 4 else financial_year + 1
            points.append({"date": date(year, month, monthrange(year, month)[1]), "yield_percent": yield_percent})
    if not points: raise IndiaGsecDataError("The RBI DBIE service returned no usable observations for this maturity.")
    points.sort(key=lambda point: point["date"])
    return {"source": "Reserve Bank of India (DBIE report 217, via public DBIE mirror)", "tenor": tenor, "data_status": "Monthly month-end yield to maturity; published with the RBI DBIE release schedule.", "points": points}
