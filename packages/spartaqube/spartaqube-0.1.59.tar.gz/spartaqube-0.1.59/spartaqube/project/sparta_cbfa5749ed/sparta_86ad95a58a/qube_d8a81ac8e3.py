from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from project.sparta_be1421a7f1.sparta_7a45329420.qube_5f17ea78ba import sparta_f7300f1d8e
from project.sparta_be1421a7f1.sparta_b4e39938af import qube_d37807507e as qube_d37807507e
from project.models import UserProfile
import project.sparta_790004e88b.sparta_8f8916340c.qube_98f8a7b1b8 as qube_98f8a7b1b8
@sparta_f7300f1d8e
@login_required(redirect_field_name='login')
def sparta_8ed875b178(request):
	E='avatarImg';B=request;A=qube_98f8a7b1b8.sparta_5af2b8ff78(B);A['menuBar']=-1;F=qube_98f8a7b1b8.sparta_7fd1b40d41(B.user);A.update(F);A[E]='';C=UserProfile.objects.filter(user=B.user)
	if C.count()>0:
		D=C[0];G=D.avatar
		if G is not None:H=D.avatar.image64;A[E]=H
	A['bInvertIcon']=0;return render(B,'dist/project/helpCenter/helpCenter.html',A)
@sparta_f7300f1d8e
@login_required(redirect_field_name='login')
def sparta_48dcaf1760(request):
	A=request;B=UserProfile.objects.filter(user=A.user)
	if B.count()>0:C=B[0];C.has_open_tickets=False;C.save()
	return sparta_8ed875b178(A)