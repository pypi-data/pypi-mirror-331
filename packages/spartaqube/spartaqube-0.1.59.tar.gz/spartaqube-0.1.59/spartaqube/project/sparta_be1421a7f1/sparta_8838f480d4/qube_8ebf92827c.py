_t='stdout'
_s='makemigrations'
_r='app.settings'
_q='DJANGO_SETTINGS_MODULE'
_p='python'
_o='thumbnail'
_n='static'
_m='project'
_l='previewImage'
_k='isExecCodeDisplay'
_j='isPublic'
_i='isExpose'
_h='password'
_g='lumino_layout'
_f='notebook_venv'
_e='lumino'
_d='Project not found...'
_c='You do not have the rights to access this project'
_b='models_access_examples.py'
_a='notebook_models.py'
_Z='template'
_Y='django_app_template'
_X='luminoLayout'
_W='hasPassword'
_V='is_exec_code_display'
_U='is_public_notebook'
_T='main_ipynb_fullpath'
_S='has_password'
_R='is_expose_notebook'
_Q='description'
_P='slug'
_O='app'
_N='manage.py'
_M='notebook_id'
_L='project_path'
_K='notebook'
_J='notebook_obj'
_I='notebookId'
_H='name'
_G='main.ipynb'
_F='projectPath'
_E='errorMsg'
_D=None
_C=False
_B='res'
_A=True
import re,os,json,stat,importlib,io,sys,subprocess,platform,base64,traceback,uuid,shutil
from django.db.models import Q
from django.utils.text import slugify
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from spartaqube_app.path_mapper_obf import sparta_f2edee430b
from project.models_spartaqube import Notebook,NotebookShared
from project.models import ShareRights
from project.sparta_be1421a7f1.sparta_304a8c1998 import qube_5ee3b67146 as qube_5ee3b67146
from project.sparta_be1421a7f1.sparta_a4f218b878 import qube_6fc03565c8 as qube_6fc03565c8
from project.sparta_be1421a7f1.sparta_409f708b0e.qube_9e7a43612a import Connector as Connector
from project.sparta_be1421a7f1.sparta_de33be2a3b import qube_c9cc1e53e8 as qube_c9cc1e53e8
from project.sparta_be1421a7f1.sparta_b1716a4f18.qube_c1fa38f5a2 import sparta_5a61c7b346
from project.sparta_be1421a7f1.sparta_edec12ad10 import qube_709c91858d as qube_709c91858d
from project.sparta_be1421a7f1.sparta_edec12ad10 import qube_c29899fd55 as qube_c29899fd55
from project.sparta_be1421a7f1.sparta_7b7b903db7.qube_ba01e1927d import sparta_b903d211e1
from project.sparta_be1421a7f1.sparta_b1716a4f18.qube_19bdab45c6 import sparta_ee7bb73842,sparta_2d82bd9c5a
from project.logger_config import logger
def sparta_faaa42601a(user_obj):
	A=qube_5ee3b67146.sparta_059217c600(user_obj)
	if len(A)>0:B=[A.user_group for A in A]
	else:B=[]
	return B
def sparta_b63c8bbff7(project_path,has_django_models=_A):
	C=has_django_models;B=project_path
	if not os.path.exists(B):os.makedirs(B)
	G=B;D=os.path.join(sparta_f2edee430b()[_Y],_K,_Z)
	for E in os.listdir(D):
		A=os.path.join(D,E);F=os.path.join(G,E)
		if os.path.isdir(A):
			H=os.path.basename(A)
			if H==_O:
				if not C:continue
			shutil.copytree(A,F,dirs_exist_ok=_A)
		else:
			I=os.path.basename(A)
			if I in[_a,_b]:
				if not C:continue
			shutil.copy2(A,F)
	return{_L:B}
