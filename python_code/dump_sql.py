import os 
import glob 
import MySQLdb as mdb
import time
from MyDict import *

log_creds = settings_dict['log_creds']
con = mdb.connect(log_creds[0],log_creds[1],log_creds[2],log_creds[3])
cursor = con.cursor()
file_list = glob.glob("../sql_files/*.sql")
print "File list: " + str(file_list)

while len(file_list) > 0:
	file_str = file_list[0]
	
	#if os.stat(file_str)[6]==0:
	#	continue
		
	with open(file_str,'r') as f:
		for line in f:
			cursor.execute(line)
			#time.sleep(0.1)

	with open(file_str,'w') as f:
		f.write("")
			
	file_list.pop(0)
	
# now end connection 
if con: 
	con.close()
