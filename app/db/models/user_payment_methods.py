from sqlalchemy import Integer, String, ForeignKey, Column
from sqlalchemy.orm import relationship, Mapped
from app.db.base import Base


class UserPaymentMethod(Base):
    __tablename__ = 'user_payment_methods'
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey('users.user_id'))
    payment_method_id: Mapped[str] = Column(String(255), nullable=False)
    title: Mapped[str] = Column(String(255), nullable=False)

    user = relationship('User', back_populates='user_payment_methods')
    user_subs = relationship('UserSubs', back_populates='user_payment_methods')