def sparta_d818cf83c8(json_data,user_obj):
	F=json_data;B=user_obj;A=F[_F];A=sparta_5a61c7b346(A);G=Notebook.objects.filter(project_path=A).all()
	if G.count()>0:
		C=G[0];H=sparta_faaa42601a(B)
		if len(H)>0:D=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=H,notebook__is_delete=0,notebook=C)|Q(is_delete=0,user=B,notebook__is_delete=0,notebook=C))
		else:D=NotebookShared.objects.filter(is_delete=0,user=B,notebook__is_delete=0,notebook=C)
		I=_C
		if D.count()>0:
			K=D[0];J=K.share_rights
			if J.is_admin or J.has_write_rights:I=_A
		if not I:return{_B:-1,_E:'Chose another path. A project already exists at this location'}
	if not isinstance(A,str):return{_B:-1,_E:'Project path must be a string.'}
	logger.debug(_L);logger.debug(A)
	try:A=os.path.abspath(A)
	except Exception as E:return{_B:-1,_E:f"Invalid project path: {str(E)}"}
	try:
		if not os.path.exists(A):os.makedirs(A)
		L=F['hasDjangoModels'];M=sparta_b63c8bbff7(A,L);A=M[_L];return{_B:1,_L:A}
	except Exception as E:return{_B:-1,_E:f"Failed to create folder: {str(E)}"}
def sparta_e431ebb302(json_data,user_obj):A=json_data;A['bAddGitignore']=_A;A['bAddReadme']=_A;return qube_c29899fd55.sparta_767507b50b(A,user_obj)
def sparta_1d5bd0380c(json_data,user_obj):
	L='%Y-%m-%d';K='Recently used';E=user_obj;G=sparta_faaa42601a(E)
	if len(G)>0:A=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=G,notebook__is_delete=0)|Q(is_delete=0,user=E,notebook__is_delete=0)|Q(is_delete=0,notebook__is_delete=0,notebook__is_expose_notebook=_A,notebook__is_public_notebook=_A))
	else:A=NotebookShared.objects.filter(Q(is_delete=0,user=E,notebook__is_delete=0)|Q(is_delete=0,notebook__is_delete=0,notebook__is_expose_notebook=_A,notebook__is_public_notebook=_A))
	if A.count()>0:
		C=json_data.get('orderBy',K)
		if C==K:A=A.order_by('-notebook__last_date_used')
		elif C=='Date desc':A=A.order_by('-notebook__last_update')
		elif C=='Date asc':A=A.order_by('notebook__last_update')
		elif C=='Name desc':A=A.order_by('-notebook__name')
		elif C=='Name asc':A=A.order_by('notebook__name')
	H=[]
	for F in A:
		B=F.notebook;M=F.share_rights;I=_D
		try:I=str(B.last_update.strftime(L))
		except:pass
		J=_D
		try:J=str(B.date_created.strftime(L))
		except Exception as N:logger.debug(N)
		D=B.main_ipynb_fullpath
		if D is _D:D=os.path.join(B.project_path,_G)
		elif len(D)==0:D=os.path.join(B.project_path,_G)
		H.append({_M:B.notebook_id,_H:B.name,_P:B.slug,_Q:B.description,_R:B.is_expose_notebook,_S:B.has_password,_T:D,_U:B.is_public_notebook,_V:B.is_exec_code_display,'is_owner':F.is_owner,'has_write_rights':M.has_write_rights,'last_update':I,'date_created':J})
	return{_B:1,'notebook_library':H}
def sparta_766613d03a(json_data,user_obj):
	C=user_obj;F=json_data[_I];E=Notebook.objects.filter(notebook_id__startswith=F,is_delete=_C).all()
	if E.count()==1:
		A=E[E.count()-1];F=A.notebook_id;G=sparta_faaa42601a(C)
		if len(G)>0:D=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=G,notebook__is_delete=0,notebook=A)|Q(is_delete=0,user=C,notebook__is_delete=0,notebook=A))
		else:D=NotebookShared.objects.filter(is_delete=0,user=C,notebook__is_delete=0,notebook=A)
		if D.count()==0:return{_B:-1,_E:_c}
	else:return{_B:-1,_E:_d}
	D=NotebookShared.objects.filter(is_owner=_A,notebook=A,user=C)
	if D.count()>0:H=datetime.now().astimezone(UTC);A.last_date_used=H;A.save()
	B=A.main_ipynb_fullpath
	if B is _D:B=os.path.join(A.project_path,_G)
	elif len(B)==0:B=os.path.join(A.project_path,_G)
	return{_B:1,_K:{'basic':{_M:A.notebook_id,_H:A.name,_P:A.slug,_Q:A.description,_R:A.is_expose_notebook,_U:A.is_public_notebook,_V:A.is_exec_code_display,_T:B,_S:A.has_password,_f:A.notebook_venv,_L:A.project_path},_e:{_g:A.lumino_layout}}}
