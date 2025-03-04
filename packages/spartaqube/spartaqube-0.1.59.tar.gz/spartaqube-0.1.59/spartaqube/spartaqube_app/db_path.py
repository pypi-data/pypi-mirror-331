import os,sys,getpass,platform
from project.sparta_be1421a7f1.sparta_b1716a4f18.qube_4924a18fbd import sparta_b6e768294b,sparta_8f486e983a
def sparta_a71c1519be(full_path,b_print=False):
	B=b_print;A=full_path
	try:
		if not os.path.exists(A):
			os.makedirs(A)
			if B:print(f"Folder created successfully at {A}")
		elif B:print(f"Folder already exists at {A}")
	except Exception as C:print(f"An error occurred: {C}")
def sparta_96ba3db4be():
	if sparta_8f486e983a():A='/app/APPDATA/local_db/db.sqlite3'
	else:C=sparta_b6e768294b();B=os.path.join(C,'data');sparta_a71c1519be(B);A=os.path.join(B,'db.sqlite3')
	return A