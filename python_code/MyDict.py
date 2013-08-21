"""
This file contains all runtime settings for the scrapers. 

It also contains the data that we wish to scrape. 
"""

import logging

settings_dict = {
				# whether we have a proxy setup
				'include_proxies': False,\
				# do we use pyvirtualdisplay
				'hide_browser': False,\
				# do we save the outputs of the sql series to a file?
				'include_database':True,\
				# only applicable if using proxies
				'include_root_ip': True,\
				# do we save a todo list of trips in a makeups database table?
				'include_makeup': False,\
				'log_level': logging.INFO,\
				# time out for get url requests
				'default_timeout': 200,\
				# onlu applicable when proxies are being used, failed requests before proxy switch
				'min_req_per_proxy': 25,\
				'max_tries': 4,\
				'num_processes': 3,\
				'slowness_factor': 2,\
				'repeats_per_browser':2, 
				'log_creds': ['localhost','bestca12_rider','theleonius','bestca12_bus_schedules']}

month_dict = { \
 1: 'January', \
 2: 'February', \
 3: 'March', \
 4: 'April', \
 5: 'May', \
 6: 'June', \
 7:'July', \
 8: 'August', \
 9:'September', 10:'October', 11:'November', 12:'December'}

BusID_dict = { \
 'BoltBus': '00', \
 'Greyhound': '01',\
 'Megabus': '02',\
 'Peterpan': '03',\
 'LuckyStar': '04',\
 'GoBus': '05',\
 'FungWah':'06',\
 'Amtrak': '07',\
 'EasternTravel':'08'}

CityID_dict = { \
'Atlantic City, NJ':'12',\
'Baltimore, MD': '00',\
'Boston, MA': '01', \
'Chicago, IL': '02',\
'Cleveland, OH': '03',\
#'Detroit, MI': '04',\
'Hartford, CT': '15',\
#'Milwaukee, WI':'05',\
'Newark, NJ': '06', \
'New York, NY': '07', \
'New Haven, CT': '13', \
'Philadelphia, PA': '08',\
'Providence, RI': '14',\
'Pittsburgh, PA': '09',\
'Virginia Beach, VA': '10',\
'Washington, DC': '11'}

paid_proxy_list = [\
('173.0.58.24',80,'380rexmec','1a2b3c4d1380'),\
('23.19.132.189',80,'380rexmec','1a2b3c4d1380'),\
('199.180.132.2',80,'380rexmec','1a2b3c4d1380'),\
('50.115.165.108',80,'380rexmec','1a2b3c4d1380'),\
('23.19.189.111',80,'380rexmec','1a2b3c4d1380'),\
('23.19.132.39',80,'380rexmec','1a2b3c4d1380'),\
('23.19.132.17',80,'380rexmec','1a2b3c4d1380'),\
('23.19.132.82',80,'380rexmec','1a2b3c4d1380'),\
('108.178.2.28',80,'380rexmec','1a2b3c4d1380'),\
('108.178.2.27',80,'380rexmec','1a2b3c4d1380')]

fungwah_trips = [\
['Boston - New York','Boston, MA','New York, NY','01'],\
['New York - Boston','New York, NY','Boston, MA','02']]

gobus_trips = [\
['Cambridge','Manhattan','Boston, MA','New York, NY','01'],\
['Manhattan','Cambridge','New York, NY','Boston, MA','02']]

luckystar_trips = [\
['Boston, MA','New York City, NY','Boston, MA','New York, NY','01'],\
['New York City, NY','Boston, MA','New York, NY','Boston, MA','02']]

