import json,base64,asyncio,subprocess,uuid,os,requests,pandas as pd
from subprocess import PIPE
from django.db.models import Q
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from project.models_spartaqube import DBConnector,DBConnectorUserShared,PlotDBChart,PlotDBChartShared
from project.models import ShareRights
from project.sparta_be1421a7f1.sparta_304a8c1998 import qube_5ee3b67146 as qube_5ee3b67146
from project.sparta_be1421a7f1.sparta_409f708b0e import qube_ec40f4d325
from project.sparta_be1421a7f1.sparta_a4f218b878 import qube_6fc03565c8 as qube_6fc03565c8
from project.sparta_be1421a7f1.sparta_409f708b0e.qube_9e7a43612a import Connector as Connector
from project.logger_config import logger
def sparta_aafeb6ba62(json_data,user_obj):
	D='key';A=json_data;logger.debug('Call autocompelte api');logger.debug(A);B=A[D];E=A['api_func'];C=[]
	if E=='tv_symbols':C=sparta_5b4882d0a6(B)
	return{'res':1,'output':C,D:B}
def sparta_5b4882d0a6(key_symbol):
	F='</em>';E='<em>';B='symbol_id';G=f"https://symbol-search.tradingview.com/local_search/v3/?text={key_symbol}&hl=1&exchange=&lang=en&search_type=undefined&domain=production&sort_by_country=US";H={'http':os.environ.get('http_proxy',None),'https':os.environ.get('https_proxy',None)};C=requests.get(G,proxies=H)
	try:
		if int(C.status_code)==200:
			I=json.loads(C.text);D=I['symbols']
			for A in D:A[B]=A['symbol'].replace(E,'').replace(F,'');A['title']=A[B];A['subtitle']=A['description'].replace(E,'').replace(F,'');A['value']=A[B]
			return D
		return[]
	except:return[]