from traceback import print_exc
import logging 
logging.basicConfig(filename='example.log')
try: 
	1/0
except ZeroDivisionError as e: 
	logging.exception(e)
	pass
except Exception as e: 
	logging.exception(e)
	pass
