from datetime import datetime
import zoneinfo
from sqlalchemy import extract, func
from starlette.concurrency import run_in_threadpool
from fastapi import Response, status, HTTPException, Depends, APIRouter, FastAPI, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import class_models, utility_functions, tb_models
from app.tb_models import Contributions
from app.utility_functions import id_gen

router = APIRouter(
    prefix="/contributions",
    tags=["contributions"],
)

NAIROBI_TZ = zoneinfo.ZoneInfo("Africa/Nairobi")


def normalize_to_nairobi(dt: datetime) -> datetime:
    """Ensures both naive and timezone-aware datetimes are cleanly mapped to Nairobi time."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # If naive (e.g., "2026-08-05 01:10:00"), explicitly set timezone to Nairobi
        return dt.replace(tzinfo=NAIROBI_TZ)
    # If timezone-aware, convert to Nairobi timezone
    return dt.astimezone(NAIROBI_TZ)


@router.post("/", status_code=201)
async def make_contribution(contribution_data: class_models.MakeContribution, db: Session = Depends(get_db)):
    def sync_db():
        contribution_id = id_gen()
        if contribution_data.contribution_amount > 0:
            new_cont = tb_models.Contributions(
                memb_member_id=contribution_data.member_id,
                contribution_id=contribution_id,
                cont_amount=contribution_data.contribution_amount
            )
            db.add(new_cont)
            db.commit()
            db.refresh(new_cont)
            return new_cont
        else:
            raise HTTPException(
                status_code=403,
                detail="Cannot make contribution of less than KSh0 in value "
            )

    return await run_in_threadpool(sync_db)


@router.post("/delete", status_code=201)
async def delete_contribution(contribution_id: str, db: Session = Depends(get_db)):
    def sync_db():
        contribution = db.get(tb_models.Contributions, contribution_id)
        if not contribution:
            raise HTTPException(status_code=404, detail="Contribution not found")

        db.delete(contribution)
        db.commit()

    return await run_in_threadpool(sync_db)


@router.get("/stats/monthly", status_code=201)
async def monthly_check(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    db: Session = Depends(get_db)
):
    def sync_db():
        contributions = db.query(tb_models.Contributions).filter(
            extract("month", func.timezone("Africa/Nairobi", tb_models.Contributions.contribution_date)) == month
        ).all()

        if not contributions:
            raise HTTPException(status_code=404, detail="Contribution not found")

        for c in contributions:
            if c.contribution_date:
                c.contribution_date = normalize_to_nairobi(c.contribution_date)

        total = sum(c.cont_amount for c in contributions)
        return {
            "contributions": [c.to_dict() for c in contributions],
            "total": total
        }

    return await run_in_threadpool(sync_db)


@router.get("/stats/year", status_code=201)
async def yearly_check(
    year: int = Query(..., ge=1900, le=3000, description="Year "),
    db: Session = Depends(get_db)
):
    def sync_db():
        contributions = db.query(tb_models.Contributions).filter(
            extract("year", func.timezone("Africa/Nairobi", tb_models.Contributions.contribution_date)) == year
        ).all()

        if not contributions:
            raise HTTPException(status_code=404, detail="Contribution not found")

        total = sum(c.cont_amount for c in contributions)

        for c in contributions:
            if c.contribution_date:
                c.contribution_date = normalize_to_nairobi(c.contribution_date)

        return {
            "contributions": [c.to_dict() for c in contributions],
            "total": total
        }

    return await run_in_threadpool(sync_db)


@router.get("/stats/indiv", status_code=201)
async def individual_check(member_id: str, db: Session = Depends(get_db)):
    def sync_db():
        total = db.query(func.sum(tb_models.Contributions.cont_amount)).filter(
            Contributions.memb_member_id == member_id
        ).scalar()

        if not total:
            raise HTTPException(status_code=404, detail="Contributions not found or member not found")

        contributions = db.query(tb_models.Contributions).filter(
            Contributions.memb_member_id == member_id
        ).all()

        for c in contributions:
            if c.contribution_date:
                c.contribution_date = normalize_to_nairobi(c.contribution_date)

        return {
            "contributions": [c.to_dict() for c in contributions],
            "total": total
        }

    return await run_in_threadpool(sync_db)


@router.get("/stats/search", status_code=201)
async def cont_search(cont_id: str, db: Session = Depends(get_db)):
    def sync_db():
        cont = db.query(tb_models.Contributions).get(cont_id)
        if not cont:
            raise HTTPException(status_code=404, detail="Contribution not found")

        if cont.contribution_date:
            cont.contribution_date = normalize_to_nairobi(cont.contribution_date)

        return cont

    return await run_in_threadpool(sync_db)


@router.post("/pstmb/cont")
async def add_pst_cont(
    contribution_data: class_models.UpdateCont,
    db: Session = Depends(get_db)
):
    def sync_db():
        contribution_id = id_gen()

        if contribution_data.contribution_amount > 0:
            # Safely normalize input date string/datetime to Nairobi time
            nairobi_date = normalize_to_nairobi(contribution_data.contribution_date)

            new_cont = tb_models.Contributions(
                memb_member_id=contribution_data.member_id,
                contribution_id=contribution_id,
                cont_amount=contribution_data.contribution_amount,
                contribution_date=nairobi_date
            )
            db.add(new_cont)
            db.commit()
            db.refresh(new_cont)
            return new_cont
        else:
            raise HTTPException(
                status_code=403,
                detail="Cannot make contribution of less than KSh0 in value "
            )

    return await run_in_threadpool(sync_db)