import random 
import datetime
from datetime import timedelta
import selenium
from MyController import BusCatcher
from MyDict import *
from MyCommon import *

COMPANY_NAME = "EasternTravel"

class MyCatcher(BusCatcher):
	def __init__(self,day_diff_array=[],do_makeups=False):
		BusCatcher.__init__(self,day_diff_array,COMPANY_NAME,do_makeups)
		self.prepare_for_launch()

	def get_makeup_tr_obj(self,job):
		makeup_tr_obj = MakeupTravelContainer(COMPANY_NAME,job.date,job.cur_trip[0],job.cur_trip[1],job.cur_trip[-1])
		return makeup_tr_obj
		
	def get_regular_jobs(self):
		now = datetime.datetime.now()
		date_vector=[]
		random.shuffle(date_vector)
		random.shuffle(eastern_trips)
		
		for day_diff in self.day_diff_array:
			time_delta=timedelta(days=day_diff)
			date_vector.append(now+time_delta)
		
		for date in date_vector:
			for cur_trip in eastern_trips:
				cur_job = self.MyJob(cur_trip,date)
				self.my_jobs.append(cur_job)
		
	def get_makeup_jobs(self):
		rows = self.sql_obj.retrieve_makeups(COMPANY_NAME)
		origin_to_destination_exact=[[trip[0],trip[1]] for trip in eastern_trips]
			
		for row in rows:
			try:
				cityOrigin_exact=row[2]
				cityDeparture_exact=row[3]
				date=row[4]
				trip_ind=origin_to_destination_exact.index([cityOrigin_exact,cityDeparture_exact])
				cur_trip = eastern_trips[trip_ind]
				cur_job = self.MyJob(cur_trip,date)
				self.my_jobs.append(cur_job)
			except ValueError as e:
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
	
		cur_day=date.day
		cur_month=date.month
		cur_year=date.year
		cur_month_str=month_dict[int(cur_month)]
		date_str = date.strftime("%m/%d/%Y")
		msg="From " + cityOrigin_tag + " to " + cityDeparture_tag + " (" + date_str + ")"
		logger.info(msg)
		
		time.sleep(5 * settings_dict['slowness_factor']) 
		logger.info("Loading URL...")
		browser.get("http://www.easternshuttle.com/")
		time.sleep(5 * settings_dict['slowness_factor'])
		
		msg="Clicking on origin city..."
		logger.info(msg)
		drop_down=browser.find_element_by_id("bus_from")
		drop_down_elements=drop_down.find_elements_by_xpath("./option")
		elements_str=[elem.text for elem in drop_down_elements]
		element_ind=elements_str.index(cityOrigin)
		drop_down_elements[element_ind].click()
		time.sleep(5 * settings_dict['slowness_factor'])
		
		msg="Clicking on destination city..."
		logger.info(msg)
		drop_down=browser.find_element_by_id("bus_to")
		drop_down_elements=drop_down.find_elements_by_xpath("./option")
		elements_str=[elem.text for elem in drop_down_elements]
		element_ind=elements_str.index(cityDeparture)
		drop_down_elements[element_ind].click()
		time.sleep(5 * settings_dict['slowness_factor'])
		
		# NEED TO ADD EXCEPTION IF CITY CANNOT BE FOUND !!!
		msg = "Entering departure date..."
		logger.info(msg)
		eastern_date_str = date.strftime("%Y-%m-%d")
		date_field = browser.find_element_by_name("filter_date")
		date_field.clear()
		date_field.send_keys(eastern_date_str)
		time.sleep(5 * settings_dict['slowness_factor'])
		
		logger.info("Clicking on Search button...")
		browser.find_element_by_id("search_submit").click()

		# parse entire table 
		logger.info("Parsing table...")
		text_html=browser.page_source.encode('utf-8')
		html_str=str(text_html)
		resp_for_scrapy=TextResponse('none',200,{},html_str,[],None)
		hxs = HtmlXPathSelector(resp_for_scrapy)
		table_rows = hxs.select("//form/div[3]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr")
		row_ct=len(table_rows)		
	
		if (row_ct < 2) or (row_ct % 2 != 0):
			msg="No data for this travel date or number of rows are uneven"
			logger.info(msg)
			return True 
		else:
			# we need to get at least one piece of data for the request to be deemed a success
			for x_half in xrange(row_ct / 2):
				x = int(2*x_half)
				cur_node_elements = table_rows[x]
				cur_node_str = cur_node_elements.extract() 
				time_matches = re.findall("(\d{1,2}\:\d\d)([ap][m])",cur_node_str)
				#logger.debug(cur_node_str)
				depart_time_num = time_matches[0][0] 
				depart_time_sig = time_matches[0][1] 
				arrive_time_num = time_matches[-1][0]
				arrive_time_sig = time_matches[-1][1]	
					
				cur_node_price_element_str = table_rows[x+1].extract()		
				travel_price_str = re.findall("(\$)(\d{1,2})(.\d{1,2}])?", cur_node_price_element_str)
								
				if not travel_price_str: 
					travel_price = None
				else: 			
					travel_price_str = travel_price_str[0]
					travel_price = travel_price_str[1]
					if len(travel_price_str) == 3: 
						travel_price += travel_price_str[2]
				
				bool_value = bool(bool(depart_time_num) * bool(depart_time_sig))
		
				if bool_value == True:
					msg= "Depart date: " + date_str
					logger.debug(msg)
					msg= "Depart time: " + depart_time_num + " " + depart_time_sig
					logger.debug(msg)	
					msg= "Arrive time: " + arrive_time_num + " " + arrive_time_sig
					logger.debug(msg)
					
					if bool(travel_price)==False:
						msg="Ticket is sold out"
						logger.info(msg)	
						travel_price_sql=None
					else:
						msg= "Cost: " + "$" + str(travel_price)
						logger.info(msg)
						travel_price_sql=int(float(travel_price))
						
					# create depart datetime object
					depart_time_list=re.split(":",depart_time_num)
					depart_minute=int(depart_time_list[1])
					pre_depart_hour=int(depart_time_list[0])
					
					if depart_time_sig=='am':
						if pre_depart_hour==12:
							depart_hour=pre_depart_hour-12
						else:
							depart_hour=pre_depart_hour
					elif depart_time_sig=='pm':
						if pre_depart_hour==12:
							depart_hour=pre_depart_hour
						else:
							depart_hour=pre_depart_hour+12
							
					depart_datetime=datetime.datetime(year=cur_year,month=cur_month,day=cur_day,hour=depart_hour,minute=depart_minute)
					
					arrive_time_list=re.split(":",arrive_time_num)
					arrive_minute=int(arrive_time_list[1])
					pre_arrive_hour=int(arrive_time_list[0])
					
					if arrive_time_sig=='am':
						if pre_arrive_hour==12:
							arrive_hour=pre_arrive_hour-12
						else:
							arrive_hour=pre_arrive_hour
					elif arrive_time_sig=='pm':
						if pre_arrive_hour==12:
							arrive_hour=pre_arrive_hour
						else:
							arrive_hour=pre_arrive_hour+12

					''' 
					TO DO: look for "next day" string 
					If it appears, make sure arrive datetime is the next day 
					'''
							
					if depart_time_sig == "pm" and arrive_time_sig == "am":
						arrive_day = cur_day + 1
					else:
						arrive_day = cur_day 
						
					arrive_datetime=datetime.datetime(year=cur_year,month=cur_month,day=arrive_day,hour=arrive_hour,minute=arrive_minute)
					time_delta = arrive_datetime - depart_datetime 
					total_seconds = time_delta.seconds + 3600.0 * 24.0 * time_delta.days
					hour_diff_pre = total_seconds/3600 
					hour_diff = int(hour_diff_pre)
					minute_diff = int(60 * (hour_diff_pre - hour_diff) )
					
					# inputs are: (company_name,depart_datetime,arrive_datetime,hour_diff,minute_diff,depart_city,arrive_city,price)
					travel_obj=TravelContainer(COMPANY_NAME,depart_datetime,arrive_datetime,hour_diff,minute_diff,cityOrigin_tag,cityDeparture_tag,travel_price_sql)
					
					if settings_dict['include_database']:
						SQL_handle.update_table(travel_obj,browser.current_url)
										
				elif (bool(len(depart_time_sig))==False):
					msg="Time of departure signature missing! Continue with next row"
					logger.info(msg)
					continue
					
				elif (bool(len(depart_time_num))==False):
					msg="Depart time num missing! Continue with next row"
					logger.info(msg)
					continue	
			
		if settings_dict['include_database'] and settings_dict['include_makeup']:
			msg= "Updating makeup table..."
			logger.info(msg)
			makeup_tr_obj=MakeupTravelContainer(COMPANY_NAME,date,cur_trip[0],cur_trip[1],cur_trip[-1])
			SQL_handle.subtract_from_makeup(makeup_tr_obj)
					
		return True
				
if __name__ == "__main__":
	bs = MyCatcher(day_diff_array=[1])
	#bs = MyCatcher(do_makeups=True)
	bs.iterate_jobs()
	
	
