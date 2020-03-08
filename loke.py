# coding=UTF-8
import slack
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

    def handle_message(self, **payload):
        # A message is recieved from Slack
        event = payload['data']
        if event['text'] == '.modules':
            self.sc.chat_postMessage(
                 as_user="true:",
                 channel=event['channel'], 
                 text='*Loaded modules*\n%s' % ('\n'.join([' - %s' % (module.handler_version()) for module in self._handlers]))
             )

        for handler in self._handlers:
            handler.handle_message(event)

        return

    def handle_presence_change(self, **payload):
        event = payload['data']
        # A user changes state active/inactive
        for handler in self._handlers:
            handler.handle_presence_change(event)
        return

    def handle_hello(self, **payload):
        presence_sub_ids = []
        users = self.sc.api_call("users.list")
        
        for user in users['members']:
            presence_sub_ids.append(user['id'])
        
        presence_sub_json = {"type": "presence_sub", "ids": presence_sub_ids}
        self.rtmclient.send_over_websocket(payload=presence_sub_json)

    def init(self):
        # Initiate Slack connection
        self.rtmclient = slack.RTMClient(token=self.config['token'])
        self.sc = slack.WebClient(self.config['token'])
        return self

    def loop(self):
        # Main procedure
        while True:
            self.rtmclient.run_on(event='message')(self.handle_message)
            self.rtmclient.run_on(event='presence_change')(self.handle_presence_change)
            self.rtmclient.run_on(event='hello')(self.handle_hello)
            self.rtmclient.start()

            # except KeyError:
            #     # TODO(vegawe): When does this happen? Should not be necessary
            #     print("Key not found in dict")
            #     print(event)


            # if round(time.time()) % 10 == 0: # Run handle_loop() each 10 seconds
            #     for handler in self._handlers:
            #         handler.handle_loop()
            # time.sleep(1)