def sparta_668fdfb223(json_data,user_obj):
	H=json_data;B=user_obj;E=H[_I];logger.debug('load_notebook DEBUG');logger.debug(E)
	if not B.is_anonymous:
		G=Notebook.objects.filter(notebook_id__startswith=E,is_delete=_C).all()
		if G.count()==1:
			A=G[G.count()-1];E=A.notebook_id;I=sparta_faaa42601a(B)
			if len(I)>0:F=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=I,notebook__is_delete=0,notebook=A)|Q(is_delete=0,user=B,notebook__is_delete=0,notebook=A)|Q(is_delete=0,notebook__is_delete=0,notebook__is_expose_notebook=_A,notebook__is_public_notebook=_A))
			else:F=NotebookShared.objects.filter(Q(is_delete=0,user=B,notebook__is_delete=0,notebook=A)|Q(is_delete=0,notebook__is_delete=0,notebook__is_expose_notebook=_A,notebook__is_public_notebook=_A))
			if F.count()==0:return{_B:-1,_E:_c}
		else:return{_B:-1,_E:_d}
	else:
		J=H.get('modalPassword',_D);logger.debug(f"DEBUG DEVELOPER VIEW TEST >>> {J}");C=sparta_f48079d93b(E,B,password_notebook=J);logger.debug('MODAL DEBUG DEBUG DEBUG notebook_access_dict');logger.debug(C)
		if C[_B]!=1:return{_B:C[_B],_E:C[_E]}
		A=C[_J]
	if not B.is_anonymous:
		F=NotebookShared.objects.filter(is_owner=_A,notebook=A,user=B)
		if F.count()>0:K=datetime.now().astimezone(UTC);A.last_date_used=K;A.save()
	D=A.main_ipynb_fullpath
	if D is _D:D=os.path.join(A.project_path,_G)
	elif len(D)==0:D=os.path.join(A.project_path,_G)
	return{_B:1,_K:{'basic':{_M:A.notebook_id,_H:A.name,_P:A.slug,_Q:A.description,_R:A.is_expose_notebook,_U:A.is_public_notebook,_V:A.is_exec_code_display,_S:A.has_password,_f:A.notebook_venv,_L:A.project_path,_T:D},_e:{_g:A.lumino_layout}}}
def sparta_68b4c1c69b(json_data,user_obj):
	I=user_obj;A=json_data;logger.debug('Save notebook');logger.debug(A);logger.debug(A.keys());N=A['isNew']
	if not N:return sparta_e55db3496a(A,I)
	C=datetime.now().astimezone(UTC);J=str(uuid.uuid4());G=A[_W];E=_D
	if G:E=A[_h];E=qube_6fc03565c8.sparta_35c4f19f42(E)
	O=A[_X];P=A[_H];Q=A[_Q];D=A[_F];D=sparta_5a61c7b346(D);R=A[_i];S=A[_j];G=A[_W];T=A[_k];U=A.get('notebookVenv',_D);B=A[_P]
	if len(B)==0:B=A[_H]
	K=slugify(B);B=K;L=1
	while Notebook.objects.filter(slug=B).exists():B=f"{K}-{L}";L+=1
	H=_D;F=A.get(_l,_D)
	if F is not _D:
		try:
			F=F.split(',')[1];V=base64.b64decode(F);D=sparta_f2edee430b()[_m];M=os.path.join(D,_n,_o,_K);os.makedirs(M,exist_ok=_A);H=str(uuid.uuid4());W=os.path.join(M,f"{H}.png")
			with open(W,'wb')as X:X.write(V)
		except:pass
	Y=Notebook.objects.create(notebook_id=J,name=P,slug=B,description=Q,is_expose_notebook=R,is_public_notebook=S,has_password=G,password_e=E,is_exec_code_display=T,lumino_layout=O,project_path=D,notebook_venv=U,thumbnail_path=H,date_created=C,last_update=C,last_date_used=C,spartaqube_version=sparta_b903d211e1());Z=ShareRights.objects.create(is_admin=_A,has_write_rights=_A,has_reshare_rights=_A,last_update=C);NotebookShared.objects.create(notebook=Y,user=I,share_rights=Z,is_owner=_A,date_created=C);return{_B:1,_M:J}
