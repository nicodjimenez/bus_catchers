import random 
import datetime
from datetime import timedelta
from MyController import BusCatcher
from MyDict import *
from MyCommon import *

COMPANY_NAME = "FungWah"

class MyCatcher(BusCatcher):
	def __init__(self,day_diff_array=[],do_makeups=False):
		BusCatcher.__init__(self,day_diff_array,COMPANY_NAME,do_makeups)
		self.prepare_for_launch()

	def get_makeup_tr_obj(self,job):
		makeup_tr_obj = MakeupTravelContainer(COMPANY_NAME,job.date,job.cur_trip[1],job.cur_trip[2],job.cur_trip[-1])
		return makeup_tr_obj

	def get_regular_jobs(self): 
		now = datetime.datetime.now()
		date_vector=[]
		random.shuffle(date_vector)
		random.shuffle(fungwah_trips)
		
		for day_diff in self.day_diff_array:
			time_delta=timedelta(days=day_diff)
			date_vector.append(now+time_delta)
			
		for date in date_vector:
			for cur_trip in fungwah_trips:
				cur_job = self.MyJob(cur_trip,date)
				self.my_jobs.append(cur_job)
				
	def get_makeup_jobs(self):
		rows = self.sql_obj.retrieve_makeups(COMPANY_NAME)
		origin_to_destination_exact=[[trip[1],trip[2]] for trip in fungwah_trips]
		for row in rows:
			try:
				cityOrigin_exact=row[2]
				cityDeparture_exact=row[3]
				date=row[4]
				trip_ind=origin_to_destination_exact.index([cityOrigin_exact,cityDeparture_exact])
				cur_trip = fungwah_trips[trip_ind]
				cur_job = self.MyJob(cur_trip,date)
				self.my_jobs.append(cur_job)
			except ValueError as e:
				pass

	def my_fcn(self,browser,SQL_handle,job,logger):	
		# *_tag is just the city name (no streets etc) that will be stored in the database
		cur_trip = job.cur_trip
		date = job.date
		cityRoute=cur_trip[0]
		cityOrigin_tag=cur_trip[1]
		cityDeparture_tag=cur_trip[2]
		logger.info("NEW SEARCH")
			
		time.sleep(3 * settings_dict['slowness_factor']) 
		logger.info("Loading URL...")
		
		if cityRoute == "New York - Boston": 
			browser.get("http://www.fungwahbus.com/Ticket.aspx?direction=NY2Boston")
		else:
			browser.get("http://www.fungwahbus.com/Ticket.aspx?direction=Boston2NY")
			
		time.sleep(5 * settings_dict['slowness_factor'])
		cur_day=date.day
		cur_month=date.month
		cur_year=date.year
		cur_month_str=month_dict[int(cur_month)]
		date_str=date.strftime("%m/%d/%Y")
		
		msg="From " + cityOrigin_tag + " to " + cityDeparture_tag + " (" + date_str + ")"
		logger.info(msg)
		
		# click on travel date
		logger.info("Clicking on travel date...")
		travel_date_elem=browser.find_element_by_class_name("dp-choose-date").click()
		time.sleep(7 * settings_dict['slowness_factor'])
	
		# get calendar 
		logger.info("Selecting current month...")
		calendar=browser.find_element_by_class_name("dp-calendar")
		sel_month=calendar.find_element_by_xpath('//div[@class="dp-popup"]/h2').text
		
		if not cur_month_str in sel_month: 
			next_month_button=browser.find_element_by_class_name("dp-nav-next-month")
			
			for ind in xrange(1,12):
				next_month_button.click()
				time.sleep(3 * settings_dict['slowness_factor'])	
				#calendar=browser.find_element_by_class_name("calendar")
				sel_month=calendar.find_element_by_xpath('//div[@class="dp-popup"]/h2').text

				if cur_month_str in sel_month: 
					break
		
		# select correct day
		logger.info("Selecting correct day...")
		calendar=browser.find_element_by_class_name("dp-calendar")		
		days_boxes = calendar.find_elements_by_xpath("..//tbody/tr/td")
		
		if len(days_boxes)==0: 
			raise RuntimeError("Unable to locate days boxes!")
		
		ind_diff = 15 - int(days_boxes[15].text)
		cur_day_index=cur_day + ind_diff
		days_boxes[cur_day_index].click()
		time.sleep(5 * settings_dict['slowness_factor']) 
		
		logger.info("Clicking on search button...")
		browser.find_element_by_xpath("//table/tbody/tr/td/p/table/tbody/tr[4]/td/table/tbody/tr/td/a/img").click()		
		time.sleep(8 * settings_dict['slowness_factor']) 
		
		# parse entire table 
		logger.info("Parsing table...")
		text_html=browser.page_source.encode('utf-8')
		html_str=str(text_html)
		resp_for_scrapy=TextResponse('none',200,{},html_str,[],None)
		hxs=HtmlXPathSelector(resp_for_scrapy)
		table_rows=hxs.select("//table//table/tbody/tr/td/form/table[3]/tbody/tr")
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
				depart_time_num=cur_node_elements.select("./td[2]").re("\d{1,2}\:\d\d")
				depart_time_sig=cur_node_elements.select("./td[2]").re("[APap][Mm]")
				travel_price=cur_node_elements.select("./td[3]").re("\d{1,3}\.\d\d")
												
				if len(travel_price)==0:
					travel_price=None
				
				bool_value=bool(bool(depart_time_num) * bool(depart_time_sig))
				
				if bool_value == True:
					msg= "Depart date: " + date_str
					logger.debug(msg)
					msg= "Depart time: " + depart_time_num[0] + " " + depart_time_sig[0]
					logger.debug(msg)		
					
					availability_str_raw = cur_node_elements.select("./td[5]").extract()
					availability_str_obj=re.search("[Bb][Uu][Yy]",availability_str_raw[0])
					
					if availability_str_obj:
						availability_str=availability_str_obj.group(0)
					else:
						availability_str=None
						
					if not bool(availability_str):
						logger.info("Could not find availability string")
						travel_price=None
					
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
					
					if depart_time_sig[0].upper()=='AM':
						if pre_depart_hour==12:
							depart_hour=pre_depart_hour-12
						else:
							depart_hour=pre_depart_hour
					elif depart_time_sig[0].upper()=='PM':
						if pre_depart_hour==12:
							depart_hour=pre_depart_hour
						else:
							depart_hour=pre_depart_hour+12
					
					depart_datetime=datetime.datetime(year=cur_year,month=cur_month,day=cur_day,hour=depart_hour,minute=depart_minute)
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
			makeup_tr_obj=MakeupTravelContainer(COMPANY_NAME,date,cityOrigin_tag,cityDeparture_tag,cur_trip[-1])
			SQL_handle.subtract_from_makeup(makeup_tr_obj)
					
		return True

if __name__ == "__main__":
	bs = MyCatcher(day_diff_array=[1])
	#bs = MyCatcher(do_makeups=None)
	bs.iterate_jobs()
	
	
