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

    # opens data base to work with it
    def open_base(self):
        Base = declarative_base()
        engine = create_engine('sqlite:///git-blog.sqlite')
        Base.metadata.create_all(engine)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session_git = DBSession()
        return session_git

    def new_user(self):
        session_git = self.open_base()
        users = session_git.query(Users)
        new_user = True
        for user in users:
            if user.user_name == self.user_name.lower() and user.user_repo_name == self.user_repo_name.lower():
                session_git.close()
                new_user = False
        if new_user:
            new_user = Users(user_name=self.user_name.lower(), user_repo_name=self.user_repo_name.lower())
            session_git.add(new_user)
            session_git.commit()
            session_git.close()
        return new_user
