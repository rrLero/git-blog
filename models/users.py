from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import select
from sqlalchemy.orm import relationship


Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_name = Column(String(100), nullable=False)
    user_repo_name = Column(String(100), nullable=False)

    # relationships
    lnk_favorites_users_2 = relationship('Favorites')

    def __init__(self, user_name, user_repo_name):
        self.user_name = user_name
        self.user_repo_name = user_repo_name
        self.engine = create_engine('sqlite:///git-blog.sqlite')

    # opens data base to work with it
    def open_base(self):
        Base = declarative_base()
        Base.metadata.create_all(self.engine)
        Base.metadata.bind = self.engine
        DBSession = sessionmaker(bind=self.engine)
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

    def del_table(self, table_name):
        m = MetaData()
        table = Table('%s' % table_name.lower(), m,
                      Column('id', Integer),
                      )
        table.drop(self.engine)
        return 'ok'

    def create_table(self, table_name):
        m = MetaData()
        table = Table('%s' % table_name.lower(), m,
                      Column('id', Integer, unique=True),
                      )
        table.create(self.engine)
        return 'ok'

    def insert_row(self, table_name, id_blog):
        m = MetaData()
        table = Table('%s' % table_name.lower(), m,
                      Column('id', Integer, unique=True),
                      )
        ins = table.insert().values(id=id_blog)
        conn = self.engine.connect()
        conn.execute(ins)
        return 'ok'

    def delete_row(self, table_name, id_blog):
        conn = self.engine.connect()
        meta = MetaData(self.engine, reflect=True)
        user_t = meta.tables[table_name.lower()]
        sel_st = user_t.select()
        conn.execute(sel_st)
        del_st = user_t.delete().where(
            user_t.c.id == id_blog)
        conn.execute(del_st)
        sel_st = user_t.select()
        conn.execute(sel_st)
        return 'ok'

    def get_row(self, table_name):
        m = MetaData()
        conn = self.engine.connect()
        table = Table('%s' % table_name.lower(), m,
                      Column('id', Integer, unique=True),
                      )
        select_st = select([table]).where(
            table.c.id)
        res = conn.execute(select_st)
        return res


class Favorites(Base):
    __tablename__ = 'favorites'

    user_name = Column(String(100), ForeignKey('users.user_name'), nullable=False,)
    id = Column(Integer, nullable=False, )
    user_name_id = Column(String(100), nullable=False, unique=True, primary_key=True)

    def __init__(self, user_name, id):
        self.engine = create_engine('sqlite:///git-blog.sqlite')
        self.user_name = user_name
        self.id = id
        self.user_name_id = '%s_%s' % (user_name, id)

    def open_base(self):
        Base = declarative_base()
        Base.metadata.create_all(self.engine)
        Base.metadata.bind = self.engine
        DBSession = sessionmaker(bind=self.engine)
        session_git = DBSession()
        return session_git

    def new_favor(self):
        session_git = self.open_base()
        new_favor = Favorites(user_name=self.user_name, id=self.id)
        session_git.add(new_favor)
        session_git.commit()
        session_git.close()
        return 'ok'

    def del_favor(self):
        session_git = self.open_base()
        query = session_git.query(Favorites)
        new_favor = query.get('%s' % self.user_name_id)
        session_git.delete(new_favor)
        session_git.commit()
        session_git.close()
        return 'ok'

    def get_favor_by_name(self):
        session_git = self.open_base()
        list_blogs = []
        query = session_git.query(Favorites).filter(Favorites.user_name == self.user_name)
        for one_id in query:
            list_blogs.append(one_id.id)
        session_git.close()
        return list_blogs

