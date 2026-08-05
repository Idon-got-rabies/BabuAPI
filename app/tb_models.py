from datetime import datetime, timezone
from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, column, Date, ARRAY, Double, DateTime
from sqlalchemy.sql.sqltypes import TIMESTAMP, Boolean
from sqlalchemy.sql.expression import text


class Member(Base):
    __tablename__ = 'members'
    member_id = Column(String, primary_key=True, nullable=False)
    member_name = Column(String, nullable=False)
    member_tel = Column(String, nullable=False)
    member_id_num = Column(String, nullable=False)
    is_active = Column(Boolean,default=True, nullable=False)

    def to_dict(self):
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

class Contributions (Base):
    __tablename__ = 'contributions'
    contribution_id = Column(String, primary_key=True, nullable=False)
    memb_member_id = Column(String, ForeignKey('members.member_id'))
    cont_amount = Column(Double, nullable=False)
    contribution_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }



