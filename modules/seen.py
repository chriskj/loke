# coding=UTF-8
import time
import json
import re
import operator

from loke import LokeEventHandler

class SeenHandler(LokeEventHandler):
    # Capture and return information of when a user last was seen

    def handler_version(self):
        # Handler information
        return("Seen")

    def __init__(self, loke):
        # Initiate the handler
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: %s" % self.handler_version())

        self.presence_last_seen = {} # Dict to store key / value => user / datetime)

        # Load stored data from file
        with open(self.loke.config['last_seen'], mode='r') as infile:
            self.presence_last_seen = json.load(infile)

    def handle_message(self, event):
        # A message is recieved from Slack

        # Capture last activity by user when a message is written
        self.presence_last_seen[event['user']] = time.time()
        # Save data
        with open(self.loke.config['last_seen'], mode='w') as outfile:
            json.dump(self.presence_last_seen, outfile)

        # Trigger on call to .seen to list last time a user was seen
        seenmatch = re.match(r'\.seen <@(.*)>', event['text'], re.I)
        if seenmatch:
            userid = seenmatch.group(1)
            self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='<@%s> was last seen: %s' % (userid, time.strftime('%d %B %Y - %H:%M:%S', time.localtime(self.presence_last_seen[userid]))))
            return

        # Trigger on call to .seenall - List all "last seen" timestamps
        if event['text'] == '.seenall':
            response = ''
            sorted_response = sorted(self.presence_last_seen.items(), key=operator.itemgetter(1), reverse=True)
            for key, value in sorted_response:
                response = '%s<@%s> - %s\n' % (response, key, time.strftime('%d %B %Y - %H:%M:%S', time.localtime(value)))
            self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='%s' % (response))
            return


    def handle_presence_change(self, event):
        # A user changes state active/inactive

        user = event['user']
        # A user is active/inactive - hence the user has been seen
        self.presence_last_seen[user] = time.time()
        # Save data
        with open(self.loke.config['last_seen'], mode='w') as outfile:
            json.dump(self.presence_last_seen, outfile)


    def handle_loop(self):
        # handle_loop() is used by handlers to pick up data when it's not triggered by message og presence change (i.e. watch, countdowns++)
        return

