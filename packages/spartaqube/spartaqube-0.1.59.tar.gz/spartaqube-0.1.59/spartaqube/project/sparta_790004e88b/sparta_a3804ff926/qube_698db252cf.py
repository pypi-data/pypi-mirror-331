import os
from project.sparta_790004e88b.sparta_a3804ff926.qube_35ec1c6de7 import qube_35ec1c6de7
from project.sparta_790004e88b.sparta_a3804ff926.qube_13ffda077b import qube_13ffda077b
from project.sparta_790004e88b.sparta_a3804ff926.qube_6e4d86ef14 import qube_6e4d86ef14
from project.sparta_790004e88b.sparta_a3804ff926.qube_2d9ccf4120 import qube_2d9ccf4120
class db_connection:
	def __init__(A,dbType=0):A.dbType=dbType;A.dbCon=None
	def get_db_type(A):return A.dbType
	def getConnection(A):
		if A.dbType==0:
			from django.conf import settings as B
			if B.PLATFORM in['SANDBOX','SANDBOX_MYSQL']:return
			A.dbCon=qube_35ec1c6de7()
		elif A.dbType==1:A.dbCon=qube_13ffda077b()
		elif A.dbType==2:A.dbCon=qube_6e4d86ef14()
		elif A.dbType==4:A.dbCon=qube_2d9ccf4120()
		return A.dbCon