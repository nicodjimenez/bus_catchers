import re
import urllib2
import time
import datetime
import socket
import warnings
import random
import sys
import os 
import glob
from calendar import Calendar
from datetime import timedelta
import shutil
import selenium 
from selenium import webdriver
from selenium.common import exceptions
from httplib import BadStatusLine
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Response 
from scrapy.http import TextResponse 
from pyvirtualdisplay import Display
import MySQLdb as mdb

from MyDict import *

INCLUDE_PROXIES_DEFAULT = settings_dict['include_proxies'] 
HIDE_BROWSER_DEFAULT = settings_dict['hide_browser']

def get_default_url(company_name):
        if company_name == "BoltBus": 
                URL_str = "https://www.boltbus.com/" 
        elif company_name == "Greyhound":
                URL_str = "https://www.greyhound.com/"
        elif company_name == "Megabus":
                URL_str = "http://us.megabus.com/"
        elif company_name == "Peterpan":
                URL_str = "http://peterpanbus.com/"
        elif company_name == "LuckyStar":
                URL_str = "http://www.luckystarbus.com" 
        elif company_name == "GoBus": 
                URL_str = "http://www.gobusboston.com/"
        elif company_name == "FungWah": 
                URL_str = "http://www.fungwahbus.com/"
        
        return URL_str

# this sets up the directories where all the logging information will be organized
def setup_directories():
        bus_list = [key for key in BusID_dict]
        log_dir="../crawl_logs"
        
        for company_name in bus_list:
        
                # setup run_log, makeup_log, and run_pics directories
                if (log_dir + "/" + company_name) not in glob.glob(log_dir + "/*"):
                        os.mkdir(log_dir + "/" + company_name)
                        os.mkdir(log_dir + "/" + company_name + "/run_logs")
                        os.mkdir(log_dir + "/" + company_name + "/makeup_logs")
                        os.mkdir(log_dir + "/" + company_name + "/run_pics")
                        
        if (log_dir + "/" + "SUMMARY") not in glob.glob(log_dir + "/*"):
                os.mkdir(log_dir + "/" + "SUMMARY")


