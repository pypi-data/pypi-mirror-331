from urllib.parse import urlparse,urlunparse
from django.contrib.auth.decorators import login_required
from django.conf import settings as conf_settings
from django.shortcuts import render
import project.sparta_790004e88b.sparta_8f8916340c.qube_98f8a7b1b8 as qube_98f8a7b1b8
from project.models import UserProfile
from project.sparta_be1421a7f1.sparta_7a45329420.qube_5f17ea78ba import sparta_f7300f1d8e
from project.sparta_cbfa5749ed.sparta_814d9f3ed2.qube_b8ee11f46d import sparta_f779af4335
@sparta_f7300f1d8e
@login_required(redirect_field_name='login')
def sparta_eff2efcb39(request,idSection=1):
	B=request;D=UserProfile.objects.get(user=B.user);E=D.avatar
	if E is not None:E=D.avatar.avatar
	C=urlparse(conf_settings.URL_TERMS)
	if not C.scheme:C=urlunparse(C._replace(scheme='http'))
	F={'item':1,'idSection':idSection,'userProfil':D,'avatar':E,'url_terms':C};A=qube_98f8a7b1b8.sparta_5af2b8ff78(B);A.update(qube_98f8a7b1b8.sparta_7fd1b40d41(B.user));A.update(F);G='';A['accessKey']=G;A['menuBar']=4;A.update(sparta_f779af4335());return render(B,'dist/project/auth/settings.html',A)