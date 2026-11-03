from datetime import date

from app.services import taiwan_gsec
from app.services.taiwan_gsec import benchmark_file_url


def test_benchmark_file_url_uses_tpex_daily_file_convention():
    assert benchmark_file_url(date(2026, 11, 2)) == (
        "https://www.tpex.org.tw/storage/bond_zone/tradeinfo/govbond/"
        "2026/202611/BDdys100.20261102-C.xls"
    )


def test_tpex_client_allows_its_known_certificate_compatibility_issue(monkeypatch):
    options = {}

    class FakeClient:
        def __init__(self, **kwargs):
            options.update(kwargs)

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url):
            raise RuntimeError("stop after client configuration")

    monkeypatch.setattr(taiwan_gsec.httpx, "AsyncClient", FakeClient)

    import asyncio

    try:
        asyncio.run(taiwan_gsec._fetch_recent_history())
    except taiwan_gsec.TaiwanGsecDataError:
        pass

    assert options["verify"] is False
