_A='jsonData'
import json,inspect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from project.sparta_be1421a7f1.sparta_94d3976291 import qube_eacf825384 as qube_eacf825384
from project.sparta_be1421a7f1.sparta_7a45329420.qube_5f17ea78ba import sparta_4864a154cb
@csrf_exempt
@sparta_4864a154cb
def sparta_a4a8bfa5cc(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_eacf825384.sparta_a4a8bfa5cc(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_23bcc1e7d6(request):
	C='userObj';B=request;D=json.loads(B.body);E=json.loads(D[_A]);F=B.user;A=qube_eacf825384.sparta_23bcc1e7d6(E,F)
	if A['res']==1:
		if C in list(A.keys()):login(B,A[C]);A.pop(C,None)
	G=json.dumps(A);return HttpResponse(G)
@csrf_exempt
@sparta_4864a154cb
def sparta_8b8211a2c3(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=A.user;E=qube_eacf825384.sparta_8b8211a2c3(C,D);F=json.dumps(E);return HttpResponse(F)
@csrf_exempt
@sparta_4864a154cb
def sparta_05bf22e6b9(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_eacf825384.sparta_05bf22e6b9(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_1f7a8182f5(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_eacf825384.sparta_1f7a8182f5(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_4864a154cb
def sparta_eb61879214(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_eacf825384.sparta_eb61879214(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_88294c728f(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_eacf825384.token_reset_password_worker(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
@sparta_4864a154cb
def sparta_b96d623438(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_eacf825384.network_master_reset_password(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_4f21ecb35f(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_eacf825384.sparta_4f21ecb35f(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
def sparta_b1d8658681(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_eacf825384.sparta_b1d8658681(A,C);E=json.dumps(D);return HttpResponse(E)