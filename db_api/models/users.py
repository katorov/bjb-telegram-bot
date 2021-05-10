from sqlalchemy import Column, BigInteger, String, sql, Boolean

from db_api.db_gino import TimedBaseModel


class User(TimedBaseModel):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    first_name = Column(String(255), nullable=False, default='')
    last_name = Column(String(255), nullable=False, default='')
    timezone = Column(String(255), nullable=False, default='Europe/Moscow')
    token = Column(String(500), default='')
    admin_access = Column(Boolean, default=False)
    team_access = Column(Boolean, default=False)

    query: sql.Select
