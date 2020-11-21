import pymysql
from django.conf import settings


class MySQLDBConnect:
	def connect(self):
		connection = pymysql.connect(host=settings.DATABASES['default']['HOST'],
			user=settings.DATABASES['default']['USER'],
			password=settings.DATABASES['default']['PASSWORD'],
			db=settings.DATABASES['default']['NAME'],
			cursorclass=pymysql.cursors.DictCursor)
		cursor = connection.cursor()
		return cursor

	def query(self, cursor, querydb):
		cursor.execute(querydb)
		resQuary = cursor.fetchall()
		return resQuary