megabus_trips = [\
['Baltimore, MD','New York, NY','01'],\
['Baltimore, MD','Boston, MA','02'],\
['Baltimore, MD','Philadelphia, PA','03'],\
['Baltimore, MD','Washington, DC','04'],\
['Boston, MA','Baltimore, MD','05'],\
#['Boston, MA','Hartford, CT','06'],\
#['Boston, MA','New Haven, CT','07'],\
['Boston, MA','New York, NY','08'],\
['Boston, MA','Philadelphia, PA','09'],\
['Boston, MA','Washington, DC','10'],\
#['Hartford, CT','Boston, MA','11'],\
#['Hartford, CT','New Haven, CT','12'],\
#['Hartford, CT','New York, NY','13'],\
#['New Haven, CT','Boston, MA','14'],\
#['New Haven, CT','New York, NY','15'],\
['New York, NY','Atlantic City, NJ','16'],\
['New York, NY','Baltimore, MD','17'],\
['New York, NY','Boston, MA','18'],\
#['New York, NY','Hartford, CT','19'],\
#['New York, NY','New Haven, CT','20'],\
['New York, NY','Philadelphia, PA','21'],\
#['New York, NY','Pittsburgh, PA','22'],\
#['New York, NY','Providence, RI','23'],\
['New York, NY','Washington, DC','24'],\
['Philadelphia, PA', 'Baltimore, MD','25'],\
['Philadelphia, PA', 'Boston, MA','26'],\
['Philadelphia, PA', 'New York, NY','27'],\
#['Philadelphia, PA', 'Pittsburgh, PA','28'],\
['Philadelphia, PA', 'Washington, DC','29'],\
#['Providence, RI', 'New York, NY','30'],\
['Washington, DC', 'Baltimore, MD','31'],\
['Washington, DC', 'Boston, MA','32'],\
['Washington, DC', 'New York, NY','33'],\
['Washington, DC', 'Philadelphia, PA','34'],\
#['Washington, DC', 'Pittsburgh, PA','35']]
]

peterpan_trips = [\
['Baltimore, MD','New York, NY','01'],\
['Baltimore, MD','Boston, MA','02'],\
#['Baltimore, MD','New Haven, CT','03'],\
['Baltimore, MD','Washington, DC','04'],\
#['Baltimore, MD','Providence, RI','05'],\
#['Baltimore, MD','Hartford, CT','06'],\
['Boston, MA','Baltimore, MD','07'],\
#['Boston, MA','Hartford, CT','08'],\
#['Boston, MA','New Haven, CT','09'],\
['Boston, MA','New York, NY','10'],\
['Boston, MA','Newark, NJ','11'],\
['Boston, MA','Philadelphia, PA','12'],\
['Boston, MA','Washington, DC','13'],\
#['Boston, MA','Providence, RI','14'],\
#['Hartford, CT','Baltimore, MD','15'],\
#'Hartford, CT','Boston, MA','16'],\
#['Hartford, CT','New Haven, CT','17'],\
#['Hartford, CT','New York, NY','18'],\
#['Hartford, CT','Providence, RI','19'],\
#['New Haven, CT','Baltimore, MD','20'],\
#['New Haven, CT','Boston, MA','21'],\
#['New Haven, CT','New York, NY','22'],\
#['New Haven, CT','Baltimore, MD','23'],\
['New York, NY','Baltimore, MD','24'],\
#['New York, NY','Hartford, CT','25'],\
#['New York, NY','New Haven, CT','26'],\
['New York, NY','Philadelphia, PA','27'],\
['New York, NY','Washington, DC','28'],\
#['New York, NY','Providence, RI','29'],\
['New York, NY','Boston, MA','30'],\
['Newark, NJ','Boston, MA','31'],\
#['Newark, NJ','Providence, RI','32'],\
['Philadelphia, PA', 'New York, NY','33'],\
['Philadelphia, PA', 'Boston, MA','34'],\
#['Providence, RI', 'Boston, MA','35'],\
#['Providence, RI', 'Baltimore, MD','36'],\
#['Providence, RI', 'Hartford, CT','37'],\
#['Providence, RI', 'Newark, NJ','38'],\
#['Providence, RI', 'New York, NY','39'],\
#['Providence, RI', 'Washington, DC','40'],\
['Washington, DC', 'Baltimore, MD','41'],\
['Washington, DC', 'Boston, MA','42'],\
['Washington, DC', 'New York, NY','43'],\
#['Washington, DC', 'Providence, RI','44'],\
#['New York, NY','Newark, NJ','24'],\
]

