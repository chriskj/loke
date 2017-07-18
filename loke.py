# coding=UTF-8
from slackclient import SlackClient

class Loke(object):
    def __init__(self, config):
        self.sc = None
        self.config = config

    def handle_message(self, event):
        return

    def handle_presence_change(self, event):
        return

    def init(self):
        self.sc = SlackClient(self.config['token'])
        if not self.sc.rtm_connect():
            raise SystemExit(1, "Connection Failed, invalid token?")
        return self

    #def loop(self):
    #    while True:
    #        new_events = self.sc.rtm_read()
    #        for event in new_events:
    #            print(event)
    #            try:
    #                if event['type'] == "message":
    #                    self.handle_message(event)

    #                if event['type'] == "presence_change":
    #                    self.handle_presence_change(event)
    #            except KeyError:
    #                # TODO(vegawe): When does this happen? Should not be necessary
    #                print("Key not found in dict")
    #                print(event)
    #        time.sleep(1)

#if __name__ == "__main__":
#    Loke().init().loop()
