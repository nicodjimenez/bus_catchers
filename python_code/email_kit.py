import smtplib
import datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os

gmail_user = "buscatchers@gmail.com"
gmail_pwd = "findmybus"

def mail(to, subject, text, attach):
   msg = MIMEMultipart()

   msg['From'] = gmail_user
   msg['To'] = to
   msg['Subject'] = subject

   msg.attach(MIMEText(text))

   #part = MIMEBase('application', 'octet-stream')
   #part.set_payload(open(attach, 'rb').read())
   #Encoders.encode_base64(part)
   #part.add_header('Content-Disposition',
   #'attachment; filename="%s"' % os.path.basename(attach))
   #msg.attach(part)

   mailServer = smtplib.SMTP("smtp.gmail.com", 587)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(gmail_user, gmail_pwd)
   mailServer.sendmail(gmail_user, to, msg.as_string())
   
   # Should be mailServer.quit(), but that crashes...
   
   mailServer.close()
   
def email_summary():
	
	now = datetime.datetime.now()
	now_str = now.strftime("%m_%d_%Y")
	my_log_dir =  "../crawl_logs/" + now_str
	file_str_summary = my_log_dir + "/SUMMARY.log"
	
	try:
		f=open(file_str_summary, 'r')
		msg = f.read()		
		subject_msg="Python daily report"
		mail("nicodjimenez@gmail.com",subject_msg,msg,None)
		f.close()
		
	except: 
		pass
	
if __name__ == "__main__":
	email_summary()
