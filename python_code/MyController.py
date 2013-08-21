# DEFINES BASE CLASS
# put all files pertaining to "Master" control here
from traceback import print_exc
import random 
import os
import time
import datetime
import logging
import urllib2
from httplib import BadStatusLine
from MyCommon import ProxyRotator,DatabaseHandle
from MyDict import settings_dict

INCLUDE_PROXIES_DEFAULT = settings_dict['include_proxies'] 
HIDE_BROWSER_DEFAULT = settings_dict['hide_browser']

# generic function that does makeups, or just regular routine
# NEEDS TO BE INHERITED BY OBJECT WITH MY FCN, GET JOBS
class BusCatcher:
	# stores variables and sets up logger object
	def __init__(self,day_diff_array=[0],company_name="none",do_makeups=False,use_proxies=INCLUDE_PROXIES_DEFAULT,hide_browser=HIDE_BROWSER_DEFAULT):
		id_int = random.randint(1, 5)
		
		do_makeups_str = "_straight "
		if do_makeups:
			do_makeups_str = "_makeup "
	
		self.use_proxies = use_proxies
		self.hide_browser = hide_browser
		self.do_makeups = do_makeups
		self.company_name = company_name	
		self.day_diff_array = day_diff_array
		self.id_str = company_name + "_" + str(id_int) + do_makeups_str 
		self.proxy_obj = None 
		self.sql_obj = None 
			
		#: the current number of consecutive failures 
		self.consec_fail_cur = 0 
		
		#: if my_logic fails to get data after running the following number of times, call diagnostic function
		self.consec_fail_diagnostic_thresh = 5
		
	def eval_diagnostic(self):
		self.my_logger.info("Saving html code...")
		self.save_html()
		self.my_logger.info("Taking screenshot...")
		self.take_screenshot()
		
	def iterate_jobs(self):
		"""
		This method goes over all jobs in self.my_jobs list and loads them off to self.my_logic. 
		Note that self.my_logic(cur_job) is a script for a single request.
		"""
		
		self.my_logger.critical("Starting session!")
		
		if self.use_proxies:
			self.my_logger.info("Using proxies!")
		else:
			self.my_logger.info("Not using proxies!")
		
		last_request_success = False
		
		try:
			if len(self.my_jobs) == 0:
				last_request_success = True 
				self.my_logger.critical("No jobs to do! self.my_jobs is empty")
			else:				
				self.check_status()
				self.my_logger.critical("Jobs remaining: " + str(len(self.my_jobs)) )
			
			#: this loop actually executes all the jobs! 
			while len(self.my_jobs) > 0:
				cur_job = self.my_jobs[0] 
				last_request_success = self.my_logic(cur_job)
				
				if last_request_success: 
					self.my_jobs.pop(0)
				else: 
					raise RuntimeError("Failed too many times! Shutting down!")
						
		except RuntimeError as e:
			msg_1 = "Aborting all operations."
			msg_2 = e.args[0]
			self.my_logger.critical(msg_1)
			self.my_logger.critical(msg_2)
			
		finally: 
			if last_request_success:
				self.my_logger.critical("Successfully completed schedule requests!")
			else: 
				self.my_logger.critical("Unable to complete schedule request!")
				
			self.my_logger.critical("Jobs remaining: " + str(len(self.my_jobs)) )
			self.quit()
				
	# does looping so we try every data fetch multiple times
	def my_logic(self,cur_job):
		""" This method is an iterative script which aims to call self.my_fcn(cur_job,...).
		 The idea is that we want to try running self.my_fcn multiple times before giving up.
		 For example, if the proxy is down, just switch proxy and keep going.  
		
		:param cur_job: an arbitrary object that will be passed to self.my_fcn 
		:returns: True or False depending on whether self.my_fcn was excecuted properly
		"""
		
		#: hack, just allows the function to try to execute more times before giving up 
		if self.use_proxies:
			num_proxy_rotate_allowed = settings_dict['max_tries'] 
		else: 
			num_proxy_rotate_allowed = 4

		self.my_logger.info("Number of proxy rotations allowed: " + str(num_proxy_rotate_allowed))

		num_browser_restarts_allowed = settings_dict["repeats_per_browser"]
		self.my_logger.info("Number of browser restarts allowed: " + str(num_browser_restarts_allowed))

		for _elem_ in range(num_proxy_rotate_allowed):
			for _elem_2 in range(num_browser_restarts_allowed):
				# if new error handling is required, simply raise new exceptions in self.my_fcn 
				
				request_success = False 
				restart_browser = False 
				
				try:
					request_success = self.my_fcn(self.proxy_obj.browser,self.sql_obj,cur_job,self.my_logger)
					
				except urllib2.URLError as e: 
					self.my_logger.error("URL error!")
					self.my_logger.exception(e)
					restart_browser = True
					request_success = False 
					
				except BadStatusLine as e: 
					self.my_logger.error("Bad status line!")
					self.my_logger.exception(e)
					restart_browser = True
					request_success = False 
					
				except ValueError as e:
					self.my_logger.exception(e)
					request_success = True
		
				except Exception as e: 
					self.my_logger.exception(e) 
					restart_browser = True 
					request_success = False
				
				if request_success: 
					self.consec_fail_cur = 0
					return True 
				else:
					self.consec_fail_cur += 1
					
					#: if we are either not using proxies, or...
					#: if we are about to switch proxies anyway
					if restart_browser and (not self.use_proxies or _elem_2 + 1 != num_browser_restarts_allowed):
						self.proxy_obj.restart_browser()
						self.my_logger.error("Request failed - trying again with same browser configuration.") 
					
					if self.consec_fail_cur > self.consec_fail_diagnostic_thresh:
						self.my_logger.error("Evaluating diagnostics!")
						self.eval_diagnostic()
					
					time.sleep(2)
		
			# the code will only reach this point if the requests kept failing
			if self.use_proxies:
				self.my_logger.error("Request failed: switching to new proxy.") 
				self.proxy_obj.rotate_proxy()
			
		return False 
		
	# over rides previous method in ProxyRotator class
	def take_screenshot(self,file_str=None):
		"""
		Takes screenshot of browser in self.proxy_obj and saves it to file_str. 
		:keyword file_str: path to file the method will save the screenshot to
		:returns: bool of whether screenshot was saved successful 
		"""
		
		if file_str == None: 
			now = datetime.datetime.now()
			now_str=now.strftime("%H_%M_%S")
			file_str= self.my_log_dir + "/" + self.company_name + "_"  + now_str + ".png"
		
		try:
			self.proxy_obj.browser.save_screenshot(file_str)
			self.my_logger.debug("Saved screenshot to: " + str(file_str))
			return True 
		
		except Exception as e:
			self.my_logger.exception(e)
			return False 
		
	def save_html(self,file_path=None):
		"""
		Saves html code from proxy_obj to a file 
		
		:keyword file_path: string of path to which html is saved
		:returns: bool representing whether the html source was saved successfully 
		"""
		
		if file_path == None: 
			now = datetime.datetime.now()
			now_str=now.strftime("%H_%M_%S")
			file_str= self.my_log_dir + "/" + self.company_name + "_"  + now_str + ".html"
		else: 
			file_str = file_path
			
		try: 
			html_str = self.proxy_obj.browser.page_source.encode("utf-8")
			with open(file_str,'w') as f: 
				f.write(html_str)
				
			self.my_logger.debug("Saved html source to: " + str(file_str))
			return True 
				
		except Exception as e:
			self.my_logger.exception(e)
			return False 
			
	def prepare_for_launch(self,**kwargs):
		"""
		A script that sets up my_logger, browser, job list, and makeups. 
		
		:param **kwargs: a dictionary of configurations for use in script tasks
		"""
		self.setup_my_logger(**kwargs)	
		self.setup_sql_dir()
		self.setup_connections(**kwargs)
		self.get_jobs(**kwargs)
	
		if not self.do_makeups and self.sql_obj:
			# if we aren't going through makeups, we should save to makeup table 
			self.my_logger.info("Setting up makeups...")
			self.setup_makeups(**kwargs)

	class MyJob:
		def __init__(self,cur_trip,date):
			self.cur_trip = cur_trip
			self.date = date
		
	def get_makeup_jobs(self):
		raise NotImplementedError("Subclass must implement abstract method")

	def get_regular_jobs(self):
		raise NotImplementedError("Subclass must implement abstract method")
		
	def my_fcn(self,browser,SQL_handle,job,logger):
		raise NotImplementedError("Subclass must implement abstract method")
		
	def get_makeup_tr_obj(self,job):
		raise NotImplementedError("Subclass must implement abstract method")	
		
	def get_jobs(self,**kwargs):
		self.my_logger.info("Retrieving jobs...")
		self.my_jobs = []
		if self.do_makeups:  
			self.get_makeup_jobs()
		else: 
			self.get_regular_jobs()
				
		if self.my_jobs:
			self.my_logger.info("Number of jobs: " + str(len(self.my_jobs)))
		
	# sets up sql_obj and proxy_obj
	def setup_connections(self,**kwargs):
		
		self.my_logger.info("Setting up mysql and firefox connections...")
		
		if settings_dict['include_database']:
			self.sql_obj=DatabaseHandle(self.company_name,self.my_logger)
		else: 
			self.sql_obj=None
			
		self.proxy_obj = ProxyRotator(self.company_name,self.my_logger)
		self.proxy_obj.establish_connection(use_proxy=self.use_proxies,hide_browser=self.hide_browser)
		#self.proxy_obj.take_screenshot = self.take_screenshot
			
	def setup_makeups(self,**kargs):
		for job in self.my_jobs:
			makeup_tr_obj = self.get_makeup_tr_obj(job)
			self.sql_obj.add_to_makeup(makeup_tr_obj)		
		
	def check_status(self):
		if not self.proxy_obj:
			raise RuntimeError("No internet connection! Aborting all operations.")
		elif self.proxy_obj.connection_status == False:
			raise RuntimeError("No internet connection! Aborting all operations.")
			
		if not self.proxy_obj:
			raise  RuntimeError("No browser instance! Aborting all operations")
		elif bool(self.proxy_obj.browser) == False: 
			raise RuntimeError("No browser instance! Aborting all operations")
				
	def quit(self):	
		self.my_logger.warning("Quitting...")
		
		if self.sql_obj:
			self.sql_obj.close_connection() 

		if self.proxy_obj:
			self.proxy_obj.delete_profile_dir()
			if self.proxy_obj.browser:
				try:
					self.proxy_obj.browser.close()
				except: 
					pass
					
			if self.proxy_obj.display:
				self.proxy_obj.display.stop()
				
	def setup_sql_dir(self):
		"""
		Makes sql directory where queries will be saved in sql files.  		
		"""
		sql_dir =  "../sql_files/" 
		
		if not os.path.exists(sql_dir):
			os.makedirs(sql_dir)

	# TO DO: have better keywork parameters 
	def setup_my_logger(self,**kwargs):
		"""
		Makes logging directory and sets logger instance as attributes of self. 
		"""

		summary_only = kwargs.get("summary_only",False)
		logger_name = kwargs.get("logger_name",None)

		if logger_name == None: 
			logger_name = self.id_str

		formatter = logging.Formatter('%(asctime)s: %(name)s - %(message)s')
		self.my_logger = logging.getLogger(logger_name) 
		self.my_logger.setLevel(logging.DEBUG)
		
		# set handlers
		now = datetime.datetime.now()
		now_str=now.strftime("%m_%d_%Y")
		
		my_log_dir =  "../crawl_logs/" + now_str
		
		if not os.path.exists(my_log_dir):
			os.makedirs(my_log_dir)
			
		# save logging directories' name
		self.my_log_dir = my_log_dir 
		file_str_summary = my_log_dir + "/SUMMARY.log"
		
		fh_summary = logging.FileHandler(file_str_summary)
		fh_summary.setLevel(logging.CRITICAL)
		fh_summary.setFormatter(formatter)
		self.my_logger.addHandler(fh_summary)
		
		sh_console = logging.StreamHandler()
		sh_console.setLevel(logging.DEBUG)
		sh_console.setFormatter(formatter)
		self.my_logger.addHandler(sh_console)
		
		if summary_only == True: 
			return True 
		
		file_str_details = my_log_dir + "/" + self.company_name + ".log"
		
		fh_details = logging.FileHandler(file_str_details)
		fh_details.setLevel(logging.DEBUG)
		fh_details.setFormatter(formatter)
		self.my_logger.addHandler(fh_details)
					
#  -- only to be used for testing --		
if __name__ == "__main__":
	pass