def sparta_e55db3496a(json_data,user_obj):
	G=user_obj;B=json_data;logger.debug('Save notebook update_notebook_view');logger.debug(B);logger.debug(B.keys());L=datetime.now().astimezone(UTC);H=B[_I];I=Notebook.objects.filter(notebook_id__startswith=H,is_delete=_C).all()
	if I.count()==1:
		A=I[I.count()-1];H=A.notebook_id;M=sparta_faaa42601a(G)
		if len(M)>0:J=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=M,notebook__is_delete=0,notebook=A)|Q(is_delete=0,user=G,notebook__is_delete=0,notebook=A))
		else:J=NotebookShared.objects.filter(is_delete=0,user=G,notebook__is_delete=0,notebook=A)
		N=_C
		if J.count()>0:
			T=J[0];O=T.share_rights
			if O.is_admin or O.has_write_rights:N=_A
		if N:
			K=B[_X];U=B[_H];V=B[_Q];W=B[_i];X=B[_j];Y=B[_W];Z=B[_k];C=B[_P]
			if A.slug!=C:
				if len(C)==0:C=B[_H]
				P=slugify(C);C=P;R=1
				while Notebook.objects.filter(slug=C).exists():C=f"{P}-{R}";R+=1
			D=_D;E=B.get(_l,_D)
			if E is not _D:
				E=E.split(',')[1];a=base64.b64decode(E)
				try:
					b=sparta_f2edee430b()[_m];S=os.path.join(b,_n,_o,_K);os.makedirs(S,exist_ok=_A)
					if A.thumbnail_path is _D:D=str(uuid.uuid4())
					else:D=A.thumbnail_path
					c=os.path.join(S,f"{D}.png")
					with open(c,'wb')as d:d.write(a)
				except:pass
			logger.debug('lumino_layout_dump');logger.debug(K);logger.debug(type(K));A.name=U;A.description=V;A.slug=C;A.is_expose_notebook=W;A.is_public_notebook=X;A.is_exec_code_display=Z;A.thumbnail_path=D;A.lumino_layout=K;A.last_update=L;A.last_date_used=L
			if Y:
				F=B[_h]
				if len(F)>0:F=qube_6fc03565c8.sparta_35c4f19f42(F);A.password_e=F;A.has_password=_A
			else:A.has_password=_C
			A.save()
	return{_B:1,_M:H}
def sparta_30c14c7274(json_data,user_obj):
	E=json_data;B=user_obj;F=E[_I];C=Notebook.objects.filter(notebook_id__startswith=F,is_delete=_C).all()
	if C.count()==1:
		A=C[C.count()-1];F=A.notebook_id;G=sparta_faaa42601a(B)
		if len(G)>0:D=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=G,notebook__is_delete=0,notebook=A)|Q(is_delete=0,user=B,notebook__is_delete=0,notebook=A))
		else:D=NotebookShared.objects.filter(is_delete=0,user=B,notebook__is_delete=0,notebook=A)
		H=_C
		if D.count()>0:
			J=D[0];I=J.share_rights
			if I.is_admin or I.has_write_rights:H=_A
		if H:K=E[_X];A.lumino_layout=K;A.save()
	return{_B:1}
