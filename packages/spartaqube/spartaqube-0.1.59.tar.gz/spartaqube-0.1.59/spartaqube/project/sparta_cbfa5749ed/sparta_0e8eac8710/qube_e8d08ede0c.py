_A='menuBar'
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
from project.sparta_be1421a7f1.sparta_255b291bda import qube_6e4b85c7a0 as qube_6e4b85c7a0
from project.sparta_be1421a7f1.sparta_edec12ad10 import qube_709c91858d as qube_709c91858d
from project.sparta_be1421a7f1.sparta_b1716a4f18.qube_4924a18fbd import sparta_b6e768294b
@csrf_exempt
@sparta_f7300f1d8e
@login_required(redirect_field_name='login')
def sparta_3388311d2c(request):A=request;B=qube_98f8a7b1b8.sparta_5af2b8ff78(A);B[_A]=-1;C=qube_98f8a7b1b8.sparta_7fd1b40d41(A.user);B.update(C);return render(A,'dist/project/homepage/homepage.html',B)
@csrf_exempt
@sparta_f7300f1d8e
@login_required(redirect_field_name='login')
def sparta_0fcc3b43b4(request,kernel_manager_uuid):
	D=kernel_manager_uuid;C=True;B=request;E=False
	if D is None:E=C
	else:
		F=qube_6e4b85c7a0.sparta_c0a62a3b57(B.user,D)
		if F is None:E=C
	if E:return sparta_3388311d2c(B)
	def H(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=C)
	K=sparta_b6e768294b();G=os.path.join(K,'kernel');H(G);I=os.path.join(G,D);H(I);J=os.path.join(I,'main.ipynb')
	if not os.path.exists(J):
		L=qube_709c91858d.sparta_2e94374c19()
		with open(J,'w')as M:M.write(json.dumps(L))
	A=qube_98f8a7b1b8.sparta_5af2b8ff78(B);A['default_project_path']=G;A[_A]=-1;N=qube_98f8a7b1b8.sparta_7fd1b40d41(B.user);A.update(N);A['kernel_name']=F.name;A['kernelManagerUUID']=F.kernel_manager_uuid;A['bCodeMirror']=C;A['bPublicUser']=B.user.is_anonymous;return render(B,'dist/project/sqKernelNotebook/sqKernelNotebook.html',A)