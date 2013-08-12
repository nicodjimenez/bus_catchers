import random 
import datetime
from datetime import timedelta
import selenium
from MyController import BusCatcher
from MyDict import *
from MyCommon import *

COMPANY_NAME = "Amtrak"

class MyCatcher(BusCatcher):
	def __init__(self,day_diff_array=[],do_makeups=False):
		BusCatcher.__init__(self,day_diff_array,COMPANY_NAME,do_makeups)
		self.prepare_for_launch()

	def get_makeup_tr_obj(self,job):
		makeup_tr_obj = MakeupTravelContainer(COMPANY_NAME,job.date,job.cur_trip[0][1],job.cur_trip[1][1])
		return makeup_tr_obj
		
	def get_regular_jobs(self):
		now = datetime.datetime.now()
		date_vector=[]
		random.shuffle(date_vector)
		random.shuffle(amtrack_cities)
		
		for day_diff in self.day_diff_array:
			time_delta=timedelta(days=day_diff)
			date_vector.append(now+time_delta)
		
		for date in date_vector:
			for cur_city_1 in amtrack_cities:
				for cur_city_2 in amtrack_cities:
					
					if cur_city_1 == cur_city_2: 
						continue
						
					cur_trip = [cur_city_1,cur_city_2]
					cur_job = self.MyJob(cur_trip,date)
					self.my_jobs.append(cur_job)
		
	def get_makeup_jobs(self):
		rows = self.sql_obj.retrieve_makeups(COMPANY_NAME)
		cities_tag=[cities[1] for cities in amtrack_cities]
		cities_exact=[cities[0] for cities in amtrack_cities]
			
		for row in rows: 
			try:
				cityOrigin_tag=row[2]
				cityDeparture_tag=row[3]
				date=row[4]
				cityOrigin_ind=cities_tag.index(cityOrigin_tag)
				cityDeparture_ind=cities_tag.index(cityDeparture_tag)
				cur_trip = [amtrack_cities[cityOrigin_ind],amtrack_cities[cityDeparture_ind]]
				cur_job = self.MyJob(cur_trip,date)
				self.my_jobs.append(cur_job)
			except ValueError:
				pass

	def my_fcn(self,browser,SQL_handle,job,logger):
		cur_trip = job.cur_trip
		date = job.date
		# *_tag is just the city name (no streets etc) that will be stored in the database
		cityOrigin=cur_trip[0][0]
		cityDeparture=cur_trip[1][0]
		cityOrigin_tag=cur_trip[0][1]
		cityDeparture_tag=cur_trip[1][1]
		logger.info("NEW SEARCH")
		
		logger.info("Deleting all cookies...")
		browser.delete_all_cookies()
	
		time.sleep(3 * settings_dict['slowness_factor']) 
		browser.get("http://tickets.amtrak.com/itd/amtrak")
		#browser.switch_to_alert().accept()
		time.sleep(12 * settings_dict['slowness_factor']) 
		
		cur_day=date.day
		cur_month=date.month
		cur_year=date.year
		cur_month_str=month_dict[int(cur_month)]
		date_str=date.strftime("%m/%d/%Y")
		
		msg="From " + cityOrigin_tag + " to " + cityDeparture_tag + " (" + date_str + ")"
		logger.info(msg)
		
		#self.take_screenshot() 
		logger.info("Clearing text fields")
		elem_0=browser.find_element_by_name("wdf_origin")
		elem_0.clear()
		elem_1=browser.find_element_by_name("wdf_destination")
		elem_1.clear()
		elem_2=browser.find_element_by_id("wdfdate1")
		
		logger.info("Typing origin city...")
		elem_0.send_keys(cityOrigin)
		#self.take_screenshot()
		time.sleep(3 * settings_dict['slowness_factor']) 
		
		logger.info("Typing destination city...")
		elem_1.send_keys(cityDeparture)
		#self.take_screenshot()
		time.sleep(3 * settings_dict['slowness_factor']) 
	
		# get calendar 
		elem_2.click()
		calendar=browser.find_element_by_xpath("//*[contains(@id, 'calContainer')]")
		time.sleep(1 * settings_dict['slowness_factor'])
		logger.info("Selecting current month...")
		#self.take_screenshot()		

		# select current month 
		sel_month=calendar.find_element_by_class_name("calheader").text
		
		if not cur_month_str in sel_month: 
			next_month_button = calendar.find_element_by_class_name("calnavright")
			
			for ind in xrange(1,12):
				next_month_button.click()
				time.sleep(3 * settings_dict['slowness_factor'])	
				#calendar=browser.find_element_by_class_name("calendar")
				sel_month=calendar.find_element_by_class_name("calheader").text
	
				if cur_month_str in sel_month: 
					break
		
		# select correct day
		logger.info("Selecting correct day...")
		calendar=browser.find_element_by_xpath("//*[contains(@id, 'calContainer')]")
		days_boxes = calendar.find_elements_by_xpath("..//div/table/tbody/tr/td")
		
		if len(days_boxes)==0: 
			raise RuntimeError("Unable to locate days boxes!")
		
		ind_diff = 10 - int(days_boxes[10].text)
		cur_day_index=cur_day + ind_diff
		days_boxes[cur_day_index].click()
		time.sleep(7 * settings_dict['slowness_factor']) 			
		logger.info("Clicking on search button...")
		#self.take_screenshot()
		elem_3=browser.find_element_by_id("ff_submit_button")
		elem_3.click()
		time.sleep(15 * settings_dict['slowness_factor']) 
		#self.take_screenshot()		
		#now = datetime.datetime.now()
		#now_str=now.strftime("%m_%d_%Y")
		#my_log_dir =  "../crawl_logs/" + now_str
		#now_str=now.strftime("%H_%M_%S")
		#file_str= my_log_dir + "/" + COMPANY_NAME + "_"  + now_str + ".png"
		#browser.save_screenshot(file_str)
		
		bottom_buttons = browser.find_elements_by_xpath("//div[7]/div/div[2]/span/a")
		page_ct = len(bottom_buttons) - 2 
	
		for _page_ in range(page_ct):
			
			# if we want to look at the next page of results
			if _page_ > 0: 
				logger.info("Selecting next page...")
				bottom_buttons = browser.find_elements_by_xpath("//div[7]/div/div[2]/span/a")
				bottom_buttons[-1].click()
				time.sleep(5 * settings_dict['slowness_factor'])
			
			# parse entire table 
			logger.info("Parsing table...")
			text_html=browser.page_source.encode('utf-8')
			html_str=str(text_html)
			resp_for_scrapy=TextResponse('none',200,{},html_str,[],None)
			hxs=HtmlXPathSelector(resp_for_scrapy)
			table_rows = hxs.select("//*[@class='availability'] | //*[@class='availability last']")
			row_ct=len(table_rows)
			#self.take_screenshot()
			
			if row_ct == 0:
				msg="No data for this travel date"
				logger.info(msg)
				got_data_bool=True
			else:
				# we need to get at least one piece of data for the request to be deemed a success
				
				got_data_bool=False
				for x in xrange(row_ct):
					
					logger.debug("Executing row " + str(1 + x) + " of " + str(row_ct))
					
					cur_node_elements=table_rows[x]
					depart_and_arrive = cur_node_elements.select('.//span[@class="time_point"]')
					
					travel_time=cur_node_elements.select('.//div[@class="duration_data"]/text()')
					depart_time_num = depart_and_arrive[0].re("\d{1,2}\:\d\d")
					depart_time_sig = depart_and_arrive[0].re("[AP][M]")
					arrive_time_num = depart_and_arrive[1].re("\d{1,2}\:\d\d")
					arrive_time_sig = depart_and_arrive[1].re("[AP][M]")
					
					cost_str_array=cur_node_elements.select('.//span[@class="price"]').re("\d{1,3}\.\d\d")
					
					if len(cost_str_array)>0:
						cost_num_array=[int(float(number)) for number in cost_str_array]
						travel_price=min(cost_num_array)
					else:
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
							msg= "Cost: " + "$" + str(travel_price)
							logger.debug(msg)
							travel_price_sql=travel_price
							
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
						day_str=travel_time.re("(\d{1}) [Dd]")
						if bool(day_str):
							day_diff=int(day_str[0])
						else:
							day_diff=0 
							
						# now do arrive data
						hour_str=travel_time.re("(\d{1,2}) [Hh]")
						if bool(hour_str):
							hour_diff=int(hour_str[0])
						else:
							hour_diff=0
						
						minute_str=travel_time.re("(\d{1,2}) [Mm]")
						if bool(minute_str):
							minute_diff=int(minute_str[0])
						else:
							minute_diff=0 
							
						msg = "Days: " + str(day_diff) + "; hours: " + str(hour_diff) + "; minutes: " + str(minute_diff)
						logger.debug(msg)	
						
						trip_delta=timedelta(days=day_diff,hours=hour_diff,minutes=minute_diff)
						arrive_datetime=depart_datetime+trip_delta
						travel_obj=TravelContainer(COMPANY_NAME,depart_datetime,arrive_datetime,hour_diff,minute_diff,cityOrigin_tag,cityDeparture_tag,travel_price_sql)
						
						if settings_dict['include_database']:
							SQL_handle.update_table(travel_obj,browser.current_url)
							
						got_data_bool=True
						
					elif (bool(len(depart_time_sig))==False) or (bool(len(arrive_time_sig))==False):
						msg="Time signature missing!"
						logger.info(msg)
						continue
						
						
					elif (bool(len(depart_time_num))==False) or (bool(len(arrive_time_num))==False):
						msg="Actual times are missing!"
						logger.info(msg)
						continue	
						
					elif bool(len(travel_time)) == False:
						msg="Travel time is missing!"
						logger.info(msg)
						continue 
			
		if settings_dict['include_database'] and settings_dict['include_makeup']:
			msg= "Updating makeup table..."
			logger.info(msg)
			makeup_tr_obj=MakeupTravelContainer(COMPANY_NAME,date,cityOrigin_tag,cityDeparture_tag)
			SQL_handle.subtract_from_makeup(makeup_tr_obj)
					
		return True
		
if __name__ == "__main__":
	bs = MyCatcher(do_makeups=False,day_diff_array=[1])
	bs.iterate_jobs()
	#bs = MyCatcher(do_makeps=None)
	#bs.iterate_jobs()

