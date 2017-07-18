# coding=UTF-8
from slackclient import SlackClient
import time

class LokeEventHandler:
    def handle_message(self, event):
        raise NotImplementedException()

    def handle_presence_change(self, event):
        raise NotImplementedException()

    def handle_loop(self):
        raise NotImplementedException()

class Loke(object):
    def __init__(self, config):
        self.sc = None
        self.config = config
        self.presence_last_seen = {}
        self._handlers = []

    def register_handler(self, handler):
        self._handlers.append(handler)

    def handle_message(self, event):
        if event['text'] == '.modules':
            self.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='*Loaded modules*\n%s' % ('\n'.join([' - %s' % (module.handler_version()) for module in self._handlers])))
        return

    def handle_presence_change(self, event):
        return

    def init(self):
        self.sc = SlackClient(self.config['token'])
        if not self.sc.rtm_connect():
            raise SystemExit(1, "Connection Failed, invalid token?")
        return self

    def loop(self):
        while True:
            new_events = self.sc.rtm_read()
            for event in new_events:
                print(event)
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
            #if round(time.time() % 10) == 0:
            for handler in self._handlers:
                handler.handle_loop()
            time.sleep(1)

