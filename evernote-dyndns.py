from api_tokens import DEV_TOKEN

from evernote.api.client import EvernoteClient
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors

import socket
import xml.dom.minidom
import time
import urllib2
import re
from datetime import datetime

CLIENT_NAME 	= socket.gethostname()
IP_CHECK_URL 	= "http://checkip.dyndns.org"
SLEEP_TIME 		= 12*60*60 # 12 hours

GUID_FILE = 'noteguid.txt'

def createNoteXml():
	impl = xml.dom.minidom.getDOMImplementation()
	dt = impl.createDocumentType('en-note', '', "http://xml.evernote.com/pub/enml2.dtd")
	doc = impl.createDocument(None, 'en-note', dt)
	return doc
	
def getMyIp():
	data = urllib2.urlopen(IP_CHECK_URL).read()
	ip = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}.\d{1,3}", data)[0]
	return ip
	
def main():
	
	client = EvernoteClient(token=DEV_TOKEN)
	noteStore = client.get_note_store()
	
	try:
		with open(GUID_FILE, 'r') as guidfile:
			guid = guidfile.read().strip()
			note = noteStore.getNote(guid,True,False,False,False)
			dom = xml.dom.minidom.parseString(note.content)
	except IOError, Errors.EDAMNotFoundException:
		dom = createNoteXml()
		note = Types.Note()
		note.title = "evernote-dyndns for {client}".format(client=CLIENT_NAME)
		note.content = dom.toxml('utf-8')
		note = noteStore.createNote(note)
		
		with open(GUID_FILE, 'w') as guidfile:
			guidfile.write(note.guid)
	
	while True:
		try:
			now = datetime.now()
			nowStr = now.strftime("%Y-%m-%d %H:%M:%S")
			ip = getMyIp()
			
			print nowStr, "Update, current IP:", ip
			
			textNode = dom.createTextNode("{date} : {ip}".format(date=nowStr, ip=ip))
			dom.documentElement.appendChild(textNode)
		
			breakNode = dom.createElement('br')
			dom.documentElement.appendChild(breakNode)
			
			note.content = dom.toxml('utf-8')
			noteStore.updateNote(note)
			time.sleep(SLEEP_TIME)
			
		except KeyboardInterrupt as e:
			break
		except Exception as e:
			print "ERROR:", e
		
		
if __name__=="__main__":
	main()