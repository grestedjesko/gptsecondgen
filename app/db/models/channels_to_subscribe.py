from sqlalchemy import Integer, VARCHAR
from sqlalchemy.orm import mapped_column
from app.db.base import Base


class ChannelsToSubcribe(Base):
    __tablename__ = "channels_to_subscribe"

    id = mapped_column(Integer, primary_key=True)
    channel_id = mapped_column(Integer, nullable=False)
    channel_link = mapped_column(VARCHAR, nullable=False)
    subs_count = mapped_column(Integer, nullable=False)
    total_count = mapped_column(Integer, nullable=False)
