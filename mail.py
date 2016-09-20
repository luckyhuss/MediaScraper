# This program sends mail
# Author : Anwar Buchoo (luckyhuss@msn.com | http://ideaof.me)
# Date : 12/02/2016
# Version : 1.0

#https://docs.python.org/2/library/email-examples.html

# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import COMMASPACE, formatdate
from os.path import basename
import os

import utils
import mylogger
import database

def sendMail(_subject, _body, _attachment=""):
	# set start time
	startTimer = utils.startTimer()
	
	_from = database.getParam("SMTP.From")
	_to =  database.getParam("SMTP.To")	
	login = database.getParam("SMTP.Login")
	password = database.getParam("SMTP.Password")
	server = database.getParam("SMTP.Server")
	port = database.getParam("SMTP.Port")	

	# Create a multipart message
	msg = MIMEMultipart(
        From=_from,
        To=_to
    )

	msg['Subject'] = _subject

	msg.attach(MIMEText(_body))

	for f in os.listdir(utils.PATH_FILES):
		with open(os.path.normpath(utils.PATH_FILES + "/" + f), "r") as fil:
			msg.attach(MIMEApplication(
				fil.read(),
				Content_Disposition='attachment; filename="%s"' % f,
				Name=f
			))
	
	# Send the message via our own SMTP server, but don't include the
	# envelope header.
	server = smtplib.SMTP(server, int(port))
	
	#server.set_debuglevel(1)
	server.ehlo()
	server.starttls()	
	server.login(login, password)
	
	server.sendmail(_from, [_to], msg.as_string())
	server.quit()
	
	utils.info("{0} seconds to send email : {1}".format(utils.stopTimer(startTimer), _subject))