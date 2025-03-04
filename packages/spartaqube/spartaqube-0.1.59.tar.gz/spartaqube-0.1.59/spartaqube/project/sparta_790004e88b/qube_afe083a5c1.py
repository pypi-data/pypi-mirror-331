import time
from project.logger_config import logger
def sparta_c400d79842():
	B=0;A=time.time()
	while True:B=A;A=time.time();yield A-B
TicToc=sparta_c400d79842()
def sparta_e21f7a0a69(tempBool=True):
	A=next(TicToc)
	if tempBool:logger.debug('Elapsed time: %f seconds.\n'%A);return A
def sparta_4a51bc523e():sparta_e21f7a0a69(False)