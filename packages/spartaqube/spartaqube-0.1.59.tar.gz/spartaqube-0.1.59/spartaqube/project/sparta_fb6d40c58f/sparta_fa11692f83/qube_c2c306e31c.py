_I='error.txt'
_H='zipName'
_G='utf-8'
_F='attachment; filename={0}'
_E='appId'
_D='res'
_C='Content-Disposition'
_B='projectPath'
_A='jsonData'
import json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_be1421a7f1.sparta_b7c3d48782 import qube_9aaa3b3165 as qube_9aaa3b3165
from project.sparta_be1421a7f1.sparta_b7c3d48782 import qube_f7466e1a38 as qube_f7466e1a38
from project.sparta_be1421a7f1.sparta_b1716a4f18 import qube_c1fa38f5a2 as qube_c1fa38f5a2
from project.sparta_be1421a7f1.sparta_7a45329420.qube_5f17ea78ba import sparta_4864a154cb
@csrf_exempt
@sparta_4864a154cb
def sparta_6b62edd400(request):
	D='files[]';A=request;E=A.POST.dict();B=A.FILES
	if D in B:C=qube_9aaa3b3165.sparta_af66f1fe22(E,A.user,B[D])
	else:C={_D:1}
	F=json.dumps(C);return HttpResponse(F)
@csrf_exempt
@sparta_4864a154cb
def sparta_ed43285bea(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_9aaa3b3165.sparta_9d74d72017(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_9bed6f953d(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_9aaa3b3165.sparta_0ad0d37530(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_f40408e956(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_9aaa3b3165.sparta_1edad17eca(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_d5ba12fcf4(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_f7466e1a38.sparta_5eefebe754(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_dff1bfe0de(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_9aaa3b3165.sparta_683f7d3288(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_3b31847def(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_9aaa3b3165.sparta_ede92fa8c4(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_3a5df259f3(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_9aaa3b3165.sparta_ac28a39588(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_a0ae9e9b3d(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_9aaa3b3165.sparta_d6396b27ed(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_ae513ef0ad(request):
	F='filePath';E='fileName';A=request;B=A.GET[E];G=A.GET[F];H=A.GET[_B];I=A.GET[_E];J={E:B,F:G,_E:I,_B:base64.b64decode(H).decode(_G)};C=qube_9aaa3b3165.sparta_60a7c7f302(J,A.user)
	if C[_D]==1:
		try:
			with open(C['fullPath'],'rb')as K:D=HttpResponse(K.read(),content_type='application/force-download');D[_C]='attachment; filename='+str(B);return D
		except Exception as L:pass
	raise Http404
@csrf_exempt
@sparta_4864a154cb
def sparta_d366e66f2b(request):
	E='folderName';B=request;F=B.GET[_B];D=B.GET[E];G={_B:base64.b64decode(F).decode(_G),E:D};C=qube_9aaa3b3165.sparta_f4c471b580(G,B.user)
	if C[_D]==1:H=C['zip'];I=C[_H];A=HttpResponse();A.write(H.getvalue());A[_C]=_F.format(f"{I}.zip")
	else:A=HttpResponse();J=f"Could not download the folder {D}, please try again";K=_I;A.write(J);A[_C]=_F.format(K)
	return A
@csrf_exempt
@sparta_4864a154cb
def sparta_e07348542d(request):
	B=request;D=B.GET[_E];E=B.GET[_B];F={_E:D,_B:base64.b64decode(E).decode(_G)};C=qube_9aaa3b3165.sparta_a416df756a(F,B.user)
	if C[_D]==1:G=C['zip'];H=C[_H];A=HttpResponse();A.write(G.getvalue());A[_C]=_F.format(f"{H}.zip")
	else:A=HttpResponse();I='Could not download the application, please try again';J=_I;A.write(I);A[_C]=_F.format(J)
	return A