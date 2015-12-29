# coding=UTF-8
import time
import json
from slackclient import SlackClient
from difflib import SequenceMatcher as SM

from config import config


class Loke(object):
    def __init__(self):
        self.sc = None

    def handle_message(self, event):
        # Ignore own messages by bot
        if event['user'] == config['ownid']:
            return

        # Open file containing auto-responses
        with open(config['auto_response'], mode='r') as infile:
            responses = json.load(infile)

        # Loop through the dictionary from CSV file
        for response in responses:
            # Split the written message into a list (split by space)
            for word in event['text'].split():
                word = word.lower()
                if response['type'] == 'ratio':
                    #print word, response['key'], SM(None, word, response['key']).ratio()
                    match = SM(None, word, response['key']).ratio() > 0.85
                elif response['type'] == 'match':
                    match = response['key'] == word
                else:
                    match = False
                if match:
                    self.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'],
                            text=response['response'].encode('utf-8'))
                    break # Don't repeat same response for multiple hits

    def handle_presence_change(self, event):
        # See if a user in list travelers becomes available
        if event['user'] in config['list_travelers'] and event['presence'] == "active":
            self.sc.api_call("chat.postMessage", as_user="true:", channel=config['chan_general'], text='<@%s> is alive!! Skal han booke fly mon tro?!' % event['user'])

    def _get_today(self):
        now = time.time()
        return now - (now % (60*60*24))

    def init(self):
        self.sc = SlackClient(config['token'])
        if not self.sc.rtm_connect():
            raise SystemExit(1, "Connection Failed, invalid token?")
        return self

    def loop(self):
        while True:
            new_events = self.sc.rtm_read()
            for event in new_events:
                print event
                try:
                    if event['type'] == "message":
                        handle_message(event)

                    if event['type'] == "presence_change":
                        handle_presence_change(event)
                except KeyError:
                    # TODO(vegawe): When does this happen? Should not be necessary
                    print("Key not found in dict")
            time.sleep(1)

if __name__ == "__main__":
    Loke().init().main()
