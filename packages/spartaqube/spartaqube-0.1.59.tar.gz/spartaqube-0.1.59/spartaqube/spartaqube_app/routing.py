import pkg_resources
from channels.routing import ProtocolTypeRouter,URLRouter
from django.urls import re_path as url
from django.conf import settings
from project.sparta_790004e88b.sparta_a668c60626 import qube_3ca2cd7b5d,qube_55a53a037a,qube_40e6bd4019,qube_d1ba79e3d7,qube_1b14c27d9d,qube_31b391e6ea,qube_1d8fc5b8c2,qube_f60074af0f,qube_21c6ceecab
from channels.auth import AuthMiddlewareStack
import channels
channels_ver=pkg_resources.get_distribution('channels').version
channels_major=int(channels_ver.split('.')[0])
def sparta_3cfec091e7(this_class):
	A=this_class
	if channels_major<=2:return A
	else:return A.as_asgi()
urlpatterns=[url('ws/statusWS',sparta_3cfec091e7(qube_3ca2cd7b5d.StatusWS)),url('ws/notebookWS',sparta_3cfec091e7(qube_55a53a037a.NotebookWS)),url('ws/wssConnectorWS',sparta_3cfec091e7(qube_40e6bd4019.WssConnectorWS)),url('ws/pipInstallWS',sparta_3cfec091e7(qube_d1ba79e3d7.PipInstallWS)),url('ws/gitNotebookWS',sparta_3cfec091e7(qube_1b14c27d9d.GitNotebookWS)),url('ws/xtermGitWS',sparta_3cfec091e7(qube_31b391e6ea.XtermGitWS)),url('ws/hotReloadLivePreviewWS',sparta_3cfec091e7(qube_1d8fc5b8c2.HotReloadLivePreviewWS)),url('ws/apiWebserviceWS',sparta_3cfec091e7(qube_f60074af0f.ApiWebserviceWS)),url('ws/apiWebsocketWS',sparta_3cfec091e7(qube_21c6ceecab.ApiWebsocketWS))]
application=ProtocolTypeRouter({'websocket':AuthMiddlewareStack(URLRouter(urlpatterns))})
for thisUrlPattern in urlpatterns:
	try:
		if len(settings.DAPHNE_PREFIX)>0:thisUrlPattern.pattern._regex='^'+settings.DAPHNE_PREFIX+'/'+thisUrlPattern.pattern._regex
	except Exception as e:print(e)