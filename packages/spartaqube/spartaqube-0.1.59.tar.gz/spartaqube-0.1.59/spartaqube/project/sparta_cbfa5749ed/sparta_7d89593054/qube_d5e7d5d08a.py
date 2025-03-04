import os,json,getpass,platform
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
import project.sparta_790004e88b.sparta_8f8916340c.qube_98f8a7b1b8 as qube_98f8a7b1b8
from project.sparta_be1421a7f1.sparta_7a45329420.qube_5f17ea78ba import sparta_f7300f1d8e
from project.sparta_be1421a7f1.sparta_a4f218b878 import qube_8d97fb1ac1 as qube_8d97fb1ac1
from project.sparta_be1421a7f1.sparta_3b268ed3fb import qube_14fead34ba as qube_14fead34ba
def sparta_edb84ad7bc():
	A=platform.system()
	if A=='Windows':return'windows'
	elif A=='Linux':return'linux'
	elif A=='Darwin':return'mac'
	else:return
@csrf_exempt
@sparta_f7300f1d8e
@login_required(redirect_field_name='login')
def sparta_e07fb3f3c7(request):
	E='template';D='developer';B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_98f8a7b1b8.sparta_5af2b8ff78(B);return render(B,'dist/project/homepage/homepage.html',A)
	A=qube_98f8a7b1b8.sparta_5af2b8ff78(B);A['menuBar']=12;F=qube_98f8a7b1b8.sparta_7fd1b40d41(B.user);A.update(F);A['bCodeMirror']=True;G=os.path.dirname(__file__);C=os.path.dirname(os.path.dirname(G));H=os.path.join(C,'static');I=os.path.join(H,'js',D,E,'frontend');A['frontend_path']=I;J=os.path.dirname(C);K=os.path.join(J,'django_app_template',D,E,'backend');A['backend_path']=K;return render(B,'dist/project/developer/developerExamples.html',A)