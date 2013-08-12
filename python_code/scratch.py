from selenium import webdriver
from pyvirtualdisplay import Display
import time 
from MyDict import *


display = Display(visible=0, size=(800, 600))
display.start()	
browser=webdriver.Firefox()

browser.get("http://us.megabus.com/")
time.sleep(10 * settings_dict['slowness_factor'])

drop_down=browser.find_element_by_id("JourneyPlanner_ddlLeavingFrom")
drop_down_elements=drop_down.find_elements_by_xpath("./option")
	
elements_str=[elem.text for elem in drop_down_elements]
element_ind=elements_str.index("New York, NY")
drop_down_elements[element_ind].click()
time.sleep(5 * settings_dict['slowness_factor'])

drop_down=browser.find_element_by_id("JourneyPlanner_ddlTravellingTo")
drop_down_elements=drop_down.find_elements_by_xpath("./option")

elements_str=[elem.text for elem in drop_down_elements]
element_ind=elements_str.index("Boston, MA")
drop_down_elements[element_ind].click()
time.sleep(5 * settings_dict['slowness_factor'])

# NEED TO REMOVE OLD DATE STRING
browser.find_element_by_id("JourneyPlanner_txtOutboundDate").clear()
time.sleep(3 * settings_dict['slowness_factor']) 
browser.find_element_by_id("JourneyPlanner_txtOutboundDate").send_keys(date_str)

#time.sleep(2 * settings_dict['slowness_factor']) 
try:
	browser.find_element_by_id("JourneyPlanner_txtOutboundDate").send_keys(Keys.ENTER)
except: 
	pass
	
time.sleep(5 * settings_dict['slowness_factor']) 
msg="Clicking on search button..."

try:
	browser.find_element_by_id("JourneyPlanner_btnSearch").click()
except: 
	pass
	
time.sleep(8 * settings_dict['slowness_factor']) 
