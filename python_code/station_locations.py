# contains bus station data

"""
0) Basic organizational plan

"stations" table:

id - int

name - string

address - string

coordinate - string

"routes" table:

origin - int (foreign key to stations table)

arrival - int(foreign key to stations table)

if arrival is 0, than arrival station can be used for any arrivals
if origin is 0, than origin station can be used for any trips, to any city
"""

station_list = []
station_list.append( (0,"BoltBus","New York", ) )
