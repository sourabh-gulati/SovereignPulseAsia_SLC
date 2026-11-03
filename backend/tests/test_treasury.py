from app.services.treasury import TENORS, parse_treasury_xml


def test_supported_tenors_cover_one_month_through_thirty_years():
    assert TENORS[0][0] == "1M"
    assert TENORS[-1][0] == "30Y"
    assert {"2M", "3Y", "7Y", "20Y"}.issubset({tenor for tenor, _, _ in TENORS})


def test_parse_treasury_xml_preserves_available_values():
    xml = """
    <feed xmlns:d="urn:data"><entry><d:NEW_DATE>2026-11-02T00:00:00</d:NEW_DATE>
    <d:BC_1MONTH>3.71</d:BC_1MONTH><d:BC_30YEAR>4.32</d:BC_30YEAR></entry></feed>
    """
    records = parse_treasury_xml(xml)

    assert [(record["tenor"], record["yield_percent"]) for record in records] == [
        ("1M", 3.71),
        ("30Y", 4.32),
    ]
