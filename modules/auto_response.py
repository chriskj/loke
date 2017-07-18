# coding=UTF-8
import json
from difflib import SequenceMatcher as SM # Used to compare words that looks the same

from loke import LokeEventHandler

class AutoResponseHandler(LokeEventHandler):
    # Handler to react to certain words written to channel

    def handler_version(self):
        # Handler information
        return("AutoResponse")

    def __init__(self, loke):
        # Initiate the handler
        self.loke = loke
        self.loke.register_handler(self)

        print("Loading module: %s" % self.handler_version())

    def handle_message(self, event):
        # A message is recieved from Slack

        # Ignore own events
        if event['user'] == self.loke.config['ownid']:
            return

        # Open file containing auto-responses
        with open(self.loke.config['auto_response'], mode='r') as infile:
            responses = json.load(infile)

        # Loop through the dictionary of words
        for response in responses:
            # Split the written message into a list (split by space)
            for word in event['text'].split():
                word = word.lower().strip('\r\t\n,.')
                if response['type'] == 'ratio': # ratio means no exact match is required - SM ratio is threshold
                    match = SM(None, word, response['key']).ratio() > 0.85
                elif response['type'] == 'equal': # exact match is required
                    match = response['key'] == word
                else:
                    match = False
                if match:
                    self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text=response['response'])
                    break # Don't repeat same response for multiple hits on same word

    def handle_presence_change(selv, event):
        # A user changes state active/inactive
        return

    def handle_loop(self):
        # handle_loop() is used by handlers to pick up data when it's not triggered by message og presence change (i.e. watch, countdowns++)
        return