def sparta_45de85f977(json_data,user_obj):
	A=user_obj;G=json_data[_I];B=Notebook.objects.filter(notebook_id=G,is_delete=_C).all()
	if B.count()>0:
		C=B[B.count()-1];E=sparta_faaa42601a(A)
		if len(E)>0:D=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=E,notebook__is_delete=0,notebook=C)|Q(is_delete=0,user=A,notebook__is_delete=0,notebook=C))
		else:D=NotebookShared.objects.filter(is_delete=0,user=A,notebook__is_delete=0,notebook=C)
		if D.count()>0:F=D[0];F.is_delete=_A;F.save()
	return{_B:1}
def sparta_f48079d93b(notebook_id,user_obj,password_notebook=_D):
	J='debug';I='Invalid password';F=password_notebook;E=notebook_id;C=user_obj;logger.debug(_M);logger.debug(E);B=Notebook.objects.filter(notebook_id__startswith=E,is_delete=_C).all();D=_C
	if B.count()==1:D=_A
	else:
		K=E;B=Notebook.objects.filter(slug__startswith=K,is_delete=_C).all()
		if B.count()==1:D=_A
	logger.debug('b_found');logger.debug(D)
	if D:
		A=B[B.count()-1];L=A.has_password
		if A.is_expose_notebook:
			logger.debug('is exposed')
			if A.is_public_notebook:
				logger.debug('is public')
				if not L:logger.debug('no password');return{_B:1,_J:A}
				else:
					logger.debug('hass password')
					if F is _D:logger.debug('empty passord provided');return{_B:2,_E:'Require password',_J:A}
					else:
						try:
							if qube_6fc03565c8.sparta_f0c5730390(A.password_e)==F:return{_B:1,_J:A}
							else:return{_B:3,_E:I,_J:A}
						except Exception as M:return{_B:3,_E:I,_J:A}
			elif C.is_authenticated:
				G=sparta_faaa42601a(C)
				if len(G)>0:H=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=G,notebook__is_delete=0,notebook=A)|Q(is_delete=0,user=C,notebook__is_delete=0,notebook=A))
				else:H=NotebookShared.objects.filter(is_delete=0,user=C,notebook__is_delete=0,notebook=A)
				if H.count()>0:return{_B:1,_J:A}
			else:return{_B:-1,J:1}
	return{_B:-1,J:2}
def sparta_310f4eeae1(json_data,user_obj):A=sparta_5a61c7b346(json_data[_F]);return sparta_ee7bb73842(A)
def sparta_7b4e251846(json_data,user_obj):A=sparta_5a61c7b346(json_data[_F]);return sparta_2d82bd9c5a(A)
def sparta_9cc353c7ba(json_data,user_obj):
	C=user_obj;B=json_data;logger.debug('notebook_ipynb_set_entrypoint json_data');logger.debug(B);F=B[_I];D=Notebook.objects.filter(notebook_id__startswith=F,is_delete=_C).all()
	if D.count()==1:
		A=D[D.count()-1];F=A.notebook_id;G=sparta_faaa42601a(C)
		if len(G)>0:E=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=G,notebook__is_delete=0,notebook=A)|Q(is_delete=0,user=C,notebook__is_delete=0,notebook=A))
		else:E=NotebookShared.objects.filter(is_delete=0,user=C,notebook__is_delete=0,notebook=A)
		H=_C
		if E.count()>0:
			J=E[0];I=J.share_rights
			if I.is_admin or I.has_write_rights:H=_A
		if H:K=sparta_5a61c7b346(B['fullPath']);A.main_ipynb_fullpath=K;A.save()
	return{_B:1}
async def notebook_permission_code_exec(json_data):
	G='source';F='cellId';C=json_data;logger.debug('Callilng notebook_permission_code_exec')
	try:
		H=C[_I];D=Notebook.objects.filter(notebook_id__startswith=H,is_delete=_C)
		if await D.acount()>0:
			E=await D.afirst();I=C[F];A=E.main_ipynb_fullpath
			if A is _D:A=os.path.join(E.project_path,_G)
			J=qube_709c91858d.sparta_064dee950d(A);K=J['cells']
			for B in K:
				L=json.loads(B['metadata']['sqMetadata'])
				if L[F]==I:logger.debug('Found Cell Code');logger.debug(B[G][0]);return B[G][0]
	except Exception as M:logger.debug('Except is:');logger.debug(M);return''
	return''
