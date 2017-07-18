# coding=UTF-8
import json
from difflib import SequenceMatcher as SM

from loke import LokeEventHandler

class AutoResponseHandler(LokeEventHandler):
    def handler_version(self):
        return("AutoResponse")

    def __init__(self, loke):
        self.loke = loke
        self.loke.register_handler(self)

        print("Loading module: %s" % self.handler_version())

    def handle_message(self, event):
        # Ignore own events
        if event['user'] == self.loke.config['ownid']:
            return

        # Open file containing auto-responses
        with open(self.loke.config['auto_response'], mode='r') as infile:
            responses = json.load(infile)

        # Loop through the dictionary from CSV file
        for response in responses:
            # Split the written message into a list (split by space)
            for word in event['text'].split():
                word = word.lower().strip('\r\t\n,.')
                if response['type'] == 'ratio':
                    #print response['key'], word, SM(None, word, response['key']).ratio()
                    match = SM(None, word, response['key']).ratio() > 0.85
                elif response['type'] == 'equal':
                    #print response['key'], word, response['type'] == 'equal'
                    match = response['key'] == word
                else:
                    match = False
                if match:
                    self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'],
                            text=response['response'])
                    break # Don't repeat same response for multiple hits

    def handle_presence_change(selv, event):
        return

    def handle_loop(self):
        return

