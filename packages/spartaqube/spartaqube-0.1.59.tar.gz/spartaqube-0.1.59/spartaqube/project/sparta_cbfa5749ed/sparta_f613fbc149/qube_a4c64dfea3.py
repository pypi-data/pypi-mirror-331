_K='bPublicUser'
_J='notebook_name'
_I='notebook_id'
_H='b_require_password'
_G='notebook_obj'
_F='default_project_path'
_E='bCodeMirror'
_D='menuBar'
_C='res'
_B=None
_A=True
import os,json,getpass,platform
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
from django.http import FileResponse,Http404
from urllib.parse import unquote
import project.sparta_790004e88b.sparta_8f8916340c.qube_98f8a7b1b8 as qube_98f8a7b1b8
from project.sparta_be1421a7f1.sparta_7a45329420.qube_5f17ea78ba import sparta_f7300f1d8e
from project.sparta_be1421a7f1.sparta_8838f480d4 import qube_8ebf92827c as qube_8ebf92827c
from project.sparta_be1421a7f1.sparta_b1716a4f18.qube_4924a18fbd import sparta_b6e768294b
@csrf_exempt
@sparta_f7300f1d8e
@login_required(redirect_field_name='login')
def sparta_ce1f1b0358(request):
	B=request;A=qube_98f8a7b1b8.sparta_5af2b8ff78(B);A[_D]=13;D=qube_98f8a7b1b8.sparta_7fd1b40d41(B.user);A.update(D);A[_E]=_A
	def E(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=_A)
	F=sparta_b6e768294b();C=os.path.join(F,'notebook');E(C);A[_F]=C;return render(B,'dist/project/notebook/notebook.html',A)
@csrf_exempt
def sparta_5cd8bef91c(request,id):
	B=request
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=False
	if C is _B:D=_A
	else:
		E=qube_8ebf92827c.sparta_f48079d93b(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_ce1f1b0358(B)
	A=qube_98f8a7b1b8.sparta_5af2b8ff78(B);A[_D]=12;H=qube_98f8a7b1b8.sparta_7fd1b40d41(B.user);A.update(H);A[_E]=_A;F=E[_G];A[_F]=F.project_path;A[_H]=0 if E[_C]==1 else 1;A[_I]=F.notebook_id;A[_J]=F.name;A[_K]=B.user.is_anonymous;return render(B,'dist/project/notebook/notebookRun.html',A)
@csrf_exempt
@sparta_f7300f1d8e
@login_required(redirect_field_name='login')
def sparta_3a208ec4c8(request,id):
	B=request
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=False
	if C is _B:D=_A
	else:
		E=qube_8ebf92827c.sparta_f48079d93b(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_ce1f1b0358(B)
	A=qube_98f8a7b1b8.sparta_5af2b8ff78(B);A[_D]=12;H=qube_98f8a7b1b8.sparta_7fd1b40d41(B.user);A.update(H);A[_E]=_A;F=E[_G];A[_F]=F.project_path;A[_H]=0 if E[_C]==1 else 1;A[_I]=F.notebook_id;A[_J]=F.name;A[_K]=B.user.is_anonymous;return render(B,'dist/project/notebook/notebookDetached.html',A)