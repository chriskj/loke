# coding=UTF-8
from slackclient import SlackClient
import time


class LokeEventHandler:
    # Class to check if handlers has the nescessary functions
    def handle_message(self, event):
        raise NotImplementedException()

    def handle_presence_change(self, event):
        raise NotImplementedException()

    def handle_loop(self):
        raise NotImplementedException()

class Loke(object):
    # Main bot object
    def __init__(self, config):
        self.sc = None # SlackClient
        self.config = config 
        self.presence_last_seen = {}
        self._handlers = [] # List of handlers

    def register_handler(self, handler): 
        #Function for the handlers to register themselves
        self._handlers.append(handler)

    def handle_message(self, event):
        # A message is recieved from Slack
        if event['text'] == '.modules':
            self.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='*Loaded modules*\n%s' % ('\n'.join([' - %s' % (module.handler_version()) for module in self._handlers])))
        return

    def handle_presence_change(self, event):
        # A user changes state active/inactive
        return

    def init(self):
        # Initiate Slack connection
        self.sc = SlackClient(self.config['token'])
        if not self.sc.rtm_connect():
            raise SystemExit(1, "Connection Failed, invalid token?")
        return self

    def loop(self):
        # Main procedure
        while True:
            new_events = self.sc.rtm_read() # Data from Slack
            for event in new_events:
                print(event) # Debug
                try:
                    if event['type'] == "message":
                        self.handle_message(event)
                        for handler in self._handlers:
                            handler.handle_message(event)

                    if event['type'] == "presence_change":
                        self.handle_presence_change(event)
                        for handler in self._handlers:
                            handler.handle_presence_change(event)

                except KeyError:
                    # TODO(vegawe): When does this happen? Should not be necessary
                    print("Key not found in dict")
                    print(event)


            if round(time.time()) % 10 == 0: # Run handle_loop() each 10 seconds
                for handler in self._handlers:
                    handler.handle_loop()
            time.sleep(1)

