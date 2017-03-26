from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_name = Column(String(100), nullable=False)
    user_repo_name = Column(String(100), nullable=False)

    def __init__(self, user_name, user_repo_name):
        self.user_name = user_name
        self.user_repo_name = user_repo_name

    # функция открывает базу данных для последующей работы с ней
    def open_base(self):
        Base = declarative_base()
        engine = create_engine('sqlite:///git-blog.sqlite')
        Base.metadata.create_all(engine)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session_git = DBSession()
        return session_git
