_E='Content-Disposition'
_D='utf-8'
_C='dashboardId'
_B='projectPath'
_A='jsonData'
import os,json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_be1421a7f1.sparta_edec12ad10 import qube_3817fce956 as qube_3817fce956
from project.sparta_be1421a7f1.sparta_edec12ad10 import qube_0fe3b9c585 as qube_0fe3b9c585
from project.sparta_be1421a7f1.sparta_3b268ed3fb import qube_14fead34ba as qube_14fead34ba
from project.sparta_be1421a7f1.sparta_7a45329420.qube_5f17ea78ba import sparta_4864a154cb,sparta_1e978b38e4
@csrf_exempt
def sparta_06b2d9601a(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_3817fce956.sparta_06b2d9601a(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_06d3fa0c88(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_3817fce956.sparta_06d3fa0c88(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_3713bf01c9(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_3817fce956.sparta_3713bf01c9(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_68ff1dd5f3(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_3817fce956.sparta_68ff1dd5f3(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
@sparta_1e978b38e4
def sparta_312ca9e1d2(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_3817fce956.sparta_312ca9e1d2(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_198e44c8f3(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_3817fce956.sparta_198e44c8f3(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_94a196979d(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_3817fce956.sparta_94a196979d(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_7f7895d30d(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_3817fce956.sparta_7f7895d30d(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_8f8dd7eefd(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_3817fce956.sparta_8f8dd7eefd(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_703fa91f21(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_3817fce956.sparta_703fa91f21(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_0c63fd9362(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_3817fce956.dashboard_project_explorer_delete_multiple_resources(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_07f0bfc6dc(request):A=request;B=A.POST.dict();C=A.FILES;D=qube_3817fce956.sparta_07f0bfc6dc(B,A.user,C['files[]']);E=json.dumps(D);return HttpResponse(E)
def sparta_3fdbda8614(path):
	A=path;A=os.path.normpath(A)
	if os.path.isfile(A):A=os.path.dirname(A)
	return os.path.basename(A)
def sparta_7b1cafe4e8(path):A=path;A=os.path.normpath(A);return os.path.basename(A)
@csrf_exempt
@sparta_4864a154cb
def sparta_bbc453756b(request):
	E='pathResource';A=request;B=A.GET[E];B=base64.b64decode(B).decode(_D);F=A.GET[_B];G=A.GET[_C];H=sparta_7b1cafe4e8(B);I={E:B,_C:G,_B:base64.b64decode(F).decode(_D)};C=qube_3817fce956.sparta_60a7c7f302(I,A.user)
	if C['res']==1:
		try:
			with open(C['fullPath'],'rb')as J:D=HttpResponse(J.read(),content_type='application/force-download');D[_E]='attachment; filename='+str(H);return D
		except Exception as K:pass
	raise Http404
@csrf_exempt
@sparta_4864a154cb
def sparta_33e733201f(request):
	D='attachment; filename={0}';B=request;E=B.GET[_C];F=B.GET[_B];G={_C:E,_B:base64.b64decode(F).decode(_D)};C=qube_3817fce956.sparta_a416df756a(G,B.user)
	if C['res']==1:H=C['zip'];I=C['zipName'];A=HttpResponse();A.write(H.getvalue());A[_E]=D.format(f"{I}.zip")
	else:A=HttpResponse();J='Could not download the application, please try again';K='error.txt';A.write(J);A[_E]=D.format(K)
	return A
@csrf_exempt
@sparta_4864a154cb
@sparta_1e978b38e4
def sparta_78c64e697d(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_0fe3b9c585.sparta_78c64e697d(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
@sparta_1e978b38e4
def sparta_c8f86445e5(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_0fe3b9c585.sparta_c8f86445e5(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
@sparta_1e978b38e4
def sparta_59923e603b(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_0fe3b9c585.sparta_59923e603b(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
@sparta_1e978b38e4
def sparta_7ea3aca46e(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_0fe3b9c585.sparta_7ea3aca46e(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
@sparta_1e978b38e4
def sparta_316eeef41c(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_0fe3b9c585.sparta_316eeef41c(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
@sparta_1e978b38e4
def sparta_046dd0b39a(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_0fe3b9c585.sparta_046dd0b39a(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
@sparta_1e978b38e4
def sparta_93a94517d0(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_0fe3b9c585.sparta_93a94517d0(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
@sparta_1e978b38e4
def sparta_bb111753a7(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_0fe3b9c585.sparta_bb111753a7(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
@sparta_1e978b38e4
def sparta_56d6df1fd7(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_0fe3b9c585.sparta_56d6df1fd7(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
@sparta_1e978b38e4
def sparta_d9fc851ec5(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_0fe3b9c585.sparta_d9fc851ec5(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
@sparta_1e978b38e4
def sparta_64114bfa97(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_0fe3b9c585.sparta_64114bfa97(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
@sparta_1e978b38e4
def sparta_4c533ac1db(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_0fe3b9c585.sparta_4c533ac1db(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
@sparta_1e978b38e4
def sparta_a8390918d8(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_0fe3b9c585.sparta_a8390918d8(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
@sparta_1e978b38e4
def sparta_3999a9e9a3(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_0fe3b9c585.sparta_3999a9e9a3(C,A.user);E=json.dumps(D);return HttpResponse(E)