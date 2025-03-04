_C='bCodeMirror'
_B='menuBar'
_A=True
import os,json,getpass,platform
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import project.sparta_790004e88b.sparta_8f8916340c.qube_98f8a7b1b8 as qube_98f8a7b1b8
from project.sparta_be1421a7f1.sparta_7a45329420.qube_5f17ea78ba import sparta_f7300f1d8e
from project.sparta_be1421a7f1.sparta_a4f218b878 import qube_8d97fb1ac1 as qube_8d97fb1ac1
from project.sparta_be1421a7f1.sparta_3b268ed3fb import qube_14fead34ba as qube_14fead34ba
from project.sparta_be1421a7f1.sparta_b1716a4f18.qube_4924a18fbd import sparta_b6e768294b
@csrf_exempt
@sparta_f7300f1d8e
@login_required(redirect_field_name='login')
def sparta_725d9d5193(request):
	B=request;C=B.GET.get('edit')
	if C is None:C='-1'
	A=qube_98f8a7b1b8.sparta_5af2b8ff78(B);A[_B]=9;E=qube_98f8a7b1b8.sparta_7fd1b40d41(B.user);A.update(E);A[_C]=_A;A['edit_chart_id']=C
	def F(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=_A)
	G=sparta_b6e768294b();D=os.path.join(G,'dashboard');F(D);A['default_project_path']=D;return render(B,'dist/project/dashboard/dashboard.html',A)
@csrf_exempt
def sparta_f4c1f2bb85(request,id):
	A=request
	if id is None:B=A.GET.get('id')
	else:B=id
	return sparta_be0cbd1ce9(A,B)
def sparta_be0cbd1ce9(request,dashboard_id,session='-1'):
	G='res';E=dashboard_id;B=request;C=False
	if E is None:C=_A
	else:
		D=qube_14fead34ba.has_dashboard_access(E,B.user);H=D[G]
		if H==-1:C=_A
	if C:return sparta_725d9d5193(B)
	A=qube_98f8a7b1b8.sparta_5af2b8ff78(B);A[_B]=9;I=qube_98f8a7b1b8.sparta_7fd1b40d41(B.user);A.update(I);A[_C]=_A;F=D['dashboard_obj'];A['b_require_password']=0 if D[G]==1 else 1;A['dashboard_id']=F.dashboard_id;A['dashboard_name']=F.name;A['bPublicUser']=B.user.is_anonymous;A['session']=str(session);return render(B,'dist/project/dashboard/dashboardRun.html',A)