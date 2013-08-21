"""
This script was used to download zip files from my gmail containing proxy 
lists supplied by HideMyAss.com and then unzip them.  
"""

import email
import imaplib
import os
import glob
import zipfile
from MyController import BusCatcher

bus_catcher = BusCatcher()
bus_catcher.setup_my_logger(summary_only=True,logger_name="Proxy_loader")
my_logger = bus_catcher.my_logger

detach_dir = '.'
if 'attachments' not in os.listdir(detach_dir):
    os.mkdir('attachments')
 
proxy_dir = "./proxy_lists"
if not os.path.exists(proxy_dir):
    os.mkdir(proxy_dir)
 
userName = "buscatchers"
passwd = "whatismyusername"

def download_attachments():
    try:
        imapSession = imaplib.IMAP4_SSL('imap.gmail.com')
        typ, accountDetails = imapSession.login(userName, passwd)
        if typ != 'OK':
            my_logger.critical('Not able to sign in!')
            raise
        
        imapSession.select('[Gmail]/All Mail')
        typ, data = imapSession.search(None, 'ALL')
        if typ != 'OK':
            my_logger.critical('Error searching Inbox.')
            raise
        
        # Iterating over all emails
        for msgId in reversed(data[0].split()):
            typ, messageParts = imapSession.fetch(msgId, '(RFC822)')
            if typ != 'OK':
                my_logger.critical('Error fetching mail.')
                raise
    
            emailBody = messageParts[0][1]
            
            if not "Subject: ProxyList for Today" in emailBody:
                continue 
            
            mail = email.message_from_string(emailBody)
            for part in mail.walk():
                if part.get_content_maintype() == 'multipart':
                    # print part.as_string()
                    continue
                if part.get('Content-Disposition') is None:
                    # print part.as_string()
                    continue
                fileName = part.get_filename()
    
                if bool(fileName):
                    attach_dir = os.path.join(detach_dir,"attachments")
                    filePath = os.path.join(attach_dir, fileName)
                    
                    if not os.path.isfile(filePath):
                        my_logger.critical("Removing old proxies...")
                        old_proxy_zips = glob.glob(attach_dir + "/*.zip")
                        [os.remove(zip) for zip in old_proxy_zips]
                        
                        my_logger.critical("Saving new proxies: " + fileName)
                        fp = open(filePath, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()
                        
                    imapSession.close()
                    imapSession.logout()
                    return True 
                                        
        imapSession.close()
        imapSession.logout()
        return True 
        #cmd = "chmod -R 755 ./attachments"
        #os.system(cmd)
        
    except Exception as e:
        my_logger.exception(e)
        
def unzip_proxies():
    zip_file_list = glob.glob(os.path.join(detach_dir,'attachments') + "/*.zip")
    zip_file_list.sort(key=lambda x: os.path.getmtime(x))
    latest_zip = zip_file_list[-1] 
    my_logger.info("Unzipping new proxies: " + str(latest_zip))
    zipfile.ZipFile(latest_zip).extractall("./")

def main():
    download_attachments()
    unzip_proxies()

if __name__ == "__main__":
    main()

    
    
    