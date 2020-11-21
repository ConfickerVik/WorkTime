from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings
import struct
from door.calculation import Serialize
from django.conf import settings
from vds.mdb import Mdbconnect
import pickle
import datetime


def list(request):
	stat = {}
	date = str(datetime.date.today())[:-3]
	objStat = Serialize()
	stat = objStat.restructuring(date)

	if request.POST:
		
		if request.POST.get('date'):
			date = request.POST.get('date')
			stat = objStat.restructuring(date)
		
	
	with open(settings.STATIC_CACHE_DOOR,'wb') as cahce:
			pickle.dump(stat, cahce)

	return render(request, 'door/list.html', {'stat':stat, 'date':date})


def detail(request, userid):
	with open(settings.STATIC_CACHE_DOOR, 'rb') as cahce:
		stat = pickle.load(cahce)
	userInfo = stat[str(userid)]
	return render(request, 'door/userdetail.html', {'userInfo':userInfo})