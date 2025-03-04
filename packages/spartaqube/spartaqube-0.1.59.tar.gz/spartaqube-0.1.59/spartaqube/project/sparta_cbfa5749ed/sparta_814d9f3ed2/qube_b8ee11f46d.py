_O='Please send valid data'
_N='dist/project/auth/resetPasswordChange.html'
_M='captcha'
_L='password'
_K='POST'
_J=False
_I='login'
_H='error'
_G='form'
_F='email'
_E='res'
_D='home'
_C='manifest'
_B='errorMsg'
_A=True
import json,hashlib,uuid
from datetime import datetime
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from django.urls import reverse
import project.sparta_790004e88b.sparta_8f8916340c.qube_98f8a7b1b8 as qube_98f8a7b1b8
from project.forms import ConnexionForm,RegistrationTestForm,RegistrationBaseForm,RegistrationForm,ResetPasswordForm,ResetPasswordChangeForm
from project.sparta_be1421a7f1.sparta_7a45329420.qube_5f17ea78ba import sparta_f7300f1d8e
from project.sparta_be1421a7f1.sparta_7a45329420 import qube_5f17ea78ba as qube_5f17ea78ba
from project.sparta_fb6d40c58f.sparta_0c1c9e81a8 import qube_fd363f6f9f as qube_fd363f6f9f
from project.models import LoginLocation,UserProfile
from project.logger_config import logger
def sparta_f779af4335():return{'bHasCompanyEE':-1}
def sparta_7c7875e2b8(request):B=request;A=qube_98f8a7b1b8.sparta_5af2b8ff78(B);A[_C]=qube_98f8a7b1b8.sparta_8f6b5cba8d();A['forbiddenEmail']=conf_settings.FORBIDDEN_EMAIL;return render(B,'dist/project/auth/banned.html',A)
@sparta_f7300f1d8e
def sparta_067257b0ef(request):
	C=request;B='/';A=C.GET.get(_I)
	if A is not None:D=A.split(B);A=B.join(D[1:]);A=A.replace(B,'$@$')
	return sparta_b9d720dd42(C,A)
def sparta_5fa950721b(request,redirectUrl):return sparta_b9d720dd42(request,redirectUrl)
def sparta_b9d720dd42(request,redirectUrl):
	E=redirectUrl;A=request;logger.debug('Welcome to loginRedirectFunc')
	if A.user.is_authenticated:return redirect(_D)
	G=_J;H='Email or password incorrect'
	if A.method==_K:
		C=ConnexionForm(A.POST)
		if C.is_valid():
			I=C.cleaned_data[_F];J=C.cleaned_data[_L];F=authenticate(username=I,password=J)
			if F:
				if qube_5f17ea78ba.sparta_b26e5d5579(F):return sparta_7c7875e2b8(A)
				login(A,F);K,L=qube_98f8a7b1b8.sparta_6d031f0c7c();LoginLocation.objects.create(user=F,hostname=K,ip=L,date_login=datetime.now())
				if E is not None:
					D=E.split('$@$');D=[A for A in D if len(A)>0]
					if len(D)>1:M=D[0];return redirect(reverse(M,args=D[1:]))
					return redirect(E)
				return redirect(_D)
			else:G=_A
		else:G=_A
	C=ConnexionForm();B=qube_98f8a7b1b8.sparta_5af2b8ff78(A);B.update(qube_98f8a7b1b8.sparta_a201da5787(A));B[_C]=qube_98f8a7b1b8.sparta_8f6b5cba8d();B[_G]=C;B[_H]=G;B['redirectUrl']=E;B[_B]=H;B.update(sparta_f779af4335());return render(A,'dist/project/auth/login.html',B)
def sparta_add03183af(request):
	B='public@spartaqube.com';A=User.objects.filter(email=B).all()
	if A.count()>0:C=A[0];login(request,C)
	return redirect(_D)
