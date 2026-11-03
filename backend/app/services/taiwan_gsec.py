"""Taiwan government-bond benchmark yield history from the Taipei Exchange."""

import asyncio
from datetime import date, datetime, timedelta, timezone

import httpx
import xlrd

SUPPORTED_TENORS = {"2Y": 2.0, "5Y": 5.0, "10Y": 10.0}
CACHE_TTL = timedelta(hours=12)
_cache: tuple[datetime, list[dict]] | None = None


class TaiwanGsecDataError(Exception):
    pass


def benchmark_file_url(observation_date: date) -> str:
    year_month = observation_date.strftime("%Y%m")
    date_string = observation_date.strftime("%Y%m%d")
    return (
        "https://www.tpex.org.tw/storage/bond_zone/tradeinfo/govbond/"
        f"{observation_date.year}/{year_month}/BDdys100.{date_string}-C.xls"
    )


def parse_benchmark_workbook(workbook_bytes: bytes) -> list[dict]:
    """Read 2Y, 5Y, and 10Y weighted-average yields from a TPEx workbook."""
    workbook = xlrd.open_workbook(file_contents=workbook_bytes)
    sheet = workbook.sheet_by_index(0)
    points = []
    for row_index in range(sheet.nrows):
        row = sheet.row_values(row_index)
        if len(row) < 3 or not isinstance(row[0], (int, float)):
            continue
        tenor = next((name for name, years in SUPPORTED_TENORS.items() if row[0] == years), None)
        if tenor is None or row[2] in ("", "-"):
            continue
        try:
            points.append({"tenor": tenor, "yield_percent": float(row[2])})
        except (TypeError, ValueError):
            continue
    return points


async def _fetch_recent_history() -> list[dict]:
    global _cache
    now = datetime.now(timezone.utc)
    today = now.date()
    if _cache and now - _cache[0] < CACHE_TTL:
        return _cache[1]

    candidate_dates = [today - timedelta(days=offset) for offset in range(45)]
    # TPEx currently serves a certificate rejected by some OpenSSL/Python builds
    # (missing Subject Key Identifier). This exception is limited to its public,
    # read-only benchmark workbook endpoint.
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True, verify=False) as client:
        responses = await asyncio.gather(
            *(client.get(benchmark_file_url(candidate_date)) for candidate_date in candidate_dates),
            return_exceptions=True,
        )

    history = []
    for candidate_date, response in zip(candidate_dates, responses, strict=True):
        if isinstance(response, Exception) or response.status_code != 200:
            continue
        try:
            for point in parse_benchmark_workbook(response.content):
                history.append({"date": candidate_date, **point})
        except (xlrd.XLRDError, IndexError):
            continue

    if not history:
        raise TaiwanGsecDataError("The Taipei Exchange data service returned no usable benchmark yields.")
    history.sort(key=lambda point: point["date"])
    _cache = (now, history)
    return history


async def fetch_taiwan_gsec_history(tenor: str) -> dict:
    if tenor not in SUPPORTED_TENORS:
        raise ValueError("Tenor must be one of: 2Y, 5Y, 10Y.")
    history = await _fetch_recent_history()
    points = [{"date": point["date"], "yield_percent": point["yield_percent"]} for point in history if point["tenor"] == tenor]
    if not points:
        raise TaiwanGsecDataError("The Taipei Exchange data service returned no usable observations for this maturity.")
    return {
        "source": "Taipei Exchange — Daily Benchmark Yield",
        "tenor": tenor,
        "data_status": "Daily weighted-average benchmark yield; recent available observations.",
        "points": points,
    }
