_A='jsonData'
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from project.models import UserProfile
from project.sparta_be1421a7f1.sparta_67665e9cde import qube_18e0b5e667 as qube_18e0b5e667
from project.sparta_be1421a7f1.sparta_b4e39938af import qube_d37807507e as qube_d37807507e
from project.sparta_be1421a7f1.sparta_7a45329420.qube_5f17ea78ba import sparta_4864a154cb
@csrf_exempt
@sparta_4864a154cb
def sparta_f6e54f495c(request):
	B=request;I=json.loads(B.body);C=json.loads(I[_A]);A=B.user;D=0;E=UserProfile.objects.filter(user=A)
	if E.count()>0:
		F=E[0]
		if F.has_open_tickets:
			C['userId']=F.user_profile_id;G=qube_d37807507e.sparta_2e04d6bf20(A)
			if G['res']==1:D=int(G['nbNotifications'])
	H=qube_18e0b5e667.sparta_f6e54f495c(C,A);H['nbNotificationsHelpCenter']=D;J=json.dumps(H);return HttpResponse(J)
@csrf_exempt
@sparta_4864a154cb
def sparta_68b59305e1(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_18e0b5e667.sparta_a431af7059(C,A.user);E=json.dumps(D);return HttpResponse(E)