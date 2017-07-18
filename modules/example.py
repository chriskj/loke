# coding=UTF-8
from loke import LokeEventHandler

class ExampleHandler(LokeEventHandler):
    def handler_version(self):
        return("Seen")

    def __init__(self, loke):
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: %s" % self.handler_version())

    def handle_message(self, event):
        return

    def handle_presence_change(self, event):
        return
