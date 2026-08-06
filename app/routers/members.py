from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Response, status, HTTPException, Depends,APIRouter
from starlette.concurrency import run_in_threadpool
from app import class_models, tb_models, utility_functions
from app.utility_functions import id_gen
from typing import Optional

router = APIRouter(
    prefix="/members",
    tags=["members"],
)

@router.post("/", status_code=201)
async def create_member(member: class_models.MemCreation, db: Session = Depends(get_db)):
    def sync_db():
        mem_id = id_gen()
        if utility_functions.num_val(9, member.member_id_number) or utility_functions.num_val(8, member.member_id_number):
            member_id_num = member.member_id_number
        else:
            raise HTTPException(status_code=400, detail="I.D number length/type invalid")

        if utility_functions.num_val(10, member.member_tell_number):
            member_num = member.member_tell_number
        else:
            raise HTTPException(status_code=400, detail="Phone number length/type invalid")

        new_member = tb_models.Member(
            member_id=mem_id,
            member_name=member.member_name,
            member_id_num=member_id_num,
            member_tel=member_num
        )
        db.add(new_member)
        db.commit()
        db.refresh(new_member)
        return new_member
    return await run_in_threadpool(sync_db)

@router.post("/del", status_code=200)
async def delete_member(member_id: str, db: Session = Depends(get_db)):
    def sync_db():
        member = db.query(tb_models.Member).get(member_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        elif not member.is_active:
            raise HTTPException(status_code=404, detail="Member not found")
        else:
            member.is_active = False
            db.commit()
    return await run_in_threadpool(sync_db)


@router.patch("/sct", status_code=200)
async def update_member(
    member_id: str,
    mem_udpdate_data: class_models.UpdateMem,
    db: Session = Depends(get_db)
):
    def sync_db():
        member = db.query(tb_models.Member).filter(
            tb_models.Member.member_id == member_id.strip()
        ).first()

        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        if mem_udpdate_data.member_id_number is not None:
            if utility_functions.num_val(9, mem_udpdate_data.member_id_number) or utility_functions.num_val(8,
                                                                                                  mem_udpdate_data.member_id_number):
                pass
            else:
                raise HTTPException(status_code=400, detail="I.D number length/type invalid")

        if mem_udpdate_data.member_tell_number is not None:
            if utility_functions.num_val(10, mem_udpdate_data.member_tell_number):
                pass
            else:
                raise HTTPException(status_code=400, detail="Phone number length/type invalid")

        update_data = mem_udpdate_data.model_dump(exclude_unset=True)

        # Map incoming Pydantic keys to exact database Column names
        field_mapping = {
            "member_name": "member_name",
            "member_id_number": "member_id_num",      # maps member_id_number -> member_id_num
            "member_tell_number": "member_tel",        # maps member_tell_number -> member_tel
        }

        for field, value in update_data.items():
            db_column = field_mapping.get(field, field)
            if hasattr(member, db_column):
                setattr(member, db_column, value)

        db.commit()
        return member

    return await run_in_threadpool(sync_db)

@router.get("/mserch", status_code=status.HTTP_200_OK)
async def get_members(
    member_name: Optional[str] = None,
    member_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    def sync_db():
        query = db.query(tb_models.Member)

        # 1. Filter by Primary Key / Exact Member ID if provided
        if member_id and member_id.strip():
            query = query.filter(tb_models.Member.member_id == member_id.strip(), tb_models.Member.is_active == True)

        # 2. Filter by Name (Case-insensitive partial match) if provided
        if member_name and member_name.strip():
            query = query.filter(
                tb_models.Member.member_name.ilike(f"%{member_name.strip()}%"),
                tb_models.Member.is_active == True
            )

        # Execute query — .all() ALWAYS returns a list (even if empty `[]`)
        members = query.where(tb_models.Member.is_active == True).all()
        if members is None:
            raise HTTPException(status_code=404, detail="Member not found")
        return {
            "members": [m.to_dict() for m in members]
        }

    return await run_in_threadpool(sync_db)

@router.get("/pst", status_code=status.HTTP_200_OK)
async def get_pst_members(
    member_name: Optional[str] = None,
    member_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    def sync_db():
        query = db.query(tb_models.Member)

        if member_id and member_id.strip():
            query = query.filter(tb_models.Member.member_id == member_id.strip(),
                                 tb_models.Member.is_active == False)

        if member_name and member_name.strip():
            query = query.filter(
                tb_models.Member.member_name.ilike(f"%{member_name.strip()}%"),
                tb_models.Member.is_active == False
            )

        members = query.where(tb_models.Member.is_active == False).all()
        if members is None:
            raise HTTPException(status_code=404, detail="Member not found")
        return {
            "members": [m.to_dict() for m in members]
        }
    return await run_in_threadpool(sync_db)








