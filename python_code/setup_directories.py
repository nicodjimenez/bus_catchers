import os 
import glob 
from MyDict import *

def setup_directories():
	bus_list = [key for key in BusID_dict]
	log_dir="../crawl_logs"
	
	for company_name in bus_list:
	
		# setup run_log, makeup_log, and run_pics directories
		if (log_dir + "/" + company_name)  not in glob.glob(log_dir + "/*"):
			os.mkdir(log_dir + "/" + company_name)
			os.mkdir(log_dir + "/" + company_name + "/run_logs")
			os.mkdir(log_dir + "/" + company_name + "/makeup_logs")
			os.mkdir(log_dir + "/" + company_name + "/run_pics")
	
		
