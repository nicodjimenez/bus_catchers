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
		# ++++++++++++++++ REPLACE HERE +++++++++++++++++++
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
		
		# ++++++++++++++++ REPLACE HERE +++++++++++++++++++	
		for date in date_vector:
			for cur_trip in bolt_trips:
				cur_job = self.MyJob(cur_trip,date)
				self.my_jobs.append(cur_job)
		
	def get_makeup_jobs(self):
		if (settings_dict['include_makeup'] == False) or (settings_dict['include_database'] == False) or not (self.sql_obj):
			self.my_logger.info("Set include_makeup to True and include_database to True!")
			return 
	
		rows = self.sql_obj.retrieve_makeups(COMPANY_NAME)
		
		# ++++++++++++++++ REPLACE HERE +++++++++++++++++++
		origin_to_destination_exact=[[trip[0],trip[1]] for trip in bolt_trips]
		for row in rows:
			cityOrigin_exact=row[2]
			cityDeparture_exact=row[3]
			date=row[4]
			origin_to_destination_exact.index([cityOrigin_exact,cityDeparture_exact])
			cur_trip = bolt_trips[trip_ind]
			cur_job = self.MyJob(cur_trip,date)
			self.my_jobs.append(cur_job)

	# ++++++++++++++++ REPLACE HERE +++++++++++++++++++				
	def my_fcn(self,browser,SQL_handle,job,logger):
		cur_trip = job.cur_trip
		date = job.date
