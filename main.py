# coding=UTF-8

from config import config

from loke import Loke
from seen import SeenLoke

import time

Loke = Loke(config).init()

while True:
    new_events = Loke.sc.rtm_read()
    for event in new_events:
        print(event)
        try:
            if event['type'] == "message":
                Loke.handle_message(event)

            if event['type'] == "presence_change":
                Loke.handle_presence_change(event)
        except KeyError:
            # TODO(vegawe): When does this happen? Should not be necessary
            print("Key not found in dict")
            print(event)
    time.sleep(1)

#if __name__ == "__main__":
#    Loke().init().loop()
