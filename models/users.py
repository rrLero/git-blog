from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_name = Column(String(100), nullable=False)
    user_repo_name = Column(String(100), nullable=False)

    def __init__(self, user_name, user_repo_name):
        self.user_name = user_name
        self.user_repo_name = user_repo_name