@sparta_f7300f1d8e
def sparta_37f76bbd89(request):
	A=request
	if A.user.is_authenticated:return redirect(_D)
	E='';D=_J;F=qube_5f17ea78ba.sparta_44c6db61db()
	if A.method==_K:
		if F:B=RegistrationForm(A.POST)
		else:B=RegistrationBaseForm(A.POST)
		if B.is_valid():
			I=B.cleaned_data;H=None
			if F:
				H=B.cleaned_data['code']
				if not qube_5f17ea78ba.sparta_350e974b2f(H):D=_A;E='Wrong guest code'
			if not D:
				J=A.META['HTTP_HOST'];G=qube_5f17ea78ba.sparta_f62f89cc1e(I,J)
				if int(G[_E])==1:K=G['userObj'];login(A,K);return redirect(_D)
				else:D=_A;E=G[_B]
		else:D=_A;E=B.errors.as_data()
	if F:B=RegistrationForm()
	else:B=RegistrationBaseForm()
	C=qube_98f8a7b1b8.sparta_5af2b8ff78(A);C.update(qube_98f8a7b1b8.sparta_a201da5787(A));C[_C]=qube_98f8a7b1b8.sparta_8f6b5cba8d();C[_G]=B;C[_H]=D;C[_B]=E;C.update(sparta_f779af4335());return render(A,'dist/project/auth/registration.html',C)
def sparta_878bd137fb(request):A=request;B=qube_98f8a7b1b8.sparta_5af2b8ff78(A);B[_C]=qube_98f8a7b1b8.sparta_8f6b5cba8d();return render(A,'dist/project/auth/registrationPending.html',B)
def sparta_65eea074f4(request,token):
	A=request;B=qube_5f17ea78ba.sparta_1f60468cfc(token)
	if int(B[_E])==1:C=B['user'];login(A,C);return redirect(_D)
	D=qube_98f8a7b1b8.sparta_5af2b8ff78(A);D[_C]=qube_98f8a7b1b8.sparta_8f6b5cba8d();return redirect(_I)
def sparta_2f752b45ba(request):logout(request);return redirect(_I)
def sparta_db34a90ce1(request):
	A=request
	if A.user.is_authenticated:
		if A.user.email=='cypress_tests@gmail.com':A.user.delete()
	logout(A);return redirect(_I)
def sparta_79544464e1(request):A={_E:-100,_B:'You are not logged...'};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_88061f4dca(request):
	A=request;E='';F=_J
	if A.method==_K:
		B=ResetPasswordForm(A.POST)
		if B.is_valid():
			H=B.cleaned_data[_F];I=B.cleaned_data[_M];G=qube_5f17ea78ba.sparta_88061f4dca(H.lower(),I)
			try:
				if int(G[_E])==1:C=qube_98f8a7b1b8.sparta_5af2b8ff78(A);C.update(qube_98f8a7b1b8.sparta_a201da5787(A));B=ResetPasswordChangeForm(A.POST);C[_C]=qube_98f8a7b1b8.sparta_8f6b5cba8d();C[_G]=B;C[_F]=H;C[_H]=F;C[_B]=E;return render(A,_N,C)
				elif int(G[_E])==-1:E=G[_B];F=_A
			except Exception as J:logger.debug('exception ');logger.debug(J);E='Could not send reset email, please try again';F=_A
		else:E=_O;F=_A
	else:B=ResetPasswordForm()
	D=qube_98f8a7b1b8.sparta_5af2b8ff78(A);D.update(qube_98f8a7b1b8.sparta_a201da5787(A));D[_C]=qube_98f8a7b1b8.sparta_8f6b5cba8d();D[_G]=B;D[_H]=F;D[_B]=E;D.update(sparta_f779af4335());return render(A,'dist/project/auth/resetPassword.html',D)
@csrf_exempt
def sparta_c042753f4f(request):
	D=request;E='';B=_J
	if D.method==_K:
		C=ResetPasswordChangeForm(D.POST)
		if C.is_valid():
			I=C.cleaned_data['token'];F=C.cleaned_data[_L];J=C.cleaned_data['password_confirmation'];K=C.cleaned_data[_M];G=C.cleaned_data[_F].lower()
			if len(F)<6:E='Your password must be at least 6 characters';B=_A
			if F!=J:E='The two passwords must be identical...';B=_A
			if not B:
				H=qube_5f17ea78ba.sparta_c042753f4f(K,I,G.lower(),F)
				try:
					if int(H[_E])==1:L=User.objects.get(username=G);login(D,L);return redirect(_D)
					else:E=H[_B];B=_A
				except Exception as M:E='Could not change your password, please try again';B=_A
		else:E=_O;B=_A
	else:return redirect('reset-password')
	A=qube_98f8a7b1b8.sparta_5af2b8ff78(D);A.update(qube_98f8a7b1b8.sparta_a201da5787(D));A[_C]=qube_98f8a7b1b8.sparta_8f6b5cba8d();A[_G]=C;A[_H]=B;A[_B]=E;A[_F]=G;A.update(sparta_f779af4335());return render(D,_N,A)