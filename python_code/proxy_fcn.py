import urllib2
import re

URL_STR = []
URL_STR.append("http://buyproxies.org/panel/api.php?a=showProxies&pid=9699&key=e6ebe537191ed491c954d3101602cb2a")
URL_STR.append("http://buyproxies.org/panel/api.php?a=showProxies&pid=8295&key=e6ebe537191ed491c954d3101602cb2a")

def update_proxies():
	try:
		file_handle = open('proxy_lists/paid_proxies.txt','w')
		for url in URL_STR:
			html = urllib2.urlopen(url).read().decode('utf-8')
			file_handle.write(html)
			
		file_handle.close()
		return 1 
		
	except: 
		return 0

def get_proxies():
	file_handle=open('proxy_lists/paid_proxies.txt','r')
	text=file_handle.read()
	proxy_list=[]
	text_lines=re.split("\n+",text)
	for line in text_lines:
		if len(line)>2:
			cur_list=re.split(":",line)
			proxy_list.append(cur_list)
	return proxy_list
	

			
			
		
