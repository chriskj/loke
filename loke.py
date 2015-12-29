# coding=UTF-8
import time
import sqlite3
from slackclient import SlackClient
from difflib import SequenceMatcher as SM
from configobj import ConfigObj

config = ConfigObj('config.ini')
sc = SlackClient(config['token'])

if sc.rtm_connect():
	while True:
		new_events = sc.rtm_read()
		for event in new_events:
			
			# Respond to messages
			try:
				# Respond to messaged, bu ignore self
				if event['type'] == "message" and event['user'] != config['ownid']:
					# Split the written message into a list
					for word in event['text'].split():
						conn = sqlite3.connect(config['db'])
						db = conn.cursor()
						responses = db.execute('select * from auto_response order by key')
						# Loop through the dictionary provided in the beginning of file
						for key, response in responses:
							# Compare word to key from dictionary
							if SM(None, word.lower(), key).ratio() > 0.85:
								sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text=response.encode('utf-8'))
								print('SequenceMatch: %s - %s ratio: %s' % (word, key, SM(None, word.lower(), key).ratio()))
						conn.close()
			except KeyError:
				print("Key not found in dict")
		
			# See if a user becomes available
			try:
				# Dom't respond to own messages
				if event['type'] == "presence_change" and event['user'] in config['list_travelers'] and event['presence'] == "active":
					sc.api_call("chat.postMessage", as_user="true:", channel=config['chan_general'], text='<@%s> is alive!! Skal han booke fly mon tro?!' % event['user'])
			except KeyError:
				print("Key not found in dict")

			print event
		time.sleep(1)
else:
	print "Connection Failed, invalid token?"

