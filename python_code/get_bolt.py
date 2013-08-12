import random 
import datetime
from datetime import timedelta
import selenium
from MyController import BusCatcher
from MyDict import *
from MyCommon import *

COMPANY_NAME = "BoltBus"

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
		random.shuffle(bolt_trips)
		
		for day_diff in self.day_diff_array:
			time_delta=timedelta(days=day_diff)
			date_vector.append(now+time_delta)
			
		for date in date_vector:
			for cur_trip in bolt_trips:
				cur_job = self.MyJob(cur_trip,date)
				self.my_jobs.append(cur_job)
		
	def get_makeup_jobs(self):
		rows = self.sql_obj.retrieve_makeups(COMPANY_NAME)
		origin_to_destination_exact=[[trip[0],trip[1]] for trip in bolt_trips]
		for row in rows:
			try:
				cityOrigin_exact=row[2]
				cityDeparture_exact=row[3]
				date=row[4]
				trip_ind = origin_to_destination_exact.index([cityOrigin_exact,cityDeparture_exact])
				cur_trip = bolt_trips[trip_ind]
				cur_job = self.MyJob(cur_trip,date)
				self.my_jobs.append(cur_job)
			except ValueError:
				pass
					
	def my_fcn(self,browser,SQL_handle,job,logger):
		cur_trip = job.cur_trip
		date = job.date
		# _tag is just the city (no streets etc)
		cityOrigin=cur_trip[0]
		cityDeparture=cur_trip[1]
		cityOrigin_tag=cur_trip[2]
		cityDeparture_tag=cur_trip[3]
		logger.info("NEW SEARCH")
		time.sleep(4 * settings_dict['slowness_factor'])
	
		logger.info("Loading URL...")
		browser.get("http://www.boltbus.com")
		time.sleep(12 * settings_dict['slowness_factor'])
		
		cur_day=date.day
		cur_month=date.month
		cur_year=date.year
		cur_month_str=month_dict[int(cur_month)]
		date_str=date.strftime("%m/%d/%Y")
		msg="From " + cityOrigin + " to " + cityDeparture + " (" + date_str + ")"
		logger.debug(msg)
		
		# click on "region" tab
		logger.info("Clicking on region tab...")
		elem_0=browser.find_element_by_id("ctl00_cphM_forwardRouteUC_lstRegion_textBox")
		elem_0.click()
		time.sleep(1) 
	
		# select Northeast
		logger.info("Selecting northeast...")
		elem_1 = browser.find_element_by_id("ctl00_cphM_forwardRouteUC_lstRegion_repeater_ctl01_link")
		#elem_1=browser.find_element_by_partial_link_text("Northeast")
		elem_1.click()
		time.sleep(5 * settings_dict['slowness_factor'])
	
		# click on origin city
		logger.info("Clicking origin city...")
		elem_2=browser.find_element_by_id("ctl00_cphM_forwardRouteUC_lstOrigin_textBox")
		elem_2.click()
		time.sleep(1)
	
		# select origin city
		table = browser.find_element_by_id("ctl00_cphM_forwardRouteUC_lstOrigin_repeater")
		logger.info("Selecting origin city (" + cityOrigin + ")")
		elem_3 = table.find_elements_by_partial_link_text(cityOrigin)
		
		if not elem_3:
			logger.info("Unable to find origin city, continuing to next search")
			return True
		
		elem_3[0].click()
		time.sleep(5 * settings_dict['slowness_factor'])
	
		# click on destination city 
		logger.info("Clicking on destination city...")
		elem_4=browser.find_element_by_id("ctl00_cphM_forwardRouteUC_lstDestination_textBox")
		elem_4.click()
		time.sleep(1)
		
		# select destination city 
		table_2 = browser.find_element_by_id("ctl00_cphM_forwardRouteUC_lstDestination_repeater")
		logger.info("Selecting arrival city (" + cityDeparture + ")")
		elem_5 = table_2.find_elements_by_partial_link_text(cityDeparture)
		
		if not elem_5:
			logger.info("Unable to find origin city, continuing to next search")
			return True

		elem_5[0].click()
		time.sleep(5 * settings_dict['slowness_factor'])
	
		# click on travel date
		logger.info("Clicking on travel date...")
		travel_date_elem=browser.find_element_by_id("ctl00_cphM_forwardRouteUC_imageE")
		travel_date_elem.click()
		time.sleep(5 * settings_dict['slowness_factor'])
	
		# get calendar 
		# calendar=browser.find_element_by_class_name("calendar")
		# calendar=browser.find_element_by_xpath("//body/form/div[3]/div[2]/table/tbody/tr/td/div[2]/div[2]/div/table/tbody/tr/td/div/table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[2]/div/div/table")
		calendar=browser.find_element_by_id("ctl00_cphM_forwardRouteUC_calendar")
		time.sleep(1 * settings_dict['slowness_factor'])
		logger.info("Selecting current month...")
		# select current month 
		sel_month=calendar.find_element_by_class_name("title").text
		if not cur_month_str in sel_month: 
			nav_buttons=calendar.find_elements_by_class_name("nav")
			next_month_button=nav_buttons[2]
			
			for ind in xrange(1,12):
				next_month_button.click()
				time.sleep(3 * settings_dict['slowness_factor'])	
				#calendar=browser.find_element_by_class_name("calendar")
				sel_month=calendar.find_element_by_class_name("title").text
	
				if cur_month_str in sel_month: 
					break
		
		# select correct day
		logger.info("Selecting correct day...")
		calendar=browser.find_element_by_class_name("calendar")		
		days_boxes = calendar.find_elements_by_xpath("..//tbody/tr/td")
		
		if len(days_boxes)==0: 
			raise RuntimeError("Unable to locate days boxes!")
		
		ind_diff = 10 - int(days_boxes[10].text)
		cur_day_index=cur_day + ind_diff
		days_boxes[cur_day_index].click()
		time.sleep(7 * settings_dict['slowness_factor']) 
	
		# retrieve actual departure date from browser
		depart_date_elem=browser.find_element_by_id("ctl00_cphM_forwardRouteUC_txtDepartureDate")
		depart_date=str(depart_date_elem.get_attribute("value"))
	
		# parse entire table 
		logger.info("Parsing table...")
		text_html=browser.page_source.encode('utf-8')
		html_str=str(text_html)
		resp_for_scrapy=TextResponse('none',200,{},html_str,[],None)
		hxs=HtmlXPathSelector(resp_for_scrapy)
	
		table_rows=hxs.select('//tr[@class="fareviewrow"] | //tr[@class="fareviewaltrow"]')
		row_ct=len(table_rows)
	
		if row_ct == 0:
			msg="No data for this travel date"
			logger.info(msg)
			got_data_bool = True 
		else:
			# we need to get at least one piece of data for the request to be deemed a success
			got_data_bool=False
			for x in xrange(row_ct):
				cur_node_elements=table_rows[x]
				travel_price=cur_node_elements.select('.//td[contains(@class,"faresColumn0")]').re("\d{1,3}\.\d\d")
				depart_time_num=cur_node_elements.select('.//td[contains(@class,"faresColumn1")]').re("\d{1,2}\:\d\d")
				depart_time_sig=cur_node_elements.select('.//td[contains(@class,"faresColumn1")]').re("[AP][M]")
				arrive_time_num=cur_node_elements.select('.//td[contains(@class,"faresColumn2")]').re("\d{1,2}\:\d\d")
				arrive_time_sig=cur_node_elements.select('.//td[contains(@class,"faresColumn2")]').re("[AP][M]")
				
				bool_value=bool(len(depart_time_num) * len(depart_time_sig) * len(arrive_time_num) * len(arrive_time_sig))
				if bool_value == True:
					msg= "Depart date: " + depart_date
					logger.debug(msg)
					msg= "Depart time: " + depart_time_num[0] + " " + depart_time_sig[0]
					logger.debug(msg)	
					msg= "Arrive time: " + arrive_time_num[0] + " " + arrive_time_sig[0]
					logger.debug(msg)
					
					if len(travel_price)==0:
						msg="Ticket is sold out"
						logger.debug(msg)	
						travel_price_sql=None
					else:
						msg= "Cost: " + "$" + travel_price[0]
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
					
					# create arrive datetime object
					arrive_time_list=re.split(":",arrive_time_num[0])
					arrive_minute=int(arrive_time_list[1])
					pre_arrive_hour=int(arrive_time_list[0])
					
					if arrive_time_sig[0]=='AM':
						if pre_arrive_hour==12:
							arrive_hour=pre_arrive_hour-12
						else:
							arrive_hour=pre_arrive_hour
					elif arrive_time_sig[0]=='PM':
						if pre_arrive_hour==12:
							arrive_hour=pre_arrive_hour
						else:
							arrive_hour=pre_arrive_hour+12
						
					# need to check if we are in the next day (assumes no trips with hr > 24)
					if arrive_hour<depart_hour:
						arrive_day=cur_day+1
						total_min = 24*60.0 - (depart_hour*60.0 + depart_minute) + (arrive_hour*60.0 + depart_minute)
	
					else:
						arrive_day=cur_day
						total_min=(arrive_hour*60.0 + depart_minute) - (depart_hour*60.0 + depart_minute) 
					
					hour_diff=int(total_min/60.0) 
					minute_diff=int((total_min/60.0 - hour_diff)*60.0)
					trip_delta=timedelta(hours=hour_diff,minutes=minute_diff)
					arrive_datetime=depart_datetime+trip_delta
					travel_obj=TravelContainer(COMPANY_NAME,depart_datetime,arrive_datetime,hour_diff,minute_diff,cityOrigin_tag,cityDeparture_tag,travel_price_sql)
					
					if settings_dict['include_database']:
						SQL_handle.update_table(travel_obj,browser.current_url)
						
					got_data_bool=True
					
				elif (bool(len(depart_time_sig))==False) or (bool(len(arrive_time_sig))==False):
					msg="Time signature missing!"
					logger.debug(msg)
					continue
					
					
				elif (bool(len(depart_time_num))==False) or (bool(len(arrive_time_num))==False):
					msg="Actual times are missing!"
					logger.debug(msg)
					continue	
		
		# update makeup table
		if settings_dict['include_database'] and settings_dict['include_makeup']:
			msg= "Updating makeup table..."
			logger.info(msg)
			makeup_tr_obj=MakeupTravelContainer(COMPANY_NAME,date,cur_trip[0],cur_trip[1],cur_trip[-1])
			SQL_handle.subtract_from_makeup(makeup_tr_obj)
			
		return got_data_bool
		
if __name__ == "__main__":
	bs = MyCatcher(day_diff_array=[1])
	bs.iterate_jobs()
