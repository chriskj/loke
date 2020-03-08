# coding=UTF-8
import json
import re
import requests
import xml.etree.ElementTree as ET

from loke import LokeEventHandler

class BrewHandler(LokeEventHandler):
    # Handler to store information of brews

    def handler_version(self):
        # Handler information
        return("Brew")

    def _show_brew(self, brew, event):
        if len(self.brews[brew]) > 0:
            attachment = [{
                "author_name": '%s - %s' % (self.brews[brew].get('name', 'No name'), self.brews[brew].get('brewdate', 'No date')),
                "author_icon": ':beers:',
                "fields": [
                ],
                "color": "#aaaaaa"
            }]

            attachment[0]['fields'].append({
                'title': 'Info',
                'value': '%s' % ('\n'.join(['%s :: %s' % (key, value) for (key, value) in sorted(self.brews[brew].items(), key=lambda x: x[0].lower()) if key != 'FG' and key != 'OG' and key != 'ABV' and key != 'gravity' and key != 'brewdate' and key != 'name' and key != 'files'])),
                'short': 'true'
            })

            attachment[0]['fields'].append({
                'title': 'Details',
                'value': '%s' % ('\n'.join(['%s :: %s' % (key, value) for (key, value) in sorted(self.brews[brew].items(), key=lambda x: x[0].lower()) if key == 'FG' or key == 'OG' or key == 'ABV' or (key == 'gravity' and len(value) > 2)])),
                'short': 'true'
            })

            self.loke.sc.chat_postMessage(as_user="true:", channel=event['channel'], attachments=json.dumps(attachment))

            if 'files' in self.brews[brew].keys():
                for fil in self.brews[brew]['files']:
                    filename = '%s%s-%s' % (self.loke.config['brewfiles'], brew, fil)
                    with open(filename, 'rb') as data:
                        res = self.loke.sc.files_upload(channels=event['channel'], filename=fil, file=data)

    def __init__(self, loke):
        # Initiate the handler
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: %s" % self.handler_version())

        # Open file containing brew-information
        with open(self.loke.config['brew'], mode='r') as infile:
            self.brews = json.load(infile)

    def handle_presence_change(self, event):
        # A user changes state active/inactive
        return

    def handle_message(self, event):
        # A message is recieved from Slack


        # Add gravity measure to brew. Trigger on call to 
        # .brew <date> gravity add <date> <gravity>
        brewmatch = re.match(r'\.brew (\d+) gravity add (\d{4}-\d{2}-\d{2}) (1\.\d{1,3})', event['text'], re.I)
        if brewmatch:
            if len(self.brews[brewmatch.group(1)]) > 0:
                self.brews[brewmatch.group(1)]['gravity'].append([brewmatch.group(2), brewmatch.group(3)]) # Add gravity information
                self.brews[brewmatch.group(1)]['OG'] = min(self.brews[brewmatch.group(1)]['gravity'])[1] # Calculate Original Gravity based on all gravities registered
                self.brews[brewmatch.group(1)]['FG'] = max(self.brews[brewmatch.group(1)]['gravity'])[1] # Calculate Final Gravity based on all gravities registered
                self.brews[brewmatch.group(1)]['gravity'].sort() # Convenience
                self.brews[brewmatch.group(1)]['ABV'] = "{0:.2f} %".format((float(self.brews[brewmatch.group(1)]['OG'])-float(self.brews[brewmatch.group(1)]['FG']))*float(131.25)) # Calculate Alcohol by Volume from OG/FG
                self._show_brew(brewmatch.group(1), event)
                # Save data
                with open(self.loke.config['brew'], mode='w') as outfile: 
                    json.dump(self.brews, outfile, sort_keys=True, indent=4)
            return

        # Delete gravity measure from brew. Trigger on call to 
        # .brew <date> gravity del <date>
        brewmatch = re.match(r'\.brew (\d+) gravity del (\d{4}-\d{2}-\d{2})', event['text'], re.I)
        if brewmatch:
            if len(self.brews[brewmatch.group(1)]) > 0:
                for date in self.brews[brewmatch.group(1)]['gravity']:
                    if date[0] == brewmatch.group(2):
                        self.brews[brewmatch.group(1)]['gravity'].remove(date) # Delete gravity information
                        self.brews[brewmatch.group(1)]['OG'] = min(self.brews[brewmatch.group(1)]['gravity'])[1] # Calculate Original Gravity based on all gravities registered
                        self.brews[brewmatch.group(1)]['FG'] = max(self.brews[brewmatch.group(1)]['gravity'])[1] # Calculate Final Gravity based on all gravities registered
                        self.brews[brewmatch.group(1)]['gravity'].sort() # Convenience
                        self.brews[brewmatch.group(1)]['ABV'] = "{0:.2f} %".format((float(self.brews[brewmatch.group(1)]['OG'])-float(self.brews[brewmatch.group(1)]['FG']))*float(131.25)) # Calculate Alcohol by Volume from OG/FG
                        self._show_brew(brewmatch.group(1), event)
                        # Save data
                        with open(self.loke.config['brew'], mode='w') as outfile:
                            json.dump(self.brews, outfile, sort_keys=True, indent=4)
            return

        # Add custom key/value element to brew. Trigger on call to 
        # .brew <date> add <key> <description>
        brewmatch = re.match(r'\.brew (\d+) add (\w+) (.*)', event['text'], re.I)
        if brewmatch:
            if len(self.brews[brewmatch.group(1)]) > 0:
                if brewmatch.group(2) not in self.brews[brewmatch.group(1)]:
                    self.brews[brewmatch.group(1)][brewmatch.group(2)] = brewmatch.group(3)
                    self._show_brew(brewmatch.group(1), event)
                # Save data    
                with open(self.loke.config['brew'], mode='w') as outfile:
                    json.dump(self.brews, outfile, sort_keys=True, indent=4)
            return

        # Delete custom key/value element to brew. Trigger on call to 
        # .brew <date> del <key>
        brewmatch = re.match(r'\.brew (\d+) del (\w+)', event['text'], re.I)
        if brewmatch:
            if len(self.brews[brewmatch.group(1)]) > 0:
                if brewmatch.group(2) in self.brews[brewmatch.group(1)] and brewmatch.group(2).upper() != 'OG' and brewmatch.group(2).upper() != 'FG' and brewmatch.group(2).lower() != 'gravity' and brewmatch.group(2).lower() != 'files':
                    del self.brews[brewmatch.group(1)][brewmatch.group(2)]
                    self._show_brew(brewmatch.group(1), event)
                # Save data    
                with open(self.loke.config['brew'], mode='w') as outfile:
                    json.dump(self.brews, outfile, sort_keys=True, indent=4)
            return

        # Show brew information. Trigger on call to 
        # .brew <id>
        brewmatch = re.match(r'\.brew (\d+)', event['text'], re.I)
        if brewmatch:
            self._show_brew(brewmatch.group(1), event)
            return
            
        # Add new empty brew. Trigger on call to 
        # .brew add
        brewmatch = re.match(r'\.brew add', event['text'], re.I)
        if brewmatch:
            self.brews['%s' % (len(self.brews)+1)] = {}
            self.brews['%s' % (len(self.brews))]['gravity'] = []
            self.loke.sc.chat_postMessage(as_user="true:", channel=event['channel'], text='Brew %s added!' % (len(self.brews)))
            # Save data
            with open(self.loke.config['brew'], mode='w') as outfile:
                json.dump(self.brews, outfile, sort_keys=True, indent=4)
            return

        # List all brew function. Trigger on call to 
        # .brew help
        brewmatch = re.match(r'\.brew help', event['text'], re.I)
        if brewmatch:
            self.loke.sc.chat_postMessage(as_user="true:", channel=event['channel'], text='Available commands - See https://github.com/chriskj/loke/blob/master/README.md#brew')    
            return

        # List all brews. Trigger on call to 
        # .brew 
        brewmatch = re.match(r'\.brew', event['text'], re.I)
        if brewmatch:
            self.loke.sc.chat_postMessage(as_user="true:", channel=event['channel'], text='*List of brews:*\n%s' % ('\n'.join(['%s - %s :: %s' % (key, self.brews[key].get('brewdate', 'Unknown date'), self.brews[key].get('name', 'No Name')) for key, brew in sorted(self.brews.items(), key=lambda i: int(i[0]))])))

            return

        # List all brews. Trigger on call to 
        # .brew 
        brewmatch = re.match(r'\.recipe', event['text'], re.I)
        if brewmatch:
            beer = recipe()
            beer.load('https://www.brewersfriend.com/homebrew/recipe/beerxml1.0/414816')
            attachment = [{
                "author_name": 'Beerxml - %s' % beer.name,
                "author_icon": ':beers:',
                "fields": [
                ],
                "color": "#aaaaaa",
                "mrkdwn_in": ["fields"]
            }]

            attachment[0]['fields'].append({
                'title': 'Fermentables',
                'value': '```%s```' % ('\n'.join(['%s %s kg' % (fermentable['name'].ljust(10), fermentable['amount']) for (fermentable) in beer.fermentables])),
            })

            attachment[0]['fields'].append({
                'title': 'Hops',
                'value': '```%s```' % ('\n'.join(['%s %s %s %s' % (hop['use'].ljust(10), hop['time'].ljust(6), hop['name'].ljust(20), hop['amount']) for (hop) in sorted(beer.hops, key=lambda x: int(x['time']))])),
            })

            attachment[0]['fields'].append({
                'title': 'Misc',
                'value': '```%s```' % ('\n'.join(['%s %s %s %s' % (misc['use'].ljust(10), misc['time'].ljust(6), misc['name'].ljust(20), misc['amount']) for (misc) in sorted(beer.miscs, key=lambda x: int(x['time']))])),
            })

            self.loke.sc.chat_postMessage(as_user="true:", channel=event['channel'], attachments=json.dumps(attachment))

            return

        # Fetch files if a comment indicates so
        if 'subtype' in event.keys():
            comment = ''
            if event['subtype'] == 'file_comment':
                comment = event['comment']['comment']
                url = event['file']['url_private']

            if event['subtype'] == 'file_share':
                if 'initial_comment' in event['file'].keys():
                    comment = event['file']['initial_comment']['comment']
                url = event['file']['url_private']

            # Check if comment indicates fetching files
            brewmatch = re.match(r'\.brew (\d+) file add', comment, re.I)
            if brewmatch:
                if len(self.brews[brewmatch.group(1)]) > 0:
                    headers = {'Authorization': 'Bearer %s' % self.loke.config['token']} # Needed for authorization
                    r = requests.get(url, headers=headers, stream=True)
                    filename = '%s%s-%s' % (self.loke.config['brewfiles'], brewmatch.group(1), event['file']['name'])
                    if r.status_code == 200:
                        with open(filename, 'wb') as f:
                            for chunk in r:
                                f.write(chunk)
                        if 'files' not in self.brews[brewmatch.group(1)].keys():
                            self.brews[brewmatch.group(1)]['files'] = []
                        self.brews[brewmatch.group(1)]['files'].append(event['file']['name']) # Let the json know we have a file uploaded
                        # Save data
                        with open(self.loke.config['brew'], mode='w') as outfile:
                            json.dump(self.brews, outfile, sort_keys=True, indent=4)
                    else:
                        print("Download failed")



    def handle_loop(self):
        # handle_loop() is used by handlers to pick up data when it's not triggered by message og presence change (i.e. watch, countdowns++)
        return



