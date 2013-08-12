from itertools import izip, cycle
import os
import imaplib
import email
import getpass
import re
import mimetypes
import base64
import grp
import shutil
import time

pattern_uid = re.compile('\d+ \(UID (?P<uid>\d+)\)')

class pygmail:
    def __init__(self):
        self.IMAP_SERVER='imap.gmail.com'
        self.IMAP_PORT=993
        self.M = None
        self.response = None
        self.mailboxes = []

    def login(self, username, password):
        self.M = imaplib.IMAP4_SSL(self.IMAP_SERVER, self.IMAP_PORT)
        rc, self.response = self.M.login(username, password)
        return rc

    def logout(self):
        self.M.logout()

    def get_mailboxes(self):
        rc, self.response = self.M.list()
        for item in self.response:
            self.mailboxes.append(item.split()[-1])
        return rc

        #creating/renaming/deleting new mail folder
    def create_mailbox(self, mailbox):
        rc, self.response = self.M.create(mailbox)
        return rc

    def parse_uid(self, data):
        match = pattern_uid.match(data)
        return match.group('uid')

    def get_attachments(self):
        self.M.select()
        typ, data = self.M.search(None,"ALL")
        
        for num in data[0].split():
            typ_2, data_2 = self.M.fetch(num, '(RFC822)')
            mail = email.message_from_string(data[0][1])
            print 'Message %s\n%s\n' % (num, data_2[0][1])
            
            if not "Subject: ProxyList for Today" in data_2[0][1]:
                continue 
            
            for part in mail.walk():

                #if part.get_content_type() == 'text/plain':
                 #   body = "\n" + part.get_payload() + "\n"
                    
                #Check if its already there
                att_path = "./test_file.zip"
                if not os.path.isfile(att_path) :
                    fp = open(att_path, 'wb')
                    temp = part.get_payload(decode=True)
                    fp.write(temp)
                    fp.close()

                #cmd = "chmod -R 755 ."
                #os.system(cmd)

                file_type = part.get_content_type().split('/')[1]

                if not file_type:
                    file_type = 'jpg'

                filename = part.get_filename()

                print filename
            
        self.M.close()
        self.M.logout()

        #get the emails with attachments, create a folder, send them over
    def _get_attachments(self, folder='Inbox'):
        name_pat = re.compile('name=\".*\"')
        self.M.select(folder)
        subjectSearch = "Whiteboard Image -- Application in progress --"
        resp, data = self.M.search(None, '(UNSEEN SUBJECT "%s")' % subjectSearch)

        counter = 0
        detach_dir = '.'

        for num in data[0].split():
            resp, data = self.M.fetch(num, '(RFC822)')
            mail = email.message_from_string(data[0][1])
                        #self.M.store(num, '+FLAGS', r'(\Deleted)')

            # walk through individual mails, looking for attachment of JPG type
            for part in mail.walk():
                if part.is_multipart():
                        continue            

                if part.get_content_type() == 'text/plain':
                    body = "\n" + part.get_payload() + "\n"

                if part.get_content_maintype() != 'image':
                    continue

                file_type = part.get_content_type().split('/')[1]

                if not file_type:
                    file_type = 'jpg'

                filename = part.get_filename()

                if not filename:
                    filename = name_pat.findall(part.get('Content-Type'))[0][6:-1]

                print filename


                #PARSING BODY OF EMAIL
                destFolder  = albumHeader = ' '
                if body:
                    word_list = body.split()
                    for i in range(len(word_list)):
                        if word_list[i] == 'DestFolder:':
                            tmpWord = word_list[i].split(":")
                            destFolder = tmpWord[1]
                        elif word_list[i] == 'AlbumHeader:':
                            tmpWord = word_list[i].split(":")
                            folderFlag = word_list[i]


                #download the attachments from email to the designated directory
                att_path = os.path.join("./", filename)

                #Check if its already there
                if not os.path.isfile(att_path) :
                    fp = open(att_path, 'wb')
                    temp = part.get_payload(decode=True)
                    fp.write(temp)
                    fp.close()

                cmd = "chmod -R 755 ."
                os.system(cmd)

                counter = counter + 1


#MAIN PROGRAM
#login to email, print login status to terminal
g = pygmail()
g.login("buscatchers","findmybus")
g.get_attachments()
