_L='bPublicUser'
_K='developer_name'
_J='developer_id'
_I='b_require_password'
_H='developer_obj'
_G='default_project_path'
_F='bCodeMirror'
_E='menuBar'
_D='dist/project/homepage/homepage.html'
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
from django.conf import settings as conf_settings
import project.sparta_790004e88b.sparta_8f8916340c.qube_98f8a7b1b8 as qube_98f8a7b1b8
from project.sparta_be1421a7f1.sparta_7a45329420.qube_5f17ea78ba import sparta_f7300f1d8e
from project.sparta_be1421a7f1.sparta_bbfe0fe21c import qube_5c3380afe6 as qube_5c3380afe6
from project.sparta_be1421a7f1.sparta_b1716a4f18.qube_4924a18fbd import sparta_b6e768294b
@csrf_exempt
@sparta_f7300f1d8e
@login_required(redirect_field_name='login')
def sparta_15ea2e05b0(request):
	B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_98f8a7b1b8.sparta_5af2b8ff78(B);return render(B,_D,A)
	qube_5c3380afe6.sparta_fe49f95725();A=qube_98f8a7b1b8.sparta_5af2b8ff78(B);A[_E]=12;D=qube_98f8a7b1b8.sparta_7fd1b40d41(B.user);A.update(D);A[_F]=_A
	def E(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=_A)
	F=sparta_b6e768294b();C=os.path.join(F,'developer');E(C);A[_G]=C;return render(B,'dist/project/developer/developer.html',A)
@csrf_exempt
def sparta_2dec13a010(request,id):
	B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_98f8a7b1b8.sparta_5af2b8ff78(B);return render(B,_D,A)
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=False
	if C is _B:D=_A
	else:
		E=qube_5c3380afe6.has_developer_access(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_15ea2e05b0(B)
	A=qube_98f8a7b1b8.sparta_5af2b8ff78(B);A[_E]=12;H=qube_98f8a7b1b8.sparta_7fd1b40d41(B.user);A.update(H);A[_F]=_A;F=E[_H];A[_G]=F.project_path;A[_I]=0 if E[_C]==1 else 1;A[_J]=F.developer_id;A[_K]=F.name;A[_L]=B.user.is_anonymous;return render(B,'dist/project/developer/developerRun.html',A)
@csrf_exempt
@sparta_f7300f1d8e
@login_required(redirect_field_name='login')
def sparta_a89d38649f(request,id):
	B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_98f8a7b1b8.sparta_5af2b8ff78(B);return render(B,_D,A)
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=False
	if C is _B:D=_A
	else:
		E=qube_5c3380afe6.has_developer_access(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_15ea2e05b0(B)
	A=qube_98f8a7b1b8.sparta_5af2b8ff78(B);A[_E]=12;H=qube_98f8a7b1b8.sparta_7fd1b40d41(B.user);A.update(H);A[_F]=_A;F=E[_H];A[_G]=F.project_path;A[_I]=0 if E[_C]==1 else 1;A[_J]=F.developer_id;A[_K]=F.name;A[_L]=B.user.is_anonymous;return render(B,'dist/project/developer/developerDetached.html',A)
def sparta_94d9744f1c(request,project_path,file_name):A=project_path;A=unquote(A);return serve(request,file_name,document_root=A)