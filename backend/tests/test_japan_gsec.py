from datetime import date

from app.services.japan_gsec import parse_jgb_csv


def test_parse_jgb_csv_returns_requested_tenor_and_omits_missing_values():
    csv_text = """Interest Rate (October 2026),,,(Unit : %)
Date,1Y,2Y,5Y,10Y
2026/10/1,1.668,1.939,2.407,3.092
2026/10/2,-,1.919,2.397,3.097
"""

    assert parse_jgb_csv(csv_text, "10Y") == [
        {"date": date(2026, 10, 1), "yield_percent": 3.092},
        {"date": date(2026, 10, 2), "yield_percent": 3.097},
    ]
