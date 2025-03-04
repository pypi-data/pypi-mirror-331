_A='utf-8'
import os,json,base64,hashlib,random
from cryptography.fernet import Fernet
def sparta_22699959ff():A='__API_AUTH__';A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_99acad007f(objectToCrypt):A=objectToCrypt;C=sparta_22699959ff();D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_94a8a6e847(apiAuth):A=apiAuth;B=sparta_22699959ff();C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_93d3f52766(kCrypt):A='__SQ_AUTH__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_bb321150f2(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_93d3f52766(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_7f93219d7e(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_93d3f52766(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_0394e4990d(kCrypt):A='__SQ_EMAIL__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_409e0448d2(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_0394e4990d(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_7fc9c0432e(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_0394e4990d(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_b530897c42(kCrypt):A='__SQ_KEY_SSO_CRYPT__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_9824eda28d(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_b530897c42(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_fccec77eed(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_b530897c42(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_404163ed6d():A='__SQ_IPYNB_SQ_METADATA__';A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_01d21bdddf(objectToCrypt):A=objectToCrypt;C=sparta_404163ed6d();D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_2ef3cd8ca8(objectToDecrypt):A=objectToDecrypt;B=sparta_404163ed6d();C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)