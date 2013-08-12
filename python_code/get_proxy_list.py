# greyhound selenium script 
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Response 
from scrapy.http import TextResponse 
import time

browser = webdriver.Firefox()
browser.get("http://www.hidemyass.com/proxy-list/")
allCountry_cb=browser.find_element_by_id("allCountries")
allCountry_cb.click()
time.sleep(3)
country_table=browser.find_element_by_id("country")
country_list=country_table.find_elements_by_tag_name("option")

for ind in range(0,10):
	cur_country=country_list[ind].text
	if "United States" in cur_country:
		country_list[ind].click()
		time.sleep(3)
		break

speed_table=browser.find_element_by_id("norightborder") 
speed_list=speed_table.find_elements_by_tag_name("label")

for speed in speed_list:
	speed_str=speed.text
	if ("Slow" in speed_str)or("Medium" in speed_str):
		speed.click()
		time.sleep(1)

search_bt=browser.find_element_by_id("updateresults")
search_bt.click()
time.sleep(5)
text_html=browser.page_source.encode('utf-8')
html_str=str(text_html)
resp_for_scrapy=TextResponse('none',200,{},html_str,[],None)
hxs=HtmlXPathSelector(resp_for_scrapy)


#table_rows=hxs.select('//tr[@class="fareviewrow"] | //tr[@class="fareviewaltrow"]')
#row_ct=len(table_rows)
#row_ct=len(table_rows)
	
#for x in xrange(row_ct):
#	cur_node_elements=table_rows[x]
#	travel_price=cur_node_elements.select('.//td[@class="faresColumn0"]/text() | .//td[@class="faresColumn0 faresColumnDollar"]/text()').re("\d{1,3}\.\d\d")
	
	# actual digits of time 
#	depart_time_num=cur_node_elements.select('.//td[@class="faresColumn1"]/text()').re("\d{1,2}\:\d\d")
	# AM or PM (time signature)
#	depart_time_sig=cur_node_elements.select('.//td[@class="faresColumn1"]/text()').re("[AP][M]")
	
	# actual digits of time 
