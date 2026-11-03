"""Import a month of Treasury daily par yields as a deliberate admin action."""
import argparse
import asyncio
from datetime import datetime

from sqlalchemy import select

from app.db import SessionLocal
from app.models import YieldObservation
from app.services.treasury import fetch_month


def save_records(records: list[dict]) -> tuple[int, int]:
    inserted = 0
    updated = 0
    with SessionLocal() as db:
        for record in records:
            existing = db.scalar(
                select(YieldObservation).where(
                    YieldObservation.observation_date == record["observation_date"],
                    YieldObservation.tenor == record["tenor"],
                )
            )
            if existing is None:
                db.add(YieldObservation(**record))
                inserted += 1
            else:
                existing.maturity_years = record["maturity_years"]
                existing.yield_percent = record["yield_percent"]
                updated += 1
        db.commit()
    return inserted, updated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--month", required=True, help="Treasury month in YYYYMM format")
    args = parser.parse_args()
    datetime.strptime(args.month, "%Y%m")

    records = asyncio.run(fetch_month(args.month))
    inserted, updated = save_records(records)
    print(f"Imported {len(records)} observations: {inserted} inserted, {updated} updated.")


if __name__ == "__main__":
    main()
