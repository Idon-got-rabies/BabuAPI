from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional, List

class Mem(BaseModel):
    member_id: str
    member_name: str
    member_id_number: str
    member_tell_number: str

class Member(Mem):
    total_member_contribution: int


class ContributionIndividual(BaseModel):
    member_id: int
    cont_ind_amount: float
    cont_ind_date: datetime

class StkFormat(Mem):
    prompt_amount: float
    prompt_date: datetime

class MemCreation(BaseModel):
    member_name: str
    member_id_number: str
    member_tell_number: str

class UpdateMem(BaseModel):
    member_name: Optional[str] = None
    member_id_number: Optional[str] = None
    member_tell_number: Optional[str] = None

class MakeContribution(BaseModel):
    member_id: str
    contribution_amount: float

class UpdateCont(BaseModel):
    member_id: Optional[str] = None
    contribution_amount: Optional[float] = None
    contribution_date: Optional[datetime] = None








