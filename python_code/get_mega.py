import random 
import datetime
from datetime import timedelta
import selenium
from MyController import BusCatcher
from MyDict import *
from MyCommon import *

COMPANY_NAME = "Megabus"

class MyCatcher(BusCatcher):
	def __init__(self,day_diff_array=[],do_makeups=False):
		BusCatcher.__init__(self,day_diff_array,COMPANY_NAME,do_makeups,use_proxies=False)
		self.prepare_for_launch()

	def get_makeup_tr_obj(self,job):
		makeup_tr_obj = MakeupTravelContainer(COMPANY_NAME,job.date,job.cur_trip[0],job.cur_trip[1],job.cur_trip[-1])
		return makeup_tr_obj
		
	def get_regular_jobs(self):
		now = datetime.datetime.now()
		date_vector=[]
		random.shuffle(date_vector)
		random.shuffle(megabus_trips)
		
		for day_diff in self.day_diff_array:
			time_delta=timedelta(days=day_diff)
			date_vector.append(now+time_delta)

		for date in date_vector:
			for cur_trip in megabus_trips:
				cur_job = self.MyJob(cur_trip,date)
				self.my_jobs.append(cur_job)
		
	def get_makeup_jobs(self):
	
		rows = self.sql_obj.retrieve_makeups(COMPANY_NAME)
		origin_to_destination_exact=[[trip[0],trip[1]] for trip in megabus_trips]
			
		for row in rows:
			try:
				cityOrigin_exact=row[2]
				cityDeparture_exact=row[3]
				date=row[4]
				trip_ind=origin_to_destination_exact.index([cityOrigin_exact,cityDeparture_exact])
				cur_trip = megabus_trips[trip_ind]
				cur_job = self.MyJob(cur_trip,date)
				self.my_jobs.append(cur_job)
			except ValueError:
				pass

	def my_fcn(self,browser,SQL_handle,job,logger):
		cur_trip = job.cur_trip
		date = job.date
	
		# *_tag is just the city name (no streets etc) that will be stored in the database
		cityOrigin=cur_trip[0]
		cityDeparture=cur_trip[1]
		cityOrigin_tag=cur_trip[0]
		cityDeparture_tag=cur_trip[1]
		logger.info("NEW SEARCH")

		logger.info("Deleting all cookies...")
		browser.delete_all_cookies()
		time.sleep(3 * settings_dict['slowness_factor']) 
		logger.info("Loading URL...")
		browser.get("http://us.megabus.com/")
		time.sleep(10 * settings_dict['slowness_factor'])
		
		cur_day=date.day
		cur_month=date.month
		cur_year=date.year
		cur_month_str=month_dict[int(cur_month)]
		date_str=date.strftime("%m/%d/%Y")
		
		msg="From " + cityOrigin_tag + " to " + cityDeparture_tag + " (" + date_str + ")"
		logger.info(msg)
		
		logger.info("Clicking on origin city...")
		drop_down=browser.find_element_by_id("JourneyPlanner_ddlLeavingFrom")
		drop_down_elements=drop_down.find_elements_by_xpath("./option")
		
		if len(drop_down_elements) == 0:
			return False
			
		logger.info("Finding element in drop_down_elements..")
		elements_str=[elem.text.lower() for elem in drop_down_elements]
		element_ind=elements_str.index(cityOrigin.lower())
		drop_down_elements[element_ind].click()
		time.sleep(10 * settings_dict['slowness_factor'])
		
		#self.proxy_obj.take_screenshot()
		
		msg="Clicking on destination city..."
		logger.info(msg)
		
		drop_down=browser.find_element_by_id("JourneyPlanner_ddlTravellingTo")
		drop_down_elements=drop_down.find_elements_by_xpath("./option")
		
		if len(drop_down_elements) == 0:
			return False	
		
		logger.info("Finding element in drop_down_elements..")
		elements_str=[elem.text.lower() for elem in drop_down_elements]
		element_ind=elements_str.index(cityDeparture.lower())
		drop_down_elements[element_ind].click()
		time.sleep(5 * settings_dict['slowness_factor'])
		
		#self.proxy_obj.take_screenshot()
		
		msg="Typing departure date..."
		logger.info(msg)
		
		# NEED TO REMOVE OLD DATE STRING
		browser.find_element_by_id("JourneyPlanner_txtOutboundDate").clear()
		time.sleep(1) 
		browser.find_element_by_id("JourneyPlanner_txtOutboundDate").send_keys(date_str)
		browser.find_element_by_id("JourneyPlanner_txtOutboundDate").send_keys(Keys.ENTER)
		browser.find_element_by_id("JourneyPlanner_txtOutboundDate").send_keys(Keys.ENTER)
			
		time.sleep(8 * settings_dict['slowness_factor']) 
		msg="Clicking on search button..."
		logger.info(msg)
		
		#browser.find_element_by_class_name("btn_search btn").click()
		#browser.find_element_by_id("JourneyPlanner_btnSearch").click()
		# browser.execute_script("return WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions('JourneyPlanner$btnSearch', '', true, 'jp', '', false, false))")

		browser.find_element_by_id("JourneyPlanner_btnSearch").send_keys(Keys.ENTER)
		
		time.sleep(10 * settings_dict['slowness_factor']) 
		
		# parse entire table 
		logger.info("Parsing table...")
		text_html=browser.page_source.encode('utf-8')
		html_str=str(text_html)
		resp_for_scrapy=TextResponse('none',200,{},html_str,[],None)
		hxs=HtmlXPathSelector(resp_for_scrapy)
		table_rows=hxs.select('//ul[@class="journey standard"]')	
		row_ct=len(table_rows)		
		
		#self.proxy_obj.take_screenshot()
		
		if row_ct == 0:
			msg="No data for this travel date"
			logger.info(msg)
			return True
		else:
			# we need to get at least one piece of data for the request to be deemed a success
			for x in xrange(row_ct):
			
				cur_node_elements=table_rows[x]
				
				depart_time_num=cur_node_elements.select(".//li[2]/p[1]").re("\d{1,2}\:\d\d")
				depart_time_sig=cur_node_elements.select(".//li[2]/p[1]").re("[AP][M]")
				arrive_time_num=cur_node_elements.select(".//li[2]/p[2]").re("\d{1,2}\:\d\d")
				arrive_time_sig=cur_node_elements.select(".//li[2]/p[2]").re("[AP][M]")
				travel_price=cur_node_elements.select(".//li[6]").re("\d{1,3}\.\d\d")
				travel_time=cur_node_elements.select(".//li[3]")				

				if len(travel_price)==0:
					travel_price=None
				
				bool_value=bool(len(depart_time_num) * len(depart_time_sig) * len(arrive_time_num) * len(arrive_time_sig) * len(travel_time))
				
				if bool_value == True:
					msg= "Depart date: " + date_str
					logger.debug(msg)
					msg= "Depart time: " + depart_time_num[0] + " " + depart_time_sig[0]
					logger.debug(msg)	
					msg= "Arrive time: " + arrive_time_num[0] + " " + arrive_time_sig[0]
					logger.debug(msg)
					
					if bool(travel_price)==False:
						msg="Ticket is sold out"
						logger.debug(msg)	
						travel_price_sql=None
					else:
						msg= "Cost: " + "$" + str(travel_price[0])
						logger.debug(msg)
						travel_price_sql=int(float(travel_price[0]))
						
					# create depart datetime object
					depart_time_list=re.split(":",depart_time_num[0])
					depart_minute=int(depart_time_list[1])
					pre_depart_hour=int(depart_time_list[0])
					
					if depart_time_sig[0]=='AM':
						if pre_depart_hour==12:
							depart_hour=pre_depart_hour-12
						else:
							depart_hour=pre_depart_hour
					elif depart_time_sig[0]=='PM':
						if pre_depart_hour==12:
							depart_hour=pre_depart_hour
						else:
							depart_hour=pre_depart_hour+12
							
					depart_datetime=datetime.datetime(year=cur_year,month=cur_month,day=cur_day,hour=depart_hour,minute=depart_minute)
					
					# now do arrive data
					day_str=travel_time.re("(\d{1})[Dd]")
					if bool(day_str):
						day_diff=int(day_str[0])
					else:
						day_diff=0 
						
					# now do arrive data
					hour_str=travel_time.re("(\d{1,2})[Hh]")
					if bool(hour_str):
						hour_diff=int(hour_str[0])
					else:
						hour_diff=0
					
					minute_str=travel_time.re("(\d{1,2})[Mm]")
					if bool(minute_str):
						minute_diff=int(minute_str[0])
					else:
						minute_diff=0 
						
					trip_delta = timedelta(days=day_diff,hours=hour_diff,minutes=minute_diff)
					arrive_datetime = depart_datetime+trip_delta
					travel_obj = TravelContainer(COMPANY_NAME,depart_datetime,arrive_datetime,hour_diff,minute_diff,cityOrigin_tag,cityDeparture_tag,travel_price_sql)
					
					if settings_dict['include_database']:
						SQL_handle.update_table(travel_obj,browser.current_url)
						
					
				elif (bool(len(depart_time_sig))==False) or (bool(len(arrive_time_sig))==False):
					msg="Time signature missing! Continue with next row"
					logger.info(msg)
					continue
					
					
				elif (bool(len(depart_time_num))==False) or (bool(len(arrive_time_num))==False):
					msg="Actual times are missing! Continue with next row"
					logger.info(msg)
					continue	
					
				elif bool(len(travel_time)) == False:
					msg="Travel time is missing! Continue with next row"
					logger.info(msg)
					continue 
			
		if settings_dict['include_database'] and settings_dict['include_makeup']:
			msg= "Updating makeup table..."
			logger.info(msg)
			makeup_tr_obj=MakeupTravelContainer(COMPANY_NAME,date,cur_trip[0],cur_trip[1],cur_trip[-1])
			SQL_handle.subtract_from_makeup(makeup_tr_obj)
					
		return True
				
if __name__ == "__main__":
	bs = MyCatcher(day_diff_array=[0,1,2,3,4,5])
	#bs = MyCatcher(do_makeups=None)
	bs.iterate_jobs()

	
	
