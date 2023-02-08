
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os 
import ssl
import smtplib
import datetime 
import logging
import logging.handlers

import pathlib
'''----------------------------------------------------------------------------------------------'''

if os.name == 'posix':
    path = pathlib.PurePosixPath(os.path.abspath(__file__)).parent 
    if 'Forex_experiments' in path.parts:
        path = path.parent / str(datetime.date.today())
    else:
        path = path / 'Forex_experiments'  / str(datetime.date.today())
    # After this, path is equals to current date folder
    file_path = pathlib.PurePosixPath(os.path.abspath(__file__))
else:
    path = pathlib.PureWindowsPath(os.path.abspath(__file__)).parent 
    if 'Forex_experiments' in path.parts:
        path = path.parent / str(datetime.date.today())
    else:
        path = path / 'Forex_experiments'  / str(datetime.date.today())
    # After this, path is equals to current date folder
    file_path = pathlib.PureWindowsPath(os.path.abspath(__file__))
'''----------------------------------------------------------------------------------------------'''
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
"""StreamHandler"""
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG) 
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
"""FileHandler"""
rotatingfile_handler = logging.handlers.RotatingFileHandler(path.parent/'main.log', backupCount=5, maxBytes=1073741824)
rotatingfile_handler.setLevel(logging.DEBUG)
rotatingfile_handler.setFormatter(formatter)
logger.addHandler(rotatingfile_handler)

'''----------------------------------------------------------------------------------------------'''

def checkInternetRequests(url='https://api.ipify.org', timeout=3):
    while True:
        try:
            #r = requests.get(url, timeout=timeout)
            r = requests.head(url)
            return True
        except requests.ConnectionError as ex:
            logger.warning(str(ex))
            logger.warning('No internet ' + str(datetime.today()))



def email(x, subj = 'New public IP'):
    try:
        gmail_user = 'ww.bingonemo@gmail.com'
        gmail_password = '47UFjqTQ5fRMxd'
        sent_from = gmail_user
        to = [gmail_user,]
        subject = subj
        body = "{0}: {1}".format(subj, x)
        email_text = """\
            From: %s
            To: %s
            Subject: %s

            %s
            """ % (sent_from, ", ".join(to), subject, body)
        message = MIMEMultipart()
        message['From'] = sent_from
        message['To'] = sent_from
        message['Subject'] = subj
    	#The body and the attachments for the mail
        message.attach(MIMEText(email_text, 'plain'))
        context = ssl.create_default_context()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls(context=context)
        server.login(gmail_user, gmail_password)
        text = message.as_string()
        server.sendmail(sent_from, to, text)
        logger.info('Mail sent '+subj)
    	# print('Mail sent')
        server.close()
    except Exception as e:
        logger.warning('Email went wrong...')
        logger.warning(e)
        checkInternetRequests()