class recipe(object):
    def __init__(self):
        self.name = None

        self.og = None
        self.fg = None
        self.abv= None
        self.ibu = None

        self.hops = []
        self.fermentables = []
        self.miscs = []
        self.yeasts = []

    def load(self, url):
        data = requests.get(url).text
        xml = ET.fromstring(data)

        self.name = xml.find('RECIPE').find('NAME').text

        self.abv = xml.find('RECIPE').find('EST_ABV').text
        self.fg = xml.find('RECIPE').find('EST_FG').text
        self.og = xml.find('RECIPE').find('EST_OG').text

        for fermentable in xml.find('RECIPE').find('FERMENTABLES'):
            self.fermentables.append({
                'name': fermentable.find('NAME').text,
                'amount': fermentable.find('AMOUNT').text,
            })

        for hop in xml.find('RECIPE').find('HOPS'):
            self.hops.append({
                'name': hop.find('NAME').text,
                'amount': hop.find('AMOUNT').text,
                'time': hop.find('TIME').text,
                'use': hop.find('USE').text,
            })

        for misc in xml.find('RECIPE').find('MISCS'):
            self.miscs.append({
                'name': misc.find('NAME').text,
                'amount': misc.find('AMOUNT').text,
                'time': misc.find('TIME').text,
                'use': misc.find('USE').text,
            })


