# coding=UTF-8
import time
import sqlite3
from slackclient import SlackClient
from difflib import SequenceMatcher as SM
from configobj import ConfigObj


def handle_message(config, sc, event):
    # Ignore own messages by bot
    if event['user'] == config['ownid']:
        return

    # Split the written message into a list (split by space)
    for word in event['text'].split():
        # Bad, temp solution. Need to persist the list after looping through.
        # Ideally list should be read once pr message (to ensure updates).
        # DB connection should also happen once, but this will lock the db-file.
        conn = sqlite3.connect(config['db'])
        db = conn.cursor()
        responses = db.execute('select * from auto_response order by key')
        # Loop through the dictionary from database
        for key, response in responses:
            # Compare word to key from dictionary
            if SM(None, word.lower(), key).ratio() > 0.85:
                sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text=response.encode('utf-8'))
                print('SequenceMatch: %s - %s ratio: %s' % (word, key, SM(None, word.lower(), key).ratio()))
        conn.close()

def handle_presence_change(config, sc, event):
    # See if a user in list travelers becomes available
    if event['user'] in config['list_travelers'] and event['presence'] == "active":
        sc.api_call("chat.postMessage", as_user="true:", channel=config['chan_general'], text='<@%s> is alive!! Skal han booke fly mon tro?!' % event['user'])

def main():
    config = ConfigObj('config.ini')
    sc = SlackClient(config['token'])
    if not sc.rtm_connect():
        print "Connection Failed, invalid token?"
        return

    while True:
        new_events = sc.rtm_read()
        for event in new_events:
            print event
            try:
                if event['type'] == "message":
                    handle_message(config, sc, event)

                if event['type'] == "presence_change":
                    handle_presence_change(config, sc, event)
            except KeyError:
                # TODO(vegawe): When does this happen? Should not be necessary
                print("Key not found in dict")
        time.sleep(1)

if __name__ == "__main__":
    main()