# emergency flag bypasses checking whether we have overused a given proxy: just find a proxy that works
class ProxyRotator:
    """
    some doc string 
    sdf
    """
    def __init__(self,company_name,logger):
        
        #: are we using proxies? 
        self.use_proxy = None
        self.company_name = company_name
        self.logger = logger
        self.browser = []
        self.proxy_list = []
        self.profile = None
        self.display = None
        self.connection_status = None 
        self.socket = socket 
        self.socket.setdefaulttimeout(settings_dict['default_timeout'])    
        
    def load_proxy_firefox(self,cur_proxy):
        """
        Takes proxy and returns Firefox webdriver instance using this proxy. 
        
        :param cur_proxy: proxy in [IP,Port] format 
        :returns: webdriver.Firefox instance using this proxy 
        """
        self.profile = webdriver.FirefoxProfile()    
        self.profile.set_preference("network.proxy.type", 1)
        self.profile.set_preference("network.proxy.http", cur_proxy[0])
        self.profile.set_preference("network.proxy.http_port", int(cur_proxy[1]))
        self.profile.update_preferences()
        browser = webdriver.Firefox(firefox_profile=self.profile)
        return browser 
        
    def load_proxies(self,proxy_file_path="./proxy_lists/full_list_nopl/_reliable_list.txt"):
    	""" 
    	Works with HMA proxy lists. 
    	:param proxy_file_path: path to .txt file, each line being formatted as IP,PORT
    	"""
    	
    	file_handle = open(proxy_file_path,'r')
    	text = file_handle.read()
    	proxy_list = []
    	text_lines = re.split("\n+",text)
    	
    	for line in text_lines:
    		if len(line)>2:
    			cur_list=re.split(":",line)
    			proxy_list.append(cur_list)
    			
    	self.proxy_list = proxy_list
    	
        if self.proxy_list: 
            if settings_dict['include_root_ip']:
                proxy_list.append(None)		
    	
    	self.proxy_list = proxy_list
        
    	return proxy_list  
	
    def establish_connection(self,use_proxy=INCLUDE_PROXIES_DEFAULT,hide_browser=HIDE_BROWSER_DEFAULT):
        """
         This method checks the internet connection, and starts a Firefox instance if internet works. 
        If client wishes to use proxies, the Firefox instance will be loaded with the first proxy in self.proxy_list
        
         	:keyword use_proxy: bool indicating whether the proxy list specified in self.proxy_list should used to hide IP.   
         	:keyword hide_browser: bool indicating whether Firefox is loaded using a virtual display (see pyvirtualdisplay docs for more info)
        """
        
        self.use_proxy = use_proxy 
        self.connection_status = self.check_internet()	
        
        if hide_browser:
        	self.display = Display(visible=0, size=(800, 600))
        	self.display.start()
            
        if not use_proxy:
            self.profile = webdriver.FirefoxProfile()    
            self.browser = webdriver.Firefox(firefox_profile=self.profile)
        else:
            if not self.proxy_list: 
            	self.logger.warning("Using default load_proxy function.")
            	self.load_proxies()
        	
        	if self.proxy_list:
        		new_proxy = self.proxy_list.pop(0)
        		self.browser = self.load_proxy_firefox(new_proxy)
        		self.logger.info("The following proxy is now being used: " + str(new_proxy))
            else:
                self.profile = webdriver.FirefoxProfile()
                self.browser = webdriver.Firefox(firefox_profile=self.profile)
            pass 
        		#raise ValueError("proxy_list attribute must be set before calling load_proxy_firefox method!")
    def rotate_proxy(self):
        """ 
        Closes browser and relaunches it with next proxy in self.proxy_list
        """
        try:
			self.logger.info("Closing current browser...")
			self.browser.close()	
        except Exception as e:
			self.logger.exception(e)
				
        new_proxy = self.proxy_list.pop(0) 
        new_firefox = self.load_proxy_firefox(new_proxy)
        self.browser = new_firefox
        self.logger.info("The following proxy is now being used: " + str(new_proxy))
    
    def gen_new_profile(self,cur_proxy=None):
        """
        Returns a new firefox profile.  Same settings, new directory. 
        
        :keyword cur_proxy: if None don't use proxy, else proxy should be in [IP,Port] format
        :returns: instance of webdriver.Firefox profile class
        """
        
        if cur_proxy: 
            profile = webdriver.FirefoxProfile()    
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.http", cur_proxy[0])
            profile.set_preference("network.proxy.http_port", int(cur_proxy[1]))
            profile.update_preferences()
        else: 
            profile = webdriver.FirefoxProfile()   

        return profile 
    
    def restart_browser(self):
        """ 
        Restarts browser using the same profile as before
        """
        self.logger.info("Restarting browser...")
        
    	try:
	       	self.browser.close()
        except Exception as e: 
	        self.logger.exception(e)
        
        self.delete_profile_dir()
        
        # by default, don't use proxy
        # if you want to use proxies and self.proxy_list is not empty, do use
        
        cur_proxy = None  
        if self.use_proxy and self.proxy_list:
            cur_proxy = self.proxy_list[0]
        
        new_profile = self.gen_new_profile(cur_proxy)
    	self.browser = webdriver.Firefox(firefox_profile=new_profile)
    	self.logger.info("Now using new browser!")
          
    def delete_profile_dir(self):
        if self.profile:
			cur_path = self.profile.path
        
        try:
            shutil.rmtree(str(cur_path))
            self.logger.info("Successfully deleted profile directory")
        except OSError as e:
        	self.logger.info(str(e))
        	self.logger.info("Unable to delete profile directory: " + cur_path)

	# TODO: this function should belong to BusCatcher class, not ProxyObj 
    def check_internet(self):
		try:
			response=urllib2.urlopen('https://www.google.com/')
			return True
		except urllib2.URLError as err: pass
		return False
	
	# returns error flag (True -> an error occurred)
    def check_proxy(self,next_proxy,new_browser):
		self.logger.debug("Checking proxy...")
		try:
			new_browser.get("http://checkip.dyndns.org/")
			time.sleep(2)
			ip_element=str(new_browser.find_element_by_xpath("/html/body").text)
			if next_proxy[0] in ip_element:
				msg="Proxy is active"
				self.logger.info(msg)
				return 0
			else: 
				msg="Proxy failed: " + next_proxy[0]
				self.logger.warning(msg)
				try:
					self.logger.info("Closing browser")
					new_browser.close()
				except: 
					self.logger.info("Unable to close browser")
					pass
				return 1
				
		except urllib2.URLError as e:
			self.logger.error("Connection failure! Internet is off or browser is off")
			self.logger.error(str(e))
			return 1
		
		except socket.timeout as e:
			self.logger.error("Proxy connection timeout!")
			self.logger.error(str(e))
			return 1		
				
		except:
			msg="Proxy failed: " + next_proxy[0]
			self.logger.warning(msg)
			
			try:
				self.logger.info("Closing browser...")
				new_browser.close()
			except: 
				self.logger.info("Unable to close browser")
				pass
				
			return 1

