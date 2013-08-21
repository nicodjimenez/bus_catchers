=============
bus_catchers 
=============

**bus_catchers** is a experimental web scraping suite to extract schedule data from the bus websites of Bolt Bus, Greyhound, Peterpan, Megabus, Amtrak, and more.  
This is the code that allowed http://www.buscatchers.com/ to work before it was shut down for legal reasons.  
Although the source code is fairly messy, it is fully functional at the present time.  
At some point, I would like to develop a python framework for extracting data from any website, including websites that use javascript extensively. 

The code uses Selenium + Firefox to navigate through the websites, and Scrapy to parse html.  The code has the following dependencies: 

Dependencies
-------------

1) **Selenium** 

A framework for controlling your browser, can be downloaded at: https://pypi.python.org/pypi/selenium

2) **Scrapy** 

A framework for web scraping and html parsing.  bus_catchers uses Scrapy's XML parsing engine extensively.  You can downoad this at: https://pypi.python.org/pypi/Scrapy

3) **pyvirtualdisplay** (with Xvfb) (*optional, so that firefox runs in the background* )

A nice python module that will allow you to run Selenium scripts without having browsers popping up everywhere.  Can be downloaded at: https://pypi.python.org/pypi/PyVirtualDisplay

4) **python-MySQL** (*optional*) 

Allows you to execute mysql queries directly from python: https://pypi.python.org/pypi/MySQL-python

Description 
------------

Once dependencies are met the code can be run from the terminal as :: 

	python RUN_ME.py short

The "short" input tells the program how many days in advance to scrape.  Warning: running this command will launch a web browser for each website to be scraped.  
This will be done using the multiprocessing python module to run the scripts in parallel.  

In order to try scraping a single website at a time, you may run the scraping scripts by themselves, as::
	
	python get_greyhound.py

or::

	python get_amtrack.py 
	
etc. 

The code supports the following features: 

1) Extensive logging, automatic emailing of log files (in the crawl_log directory)

2) 	Direct conversion from parsed html to MySQL insert statements (in the sql_files directory).  The outputs of the scripts are writtent to .sql files.  
	I then use a script (dump_sql.py) to import the .sql files and remove all the loaded queries from the .sql files.
	The script is run periodically at a schedule determined by the cron unix utility program.

3) Proxy support.  That way if a site blocks you (this happens a lot with Peterpan) you can just switch to a new proxy and keep scraping.   

4) Parallel execution.  This aspect of the code is still in progress.  

The crontab file in the python_code directory shows how the scheduling can be set up.  

Notes 
-------
The files need to be run from within the python_code directory, otherwise the outputs of the files 
will appear in the wrong directories.    

The outputs of the scripts are written to sql files with a random integer 1-5 in the file name.  The base 
file name of the output sql files is set by the :meth:`MyController.BusCatcher.setup_my_logger` method. 

The settings for the scraping are found in python_code/MyDict.py.  This file determines whether the scraping is done in the background using pyvirtualdisplay,
how fast the scraping happens, etc.  

Contact me at nicodjimenez [at] gmail.com if you have any questions / comments.  





