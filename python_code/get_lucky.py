import random 
import datetime
from datetime import timedelta
import selenium
from MyController import BusCatcher
from MyDict import *
from MyCommon import *

COMPANY_NAME = "LuckyStar"

class MyCatcher(BusCatcher):
	def __init__(self,day_diff_array=[],do_makeups=False):
		BusCatcher.__init__(self,day_diff_array,COMPANY_NAME,do_makeups)
		self.prepare_for_launch()

	def get_makeup_tr_obj(self,job):
		#makeup_travel_container(company_name,date,cur_trip[0],cur_trip[1],cur_trip[-1])
		makeup_tr_obj = MakeupTravelContainer(COMPANY_NAME,job.date,job.cur_trip[0],job.cur_trip[1],job.cur_trip[-1])
		return makeup_tr_obj
		
	def get_regular_jobs(self):
		now = datetime.datetime.now()
		date_vector=[]
		random.shuffle(date_vector)
		random.shuffle(luckystar_trips)
		
		for day_diff in self.day_diff_array:
			time_delta=timedelta(days=day_diff)
			date_vector.append(now+time_delta)
		
		for date in date_vector:
			for cur_trip in luckystar_trips:
				cur_job = self.MyJob(cur_trip,date)
				self.my_jobs.append(cur_job)
		
	def get_makeup_jobs(self):
		rows = self.sql_obj.retrieve_makeups(COMPANY_NAME)
		origin_to_destination_exact=[[trip[0],trip[1]] for trip in luckystar_trips]

		for row in rows:
			try:
				cityOrigin_exact=row[2]
				cityDeparture_exact=row[3]
				date=row[4]
				trip_ind=origin_to_destination_exact.index([cityOrigin_exact,cityDeparture_exact])
				cur_trip = luckystar_trips[trip_ind]
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
		cityOrigin_tag=cur_trip[2]
		cityDeparture_tag=cur_trip[3]
		logger.info("NEW SEARCH")
		
		time.sleep(3 * settings_dict['slowness_factor']) 
		logger.info("Loading URL...")
		browser.get("http://www.luckystarbus.com/Purchase.aspx")
		time.sleep(5 * settings_dict['slowness_factor'])
		
		cur_day=date.day
		cur_month=date.month
		cur_year=date.year
		cur_month_str=month_dict[int(cur_month)]
		date_str=date.strftime("%m/%d/%Y")
		
		msg="From " + cityOrigin_tag + " to " + cityDeparture_tag + " (" + date_str + ")"
		logger.info(msg)
		
		# id: ctl00_MainContent_rbTripType_1
		logger.info("Clicking on one way button...")
		browser.find_element_by_id("ctl00_MainContent_rbTripType_1").click()
		time.sleep(5 * settings_dict['slowness_factor'])	
		
		logger.info("Clicking on origin city...")
		drop_down=browser.find_element_by_id("ctl00_MainContent_ddDepartureCity")
		drop_down_elements=drop_down.find_elements_by_xpath("./option")
		elements_str=[elem.text for elem in drop_down_elements]
		element_ind=elements_str.index(cityOrigin)
		drop_down_elements[element_ind].click()
		time.sleep(5 * settings_dict['slowness_factor'])
		
		msg="Clicking on destination city..."
		logger.info(msg)
		
		drop_down=browser.find_element_by_id("ctl00_MainContent_ddArrivalCity")
		drop_down_elements=drop_down.find_elements_by_xpath("./option")
		elements_str=[elem.text for elem in drop_down_elements]
		element_ind=elements_str.index(cityDeparture)
		drop_down_elements[element_ind].click()
		time.sleep(5 * settings_dict['slowness_factor'])
		
		msg="Typing departure date..."
		logger.info(msg)
		
		# NEED TO REMOVE OLD DATE STRING
		browser.find_element_by_id("ctl00_MainContent_sd").clear()
		time.sleep(3 * settings_dict['slowness_factor']) 
		browser.find_element_by_id("ctl00_MainContent_sd").send_keys(date_str)
		time.sleep(5 * settings_dict['slowness_factor']) 
		
		msg="Clicking on search button..."
		logger.info(msg)
	
		browser.find_element_by_id("ctl00_MainContent_btGo").click()
		time.sleep(8 * settings_dict['slowness_factor']) 
		
		# parse entire table 
		logger.info("Parsing table...")
		text_html=browser.page_source.encode('utf-8')
		html_str=str(text_html)
		resp_for_scrapy=TextResponse('none',200,{},html_str,[],None)
		hxs=HtmlXPathSelector(resp_for_scrapy)
		calendar=hxs.select('//table[@id="ctl00_MainContent_DepartureGrid"]')
		table_rows=calendar.select('.//tr')	
		row_ct=len(table_rows)		
	
		if row_ct == 0:
			msg="No data for this travel date"
			logger.info(msg)
			return True
		else:
			# we need to get at least one piece of data for the request to be deemed a success
			got_data_bool=False
			for x in xrange(row_ct):
			
				cur_node_elements=table_rows[x]
				
				depart_time_num=cur_node_elements.re("\d{1,2}\:\d\d")
				depart_time_sig=cur_node_elements.re("[AP][M]")
				travel_price=cur_node_elements.re("\d{1,3}\.\d\d")
				arrive_time_num=None
				arrive_time_sig=None			
	
				if len(travel_price)==0:
					travel_price=None
				
				bool_value=bool(bool(depart_time_num) * bool(depart_time_sig))
		
				if bool_value == True:
					msg= "Depart date: " + date_str
					logger.debug(msg)
					msg= "Depart time: " + depart_time_num[0] + " " + depart_time_sig[0]
					logger.debug(msg)	
	
					if bool(travel_price)==False:
						msg="Ticket is sold out"
						logger.info(msg)	
						travel_price_sql=None
					else:
						msg= "Cost: " + "$" + str(travel_price[0])
						logger.info(msg)
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
					
					# inputs are: (company_name,depart_datetime,arrive_datetime,hour_diff,minute_diff,depart_city,arrive_city,price)
					travel_obj=TravelContainer(COMPANY_NAME,depart_datetime,None,None,None,cityOrigin_tag,cityDeparture_tag,travel_price_sql)
					
					if settings_dict['include_database']:
						SQL_handle.update_table(travel_obj,browser.current_url)
										
				elif (bool(len(depart_time_sig))==False):
					msg="Time signature missing! Continue with next row"
					logger.info(msg)
					continue
					
					
				elif (bool(len(depart_time_num))==False):
					msg="Actual times are missing! Continue with next row"
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
	#bs = MyCatcher(do_makeups=None)
	bs.iterate_jobs()
	
	
