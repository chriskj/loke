# coding=UTF-8
import time
import json
import re
import operator

from loke import LokeEventHandler

class SeenHandler(LokeEventHandler):
    def handler_version(self):
        return("Seen")

    def __init__(self, loke):
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: %s" % self.handler_version())

        self.presence_last_seen = {}

        with open(self.loke.config['last_seen'], mode='r') as infile:
            self.presence_last_seen = json.load(infile)

    def handle_message(self, event):
        # Capture last activity by user
        self.presence_last_seen[event['user']] = time.time()
        with open(self.loke.config['last_seen'], mode='w') as outfile:
            json.dump(self.presence_last_seen, outfile)

        # Trigger on call to .seen - requires that the user has been online since the bot was started
        seenmatch = re.match(r'\.seen <@(.*)>', event['text'], re.I)
        if seenmatch:
            userid = seenmatch.group(1)
            self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='<@%s> was last seen: %s' % (userid, time.strftime('%d %B %Y - %H:%M:%S', time.localtime(self.presence_last_seen[userid]))))
            return

        # Trigger on call to .seenall - List all "last seen" timestamps
        if event['text'] == '.seenall':
            response = ''
            sorted_response = sorted(self.presence_last_seen.items(), key=operator.itemgetter(1), reverse=True)
            #for key, value in self.presence_last_seen.iteritems():
            for key, value in sorted_response:
                response = '%s<@%s> - %s\n' % (response, key, time.strftime('%d %B %Y - %H:%M:%S', time.localtime(value)))
            self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='%s' % (response))
            return


    def handle_presence_change(self, event):
        user = event['user']
        # Capture last activity by user
        self.presence_last_seen[user] = time.time()
        with open(self.loke.config['last_seen'], mode='w') as outfile:
            json.dump(self.presence_last_seen, outfile)


    def handle_loop(self):
        return