# note: makeup_id is an integer
class MakeupTravelContainer:	
# route id string becomes the MySQL id 
	def __init__(self,company_name,depart_datetime,depart_city,arrive_city,route_id_str=None):
		#self.table_name=company_name + "_makeup"
		self.company_name=company_name
		self.depart_date=depart_datetime.strftime("%Y-%m-%d")
		self.depart_city=depart_city
		self.arrive_city=arrive_city
		bus_id_str=BusID_dict[company_name]
		
		if bool(route_id_str):
			cities_id_str = route_id_str + depart_datetime.strftime("%m%d") + bus_id_str
		else:
			cities_id_str= CityID_dict[depart_city]+CityID_dict[arrive_city]+depart_datetime.strftime("%m%d") + bus_id_str
			
		self.trip_id=int(cities_id_str)

class TravelContainer:
	def __init__(self,company_name,depart_datetime,arrive_datetime,hour_diff,minute_diff,depart_city,arrive_city,price):
		# 'YYYY-MM-DD HH:MM:SS'	
		# price should be an integer or should be None
		self.company_name=company_name
		
		if bool(price):
			self.trip_cost=str(price)
		else:
			self.trip_cost="NULL"
			
		self.table_name=str(depart_datetime.year) + str(month_dict[depart_datetime.month]) + str(depart_datetime.day)
		# now.strftime("%p") gives 'AM' or 'PM' and %I gives number of hours in [1,12]
		# strftime("%Y-%m-%d %I:%M:%S %p")
		# the following give time in military time
		self.depart_time=depart_datetime.strftime("%Y-%m-%d %H:%M:%S")
		
		if bool(arrive_datetime):
			self.arrive_time=arrive_datetime.strftime("%Y-%m-%d %H:%M:%S")
			self.trip_length=str(hour_diff)+"H, " + str(minute_diff) + "m"
		else:
			self.arrive_time="NULL"
			self.trip_length="NULL"
			
		self.depart_city=depart_city
		self.arrive_city=arrive_city
		
		bus_id_str=BusID_dict[company_name]
		cities_id_str= CityID_dict[depart_city]+CityID_dict[arrive_city]+depart_datetime.strftime("%H%M") + bus_id_str
		#trip_id = BusID_dict[company_name]
		self.trip_id=int(cities_id_str)
		
#self.con = mdb.connect('nicodjimenez.com','nicodj5_ilike123','theleonius1a2b3c4d','nicodj5_bus_schedules')
#self.con = mdb.connect('localhost', 'easy_rider', 'theleonius', 'bus_schedules')
#self.con = mdb.connect('localhost','bestca12_rider','theleonius','bestca12_bus_schedules')