# format is: 
# specific origin, specific destination, general origin, general destination, trip ID 
bolt_trips = [\
['Baltimore', 'New York','Baltimore, MD','New York, NY','24'],\
['Baltimore', 'Newark', 'Baltimore, MD','Newark, NJ','01'],\
['Boston', 'New York', 'Boston, MA', 'New York, NY', '02'],\
['Boston', 'Newark', 'Boston, MA','Newark, NJ','03'],\
['Boston', 'Philadelphia','Boston, MA','Philadelphia, PA','04'],\
['New York 33rd','Baltimore','New York, NY','Baltimore, MD','05'],\
['New York 33rd','Washington','New York, NY','Washington, DC','06'],\
['New York 34th','Boston','New York, NY','Boston, MA','07'],\
['New York 34th','Philadelphia - Cherry','New York, NY','Philadelphia, PA','08'],\
['New York 34th','Philadelphia JFK','New York, NY', 'Philadelphia, PA','09'],\
['New York 6th','Philadelphia JFK','New York, NY', 'Philadelphia, PA','10'],\
['New York 6th','Washington','New York, NY', 'Washington, DC','11'],\
['Newark','Baltimore','Newark, NJ','Baltimore, MD','12'],\
['Newark','Boston','Newark, NJ','Boston, MA','13'],\
['Newark','Philadelphia','Newark, NJ','Philadelphia, PA','14'],\
['Newark','Washington','Newark, NJ','Washington, DC','15'],\
['Philadelphia - Cherry','New York 34th','Philadelphia, PA','New York, NY','16'],\
['Philadelphia JFK','Boston','Philadelphia, PA','Boston, MA','17'],\
['Philadelphia JFK','New York 34th','Philadelphia, PA','New York, NY','18'],\
['Philadelphia JFK','New York 6th','Philadelphia, PA','New York, NY','19'],\
['Philadelphia JFK','Newark','Philadelphia, PA','Newark, NJ','20'],\
['Washington','New York 33rd','Washington, DC','New York, NY','21'],\
['Washington','New York 6th','Washington, DC','New York, NY','22'],\
['Washington','Newark','Washington, DC','Newark, NJ','23']]
#('New York 6th','Philadelphia - Cherry','New York','Philadelphia',0,5)
#('Philadelphia - Cherry','New York 6th',0,5),\

greyhound_cities=[\
#['Atlantic City, NJ','Atlantic City, NJ'],\
['Baltimore Downtown, MD','Baltimore, MD'],\
['Boston, MA', 'Boston, MA'],\
#['Hartford, CT','Hartford, CT'],\
#['New Haven, CT', 'New Haven, CT'],\
['New York, NY','New York, NY'],\
['Newark, NJ','Newark, NJ'],\
['Philadelphia, PA','Philadelphia, PA'],\
#['Providence, RI', 'Providence, RI'],\
#['Pittsburgh, PA','Pittsburgh, PA'],\
#['Virginia Beach, VA','Virginia Beach, VA'],\
['Washington, DC','Washington, DC']]

#['Cleveland, OH','Cleveland, OH']]
#['Milwaukee, WI','Milwaukee, WI'],\
#['Chicago, IL','Chicago, IL'],\
#['Detroit, MI','Detroit, MI'],\

amtrack_cities=[\
#['Atlantic City, NJ','Atlantic City, NJ'],\
['Baltimore - Penn Station, MD (BAL)','Baltimore, MD'],\
['Boston - South Station, MA (BOS)', 'Boston, MA'],\
#['Hartford, CT','Hartford, CT'],\
#['New Haven, CT', 'New Haven, CT'],\
['New York - Penn Station, NY (NYP)','New York, NY'],\
['Newark, NJ (NWK)','Newark, NJ'],\
['Philadelphia - 30th Street Station, PA (PHL)','Philadelphia, PA'],\
#['Providence, RI', 'Providence, RI'],\
#['Pittsburgh, PA','Pittsburgh, PA'],\
#['Virginia Beach, VA','Virginia Beach, VA'],\
['Washington - Union Station, DC (WAS)','Washington, DC']]

eastern_trips = [\
['Baltimore, MD','New York, NY'],\
['New York, NY','Baltimore, MD'],\
#['New York, NY','Richmond, VA'],\
#['New York, NY','Rockville'', MD'],\
['New York, NY','Washington, DC'],\
['Washington, DC','New York, NY']]

ct = 0
for elem in eastern_trips:
	elem.append(str(ct))
	ct += 1 
	
if __name__ == '__main__':
	print settings_dict 

