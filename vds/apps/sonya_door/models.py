from django.db import models
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, String, Table, TIME, TIMESTAMP
from sqlalchemy.types import DECIMAL
# Create your models here.

Base = declarative_base()

class Users(Base):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    obed = Column(DECIMAL)
    otpusk = Column(Integer)
    bolezn = Column(Integer)
    poezdka = Column(Integer)
    deni = Column(DECIMAL)
    time = Column(TIMESTAMP)
    workdays = Column(Integer)
    other = Column(DECIMAL)
    work_time_start = Column(TIME)
    work_time_end = Column(TIME)
    
    def __init__(self, id_user):
        self.id = id
        self.obed = obed
        self.otpusk = otpusk
        self.bolezn = bolezn
        self.poezdka = poezdka
        self.deni = deni
        self.time = time
        self.workdays = workdays
        self.other = other
        self.work_time_start = work_time_start
        self.work_time_end = work_time_end

class HR(Base):
    __tablename__ = 'hr'
    id = Column(Integer, primary_key=True)
    text = Column(Text)
    
    def __init__(self):
        self.id = id
        self.hr = hr

class WorkDays(Base):
    __tablename__ = 'work_days'
    id = Column(Integer, primary_key=True)
    daycount = Column(Integer)
    yearmonth = Column(TIMESTAMP)

    def __init__(self):
    	self.daycount = daycount
    	self.yearmonth = yearmonth
