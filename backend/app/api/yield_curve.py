from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import YieldObservation
from app.services.treasury import TENORS
from app.services.india_gsec import IndiaGsecDataError, fetch_india_gsec_history
from app.services.japan_gsec import JapanGsecDataError, fetch_japan_gsec_history
from app.services.taiwan_gsec import TaiwanGsecDataError, fetch_taiwan_gsec_history

router = APIRouter(prefix="/api/treasury-yields", tags=["Treasury yields"])
india_router = APIRouter(prefix="/api/india-gsec", tags=["Indian government securities"])
japan_router = APIRouter(prefix="/api/japan-gsec", tags=["Japanese government securities"])
taiwan_router = APIRouter(prefix="/api/taiwan-gsec", tags=["Taiwan government securities"])


def latest_stored_daily_yields(db: Session):
    """Return stored data only; web requests never call the Treasury service."""
    cutoff = date.today() - timedelta(days=1)
    observation_date = db.scalar(
        select(YieldObservation.observation_date)
        .where(YieldObservation.observation_date <= cutoff)
        .order_by(YieldObservation.observation_date.desc())
        .limit(1)
    )
    if observation_date is None:
        return None, []

    rows = db.scalars(
        select(YieldObservation).where(YieldObservation.observation_date == observation_date)
    ).all()
    order = {name: index for index, (name, _, _) in enumerate(TENORS)}
    rows.sort(key=lambda row: order.get(row.tenor, len(order)))
    return observation_date, rows


@router.get("/latest")
def get_latest(db: Session = Depends(get_db)):
    observation_date, rows = latest_stored_daily_yields(db)
    if not rows:
        raise HTTPException(
            status_code=404,
            detail="No stored Treasury observations are available for yesterday or earlier. Import historical data first.",
        )

    return {
        "source": "US Treasury Daily Par Yield Curve",
        "observation_date": observation_date,
        "data_status": "Historical daily observation (latest stored value no later than yesterday)",
        "yields": [
            {
                "tenor": row.tenor,
                "maturity_years": row.maturity_years,
                "yield_percent": row.yield_percent,
            }
            for row in rows
        ],
    }


@india_router.get("/history")
async def get_india_gsec_history(tenor: str = Query("10Y", pattern="^(1Y|2Y|5Y|10Y)$")):
    """Return public RBI DBIE Indian government-bond yield history."""
    try:
        return await fetch_india_gsec_history(tenor)
    except IndiaGsecDataError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@japan_router.get("/history")
async def get_japan_gsec_history(tenor: str = Query("10Y", pattern="^(1Y|2Y|5Y|10Y)$")):
    """Return daily Japanese government-bond constant-maturity yield history."""
    try:
        return await fetch_japan_gsec_history(tenor)
    except JapanGsecDataError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@taiwan_router.get("/history")
async def get_taiwan_gsec_history(tenor: str = Query("10Y", pattern="^(2Y|5Y|10Y)$")):
    """Return daily Taiwan government-bond benchmark yield history."""
    try:
        return await fetch_taiwan_gsec_history(tenor)
    except TaiwanGsecDataError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
