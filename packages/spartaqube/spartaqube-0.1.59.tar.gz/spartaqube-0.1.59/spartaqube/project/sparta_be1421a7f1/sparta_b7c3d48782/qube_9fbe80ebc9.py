import os,zipfile,pytz
UTC=pytz.utc
from django.conf import settings as conf_settings
def sparta_d9b4dba7cb():
	B='APPDATA'
	if conf_settings.PLATFORMS_NFS:
		A='/var/nfs/notebooks/'
		if not os.path.exists(A):os.makedirs(A)
		return A
	if conf_settings.PLATFORM=='LOCAL_DESKTOP'or conf_settings.IS_LOCAL_PLATFORM:
		if conf_settings.PLATFORM_DEBUG=='DEBUG-CLIENT-2':return os.path.join(os.environ[B],'SpartaQuantNB/CLIENT2')
		return os.path.join(os.environ[B],'SpartaQuantNB')
	if conf_settings.PLATFORM=='LOCAL_CE':return'/app/notebooks/'
def sparta_81d13f682a(userId):A=sparta_d9b4dba7cb();B=os.path.join(A,userId);return B
def sparta_3c38ab7d4a(notebookProjectId,userId):A=sparta_81d13f682a(userId);B=os.path.join(A,notebookProjectId);return B
def sparta_04da9fbf63(notebookProjectId,userId):A=sparta_81d13f682a(userId);B=os.path.join(A,notebookProjectId);return os.path.exists(B)
def sparta_58b034f490(notebookProjectId,userId,ipynbFileName):A=sparta_81d13f682a(userId);B=os.path.join(A,notebookProjectId);return os.path.isfile(os.path.join(B,ipynbFileName))
def sparta_009d0b7617(notebookProjectId,userId):
	C=userId;B=notebookProjectId;D=sparta_3c38ab7d4a(B,C);G=sparta_81d13f682a(C);A=f"{G}/zipTmp/"
	if not os.path.exists(A):os.makedirs(A)
	H=f"{A}/{B}.zip";E=zipfile.ZipFile(H,'w',zipfile.ZIP_DEFLATED);I=len(D)+1
	for(J,M,K)in os.walk(D):
		for L in K:F=os.path.join(J,L);E.write(F,F[I:])
	return E
def sparta_eb9a2b1861(notebookProjectId,userId):B=userId;A=notebookProjectId;sparta_009d0b7617(A,B);C=f"{A}.zip";D=sparta_81d13f682a(B);E=f"{D}/zipTmp/{A}.zip";F=open(E,'rb');return{'zipName':C,'zipObj':F}