def sparta_4c4bbfa821(json_data,user_obj):0
from django.core.management import call_command
from io import StringIO
def sparta_74d1cde437(project_path,python_executable=_p):
	E=python_executable;B=project_path;A=_C
	try:
		H=os.path.join(B,_N)
		if not os.path.exists(H):A=_A;return _C,f"Error: manage.py not found in {B}",A
		F=os.environ.copy();F[_q]=_r;E=sys.executable;I=[E,_N,_s,'--dry-run'];C=subprocess.run(I,cwd=B,text=_A,capture_output=_A,env=F)
		if C.returncode!=0:A=_A;return _C,f"Error: {C.stderr}",A
		G=C.stdout;J='No changes detected'not in G;return J,G,A
	except FileNotFoundError as D:A=_A;return _C,f"Error: {D}. Ensure the correct Python executable and project path.",A
	except Exception as D:A=_A;return _C,str(D),A
def sparta_ba6d43fec3():
	A=os.environ.get('VIRTUAL_ENV')
	if A:return A
	else:return sys.prefix
def sparta_e622b4d36d():
	A=sparta_ba6d43fec3()
	if sys.platform=='win32':B=os.path.join(A,'Scripts','pip.exe')
	else:B=os.path.join(A,'bin','pip')
	return B
def sparta_cea3774759(json_data,user_obj):
	D=sparta_5a61c7b346(json_data[_F]);A=D;B=os.path.join(sparta_f2edee430b()[_Y],_K,_Z);C=os.path.join(A,_O)
	if not os.path.exists(C):os.makedirs(C)
	shutil.copytree(os.path.join(B,_O),C,dirs_exist_ok=_A);logger.debug(f"Folder copied from {B} to {A}");shutil.copy2(os.path.join(B,_a),A);shutil.copy2(os.path.join(B,_b),A);return{_B:1}
def sparta_df8aca5a17(json_data,user_obj):
	A=sparta_5a61c7b346(json_data[_F]);A=os.path.join(A,_O);G,C,D=sparta_74d1cde437(A);B=_A;E=1;F=''
	if D:
		E=-1;F=C;B;H=os.path.join(A,_N)
		if not os.path.exists(H):B=_C
	I={_B:E,'has_error':D,'has_pending_migrations':G,_t:C,_E:F,'has_django_init':B};return I
def sparta_dbc6da8309(project_path,python_executable=_p):
	D=python_executable;C=project_path
	try:
		G=os.path.join(C,_N)
		if not os.path.exists(G):return _C,f"Error: manage.py not found in {C}"
		F=os.environ.copy();F[_q]=_r;D=sys.executable;H=[[D,_N,_s],[D,_N,'migrate']];B=[]
		for I in H:
			A=subprocess.run(I,cwd=C,text=_A,capture_output=_A,env=F)
			if A.stdout is not _D:
				if len(str(A.stdout))>0:B.append(A.stdout)
			if A.stderr is not _D:
				if len(str(A.stderr))>0:B.append(f"<span style='color:red'>Stderr:\n{A.stderr}</span>")
			if A.returncode!=0:return _C,'\n'.join(B)
		return _A,'\n'.join(B)
	except FileNotFoundError as E:return _C,f"Error: {E}. Ensure the correct Python executable and project path."
	except Exception as E:return _C,str(E)
def sparta_6420452dea(json_data,user_obj):
	A=sparta_5a61c7b346(json_data[_F]);A=os.path.join(A,_O);B,C=sparta_dbc6da8309(A);D=1;E=''
	if not B:D=-1;E=C
	return{_B:D,'res_migration':B,_t:C,_E:E}
def sparta_0d38f57a05(json_data,user_obj):return{_B:1}
def sparta_09b9e58b93(json_data,user_obj):return{_B:1}