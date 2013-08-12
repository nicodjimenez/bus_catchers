# greyhound selenium script 
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Response 
from scrapy.http import TextResponse 
from MyDict import month_dict, bolt_trips
import time
import datetime
import proxy_fcn
import logging
	
#cities: Baltimore, Boston, New York, Newark, Philadelphia, Washington
class proxy_rotator:
	def rotate_proxy(self):
		self.cur_proxy_req=self.cur_proxy_req+1
		if self.cur_proxy_req>self.req_limit:
			self.browser.close()			
			for x_ind in range(self.proxy_ind,self.proxy_ind+3):
				next_ind=x_ind % len(self.proxy_list)
				next_proxy=self.proxy_list[next_ind]
				
				if next_proxy==None:
					self.browser=webdriver.Firefox()
					return 0
				else:
					profile = webdriver.FirefoxProfile()	
					profile.set_preference("network.proxy.type", 1)
					profile.set_preference("network.proxy.http", next_proxy[0])
					profile.set_preference("network.proxy.http_port", int(next_proxy[1]))
					profile.update_preferences()
					new_browser=webdriver.Firefox(firefox_profile=profile)
					flag=self.check_proxy(next_proxy,new_browser)
					if flag == 0:
						self.browser=new_browser
						return 0 
						
			return 1
	
	def check_proxy(self,next_proxy,new_browser):
		try:
			new_browser.get("http://checkip.dyndns.org/")
			time.sleep(2)
			ip_element=str(new_browser.find_element_by_xpath("/html/body").text)
			print ip_element
			print next_proxy[0] 
			if next_proxy[0] in ip_element:
				return 0
			else: 
				new_browser.close()
		except: 
			new_browser.close()
			return 1
	
	def __init__(self,req_per_proxy):
		flag=proxy_fcn.update_proxies()
		if flag==1 :
			logging.info("Update proxies: success")
		else:
			logging.warning("Update proxies: failed")	
		
		proxy_list=proxy_fcn.get_proxies()
		proxy_list.append(None)	
		self.proxy_list=proxy_list
		self.req_limit=req_per_proxy
		self.cur_proxy_req=0
		self.proxy_ind=0
		self.browser=webdriver.Firefox()
