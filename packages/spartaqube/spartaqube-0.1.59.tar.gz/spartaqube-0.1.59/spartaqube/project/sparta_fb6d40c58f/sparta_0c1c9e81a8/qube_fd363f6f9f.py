_C='isAuth'
_B='jsonData'
_A='res'
import json
from django.contrib.auth import logout
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from project.sparta_be1421a7f1.sparta_7a45329420 import qube_5f17ea78ba as qube_5f17ea78ba
from project.sparta_790004e88b.sparta_8f8916340c.qube_98f8a7b1b8 import sparta_9f621cc76e
from project.logger_config import logger
@csrf_exempt
def sparta_f62f89cc1e(request):A=json.loads(request.body);B=json.loads(A[_B]);return qube_5f17ea78ba.sparta_f62f89cc1e(B)
@csrf_exempt
def sparta_8fe7e8be0d(request):logout(request);A={_A:1};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_a260f352a0(request):
	if request.user.is_authenticated:A=1
	else:A=0
	B={_A:1,_C:A};C=json.dumps(B);return HttpResponse(C)
def sparta_dfea80b34e(request):
	B=request;from django.contrib.auth import authenticate as F,login;from django.contrib.auth.models import User as C;G=json.loads(B.body);D=json.loads(G[_B]);H=D['email'];I=D['password'];E=0
	try:
		A=C.objects.get(email=H);A=F(B,username=A.username,password=I)
		if A is not None:login(B,A);E=1
	except C.DoesNotExist:pass
	J={_A:1,_C:E};K=json.dumps(J);return HttpResponse(K)