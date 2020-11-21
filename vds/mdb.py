from django.conf import settings
import pyodbc


class Mdbconnect:
	def connect(self):
		user = 'admin'
		password = 'BSA'
		odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb)};DBQ=%s;UID=%s;PWD=%s' % (settings.MS_ACCESS_DIR, user, password)
		conn = pyodbc.connect(odbc_conn_str)
		cursor = conn.cursor()
		return cursor
		
	def query(self, cursor, querydb):
		cursor.execute(querydb)
		rest_of_rows = cursor.fetchall()	
		return rest_of_rows
