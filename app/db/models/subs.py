from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, relationship
from app.db.base import Base
import enum
from sqlalchemy import Enum as SAEnum



class SubsKind(enum.Enum):
    BASE = "base"   # обычный план
    TRIAL = "trial" # триал/вступительный оффер


class Subs(Base):
    __tablename__ = "subs"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(255), nullable=False)
    subtype_id = mapped_column(ForeignKey("sub_types.id"), nullable=False)

    kind = mapped_column(SAEnum(SubsKind, name="subs_kind"), default=SubsKind.BASE, nullable=False)
    base_sub_id = mapped_column(ForeignKey("subs.id"), nullable=True)

    period = mapped_column(Integer, nullable=False)
    price = mapped_column(Integer, nullable=False)
    stars_price = mapped_column(Integer, nullable=False)
    is_visible = mapped_column(Boolean, default=False)

    subtype = relationship("SubType", back_populates="subs")
    user_subs = relationship("UserSubs", back_populates="subs")
    user_trial_usage = relationship("UserTrialUsage", back_populates="trial_plan")
    invoices = relationship("Invoice", back_populates="subs")