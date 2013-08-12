import urllib2
import re

def update_proxies():
	try:
		html = urllib2.urlopen("http://buyproxies.org/panel/api.php?a=showProxies&pid=8295&key=e6ebe537191ed491c954d3101602cb2a").read().decode('utf-8')
		proxy_count=len(re.findall('380rexmec',html))
		if proxy_count>5: 
			# checks that we have the right page 
			file_handle = open('proxy_lists/paid_proxies.txt','w')
			file_handle.write(html)
			return 1 
		else:
			return 0
		
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
	

			
			
		
