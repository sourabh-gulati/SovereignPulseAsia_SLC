from datetime import date
from pydantic import BaseModel

class YieldPoint(BaseModel):
    tenor: str
    maturity_years: float
    yield_percent: float

class YieldCurveResponse(BaseModel):
    source: str
    observation_date: date
    yields: list[YieldPoint]
    data_status: str
