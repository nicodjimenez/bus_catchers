=============
bus_catchers 
=============

bus_catchers" is a experimental web scraping suite to extract schedule data from the bus websites of Bolt Bus, Greyhound, Peterpan, Megabus, Amtrak, and more.  This is the code that allows http://www.buscatchers.com/ to work.  Although the source code is far from perfect, it is fully functional at the present time.  The plan is to develop a full fledged python framework for extracting data from any website, including websites that use javascript extensively. 

Source code uses Selenium + Firefox to navigate through the websites, and Scrapy to parse html.  The code has the following dependencies: 

Dependencies
-------------

1) **Selenium** 

A framework for controlling your browser, can be downloaded at: https://pypi.python.org/pypi/selenium

2) **Scrapy** 

A framework for web scraping and html parsing.  bus_catchers uses Scrapy's XLM parsing engine extensively.  You can downoad this at: https://pypi.python.org/pypi/Scrapy

3) **pyvirtualdisplay** (with Xvfb) (*optional, so that firefox runs in the background* )

A nice python module that will allow you to run Selenium scripts without having browsers popping up everywhere.  Can be downloaded at: https://pypi.python.org/pypi/PyVirtualDisplay

4) **python-MySQL** (*optional*) 

Allows you to execute mysql queries directly from python: https://pypi.python.org/pypi/MySQL-python

Description 
------------

Once dependencies are met the code can be run from the terminal as :: 

	RUN_ME.py medium all 

The "medium" input tells the program how many days in advance to scrape.  The "all" input tells the program to scrape all the websites concurrently.  Since there are 7 websites, this will suck up a lot of your memory! You can also run:: 

	RUN_ME.py medium 1 

which will only the first half of websites.  

The code supports the following features: 

1) Extensive logging, automatic emailing of log files (in the crawl_log directory)

2) Direct conversion from parsed html to MySQL insert statements (in the sql_files directory).  The way the code now works, is that it writes to .tmp files, and once the scripts are done running, the files are renamed as .sql files.  I then use a script (dump_sql.py) to import the .sql files. 

3) Proxy support.  That way if a site blocks you (this happens a lot with Peterpan) you can just switch to a new proxy and keep scraping.   

4) Parallel execution.  This aspect of the code is still in progress.  

The crontab file in the python_code directory shows how the scheduling is currently working online.  

Contact me at nicodjimenez@gmail.com if you have any questions / comments.  





