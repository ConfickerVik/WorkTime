from django.shortcuts import render
from django.http import HttpResponseRedirect
#from django.shortcuts import render_to_response
import sqlalchemy, sqlalchemy.orm
from sqlalchemy import extract
from django.conf import settings
from sonya_door.models import *
import struct
from sonya_door.sonya import Serialize
from vds.mdb import Mdbconnect
import pickle
import datetime


def list(request):
	objStat = Serialize()
	db_engine = sqlalchemy.create_engine(settings.SQLALCHEMY_DATABASE_URI)
	Session = sqlalchemy.orm.sessionmaker(bind=db_engine)
	session = Session()
	Base.metadata.create_all(db_engine)
	stat = {}
	date = str(datetime.date.today())[:-3]
	stat = objStat.restructuring(date)
	if request.POST:
		
		if request.POST.get('date'):
			date = request.POST.get('date')
			stat = objStat.restructuring(date)

		if request.POST.get('workdayscount'):
			workdayscount = request.POST.get('workdayscount')
			print("interesno ",workdayscount)
			with open(settings.STATIC_CACHE_SONYA,'rb') as cahce:
				stat = pickle.load(cahce)
			for key in stat.keys():
				stat[key]['info']['workdays'] = workdayscount
				query = session.query(Users).filter(Users.id == int(key)).update({Users.workdays: workdayscount}, synchronize_session=False)
				session.commit()

		if request.POST.get('saveworkdaysall'):
			with open(settings.STATIC_CACHE_SONYA,'rb') as cahce:
				stat = pickle.load(cahce)
			#stat = objStat.restructuring(date)
			for key in stat.keys():
				try:
					year, mon = date.split("-")
					if mon == '1':
						s = session.query(Users).filter(Users.id == int(key), extract('year', Users.time) == year, extract('month', Users.time) == 12).all()
					else: 
						s = session.query(Users).filter(Users.id == int(key), extract('year', Users.time) == year, extract('month', Users.time) == int(mon)-1).all()
					stat[key]['info']['deni'] = s[0].deni
					session.query(Users).filter(Users.id == int(key)).update({Users.deni: s[0].deni}, synchronize_session=False)
					session.commit()
				except IndexError as e:
					pass

		if request.POST.get('saveall'):
			with open(settings.STATIC_CACHE_SONYA,'rb') as cahce:
				stat = pickle.load(cahce)
			otpusklist = request.POST.getlist('otpusk')
			boleznlist = request.POST.getlist('bolezn')
			poezdkalist = request.POST.getlist('poezdka')
			denilist = request.POST.getlist('deni')
			workdayslist = request.POST.getlist('workdays')
			otherlist = request.POST.getlist('other')
			work_time_startlist = request.POST.getlist('work_time_start')
			work_time_endlist = request.POST.getlist('work_time_end')
			i = 0
			for key in stat.keys():
				session.query(Users).filter(Users.id == int(key)).update({Users.otpusk: otpusklist[i], Users.bolezn: boleznlist[i], 
					Users.poezdka: poezdkalist[i], Users.deni: denilist[i], Users.workdays: workdayslist[i], Users.other: otherlist[i],
					Users.work_time_start: work_time_startlist[i], Users.work_time_end: work_time_endlist[i]}, synchronize_session=False)
				session.commit()
				stat[key]['info']['otpusk'] = otpusklist[i]
				stat[key]['info']['bolezn'] = boleznlist[i]
				stat[key]['info']['poezdka'] = poezdkalist[i]
				stat[key]['info']['deni'] = denilist[i]
				stat[key]['info']['workdays'] = workdayslist[i]
				stat[key]['info']['other'] = otherlist[i]
				stat[key]['info']['work_time_start'] = work_time_startlist[i]
				stat[key]['info']['work_time_end'] = work_time_endlist[i]
				i += 1

	with open(settings.STATIC_CACHE_SONYA,'wb') as cahce:
		pickle.dump(stat, cahce)

	return render(request, 'sonya_door/list.html', {'stat':stat, 'date':date})

def detail(request, userid):
	with open(settings.STATIC_CACHE_SONYA, 'rb') as cahce:
		stat = pickle.load(cahce)
	userInfo = stat[str(userid)]
	return render(request, 'sonya_door/userdetail.html', {'userInfo':userInfo})
