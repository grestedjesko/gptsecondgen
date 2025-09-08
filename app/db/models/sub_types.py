from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, relationship
from app.db.base import Base


class SubType(Base):
    __tablename__ = "sub_types"

    id = mapped_column(Integer, primary_key=True, autoincrement=False)
    name = mapped_column(String(255), nullable=False)

    config = relationship("SubTypeLimits", back_populates="subtype", uselist=False)
    subs = relationship("Subs", back_populates="subtype")
    user_subs = relationship("UserSubs", back_populates="subtype")