class DatabaseHandle:
	""" 
	This new database handle writes sql commands to a .tmp text file. 
	Once this file is done, it will be renamed as a .sql file, which will be eaten up by a cronjob.
	"""
	def __init__(self,company_name,logger):
		
		warnings.simplefilter("ignore")
		self.logger = logger
		self.company_name = company_name
		self.now = datetime.datetime.now()
		self.today=datetime.date.today()
		self.makeup_table_name = company_name + "_makeup"
		
		output_file_name = logger.name[0:-1] + ".sql"
		self.output_file_path = os.path.join("../sql_files",output_file_name) 
		
		# we delete last two week's tables of old schedules 
		for days_before in range(1,15):
			cur_delta=timedelta(days=days_before)
			cur_datetime=self.now-cur_delta
			table_name=str(cur_datetime.year) + str(month_dict[cur_datetime.month]) + str(cur_datetime.day)
			str_0 = "DROP TABLE IF EXISTS " + table_name	
			self.logger.debug(str_0)
			self.logger.debug(str_0)	
			self.cur_execute(str_0)
			
	def cur_execute(self,str): 
		with open(self.output_file_path, "a") as text_file:
		    text_file.write(str + ";")
		    text_file.write("\n")			

	def close_connection(self):
		""" (Deprecated code that) renames to .sql file so that cron job will eat it up """
		pass 
        
        """ Old lines of code:
        sql_file_path = self.output_file_path[0:-4] + ".sql" 
		self.logger.critical("Renaming file with sql extension...")
		os.rename(self.output_file_path, sql_file_path) 	
		self.logger.critical("Successfully renamed file: " + sql_file_path) 
		"""
	
	def clear_makeups(self):
		str_0 = "TRUNCATE TABLE " + self.makeup_table_name
		self.logger.debug(str_0)
		self.cur_execute(str_0)
		self.close_connection()
	
	def retrieve_makeups(self,company_name):
		
		log_creds = settings_dict['log_creds']
		con = mdb.connect(log_creds[0],log_creds[1],log_creds[2],log_creds[3])
		cur = con.cursor()
		str_0 = "DELETE FROM " + self.makeup_table_name + " WHERE DEPART_DATE < '" + self.today.strftime("%Y-%m-%d") + "'"
		self.logger.debug(str_0)
		cur.execute(str_0)
		str_1 = "SELECT * FROM " + self.makeup_table_name
		self.logger.debug(str_1)
		cur.execute(str_1)
		rows = cur.fetchall()
		con.close()
		return rows
		
	# note: this is actually a  makeup travel object
	def add_to_makeup(self,tr_obj): 
		#cur = self.con.cursor()
		table_arg=self.makeup_table_name + "("
		id_arg="TRIP_ID INT PRIMARY KEY, "
		company_name_arg="COMPANY_NAME VARCHAR(40), "
		depart_city_arg="DEPART_CITY VARCHAR(40), "
		arrive_city_arg="ARRIVE_CITY VARCHAR(40), "
		depart_date_arg="DEPART_DATE DATE)"
		setup_table_str="CREATE TABLE IF NOT EXISTS " + table_arg + id_arg + company_name_arg + depart_city_arg + arrive_city_arg + depart_date_arg
		self.logger.debug(setup_table_str)
		self.cur_execute(setup_table_str)
		str_0="INSERT INTO " + self.makeup_table_name + "(TRIP_ID,COMPANY_NAME,DEPART_CITY,ARRIVE_CITY,DEPART_DATE) VALUES"
		str_1= "(" +  str(tr_obj.trip_id) + ",\'" + tr_obj.company_name + "\'"  \
		+ ",\'" + tr_obj.depart_city + "\'" + ",\'" + tr_obj.arrive_city + "\'" + \
		",\'" + tr_obj.depart_date + "\'" + ")" 
		str_2=" ON DUPLICATE KEY UPDATE TRIP_ID = TRIP_ID"
		total_str = str_0 + str_1 + str_2 
		self.logger.debug(total_str)
		self.cur_execute(total_str)
		
	def subtract_from_makeup(self,tr_obj):
		#cur = self.con.cursor()
		str_0 = "DELETE FROM " + self.makeup_table_name + " WHERE TRIP_ID = " + str(tr_obj.trip_id)
		self.logger.debug(str_0)
		self.cur_execute(str_0)
	
	#self.con = mdb.connect('nicodjimenez.com','nicodj5_ilike123','theleonius1a2b3c4d','nicodj5_bus_schedules')
	# this table takes a travel object and stores it in a row of the mysql 
	def update_table(self,tr_obj,URL_str="NULL"):
		
		if (URL_str == "NULL") or (tr_obj.company_name == "Peterpan"):
			URL_str = get_default_url(tr_obj.company_name)
			
		table_arg=tr_obj.table_name + "("
		id_arg="TRIP_ID INT PRIMARY KEY, "
		company_name_arg="COMPANY_NAME VARCHAR(40), "
		depart_city_arg="DEPART_CITY VARCHAR(40), "
		arrive_city_arg="ARRIVE_CITY VARCHAR(40), "
		depart_time_arg="DEPART_TIME DATETIME, "
		arrive_time_arg="ARRIVE_TIME DATETIME, "
		trip_length_arg="TRIP_LENGTH VARCHAR(12), "
		trip_cost_arg="TRIP_COST int,"
		page_url="URL VARCHAR(500))" 
		setup_table_str="CREATE TABLE IF NOT EXISTS " + table_arg + id_arg + company_name_arg + depart_city_arg + arrive_city_arg + depart_time_arg + arrive_time_arg + trip_length_arg + trip_cost_arg + page_url
		self.cur_execute(setup_table_str)
		str_0="INSERT INTO " + tr_obj.table_name + "(TRIP_ID,COMPANY_NAME,DEPART_CITY,ARRIVE_CITY,DEPART_TIME,ARRIVE_TIME,TRIP_LENGTH,TRIP_COST,URL) VALUES"
		str_1= "(" +  str(tr_obj.trip_id) + ",\'" + tr_obj.company_name + "\'"  \
		+ ",\'" + tr_obj.depart_city + "\'" + ",\'" + tr_obj.arrive_city + "\'" + \
		",\'" + tr_obj.depart_time + "\'" + ",\'" + tr_obj.arrive_time + "\'" + \
		",\'" + tr_obj.trip_length + "\'" + "," + tr_obj.trip_cost + ",\'" + str(URL_str) + "\'" + ")" 
		str_2=" ON DUPLICATE KEY UPDATE TRIP_COST = " + tr_obj.trip_cost
		total_str = str_0 + str_1 + str_2
		self.logger.debug(total_str)
		self.cur_execute(total_str)		
