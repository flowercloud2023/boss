from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import os
database = f'sqlite:///{os.path.dirname(__file__)}\\data.db'

Base = declarative_base()
engine = create_engine(database)
DBSession = sessionmaker(bind=engine)
SQLsession = DBSession()

# ORM
class Candidate(Base):
    __tablename__ = 'candidate'
    id = Column(Integer(), primary_key=True)
    account = Column(String(255))
    name = Column(String(255))
    education = Column(String(255))
    age = Column(String(255))
    job = Column(String(255))
    location = Column(String(255))
    grade = Column(Text())
    style = Column(String(255))
    chat = Column(String(255))
    firsttime = Column(String(255))
    secondtime = Column(String(255))
    resume = Column(String(255))
    status = Column(Integer(), default=1)
    remark = Column(Text)
    created = Column(Date, default=datetime.now())
    updated = Column(Date, default=datetime.now(), onupdate=datetime.now())

Base.metadata.create_all(engine)