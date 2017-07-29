# coding=UTF-8
import requests
import json
import re
from datetime import datetime
import dateutil.parser

from loke import LokeEventHandler

class RuterHandler(LokeEventHandler):
    # Realtime data from Ruter

    def handler_version(self):
        # Handler information
        return("Ruter")

    def __init__(self, loke):
        # Initiate the handler
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: %s" % self.handler_version())

    def handle_message(self, event):
        # A message is recieved from Slack

        rutermatch = re.match(r'\.ruter (.*)', event['text'], re.I)
        if rutermatch:
            ruter = Ruter()
            with open(self.loke.config['ruterstops'], 'r') as infile:
                stops = json.load(infile)

            stationname = rutermatch.group(1).lower().strip()
            if stationname not in stops:
                self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='%s not found in Ruter database' % stationname)
                return

            attachment = [{
                "author_name": 'Ruter - Kollektivtrafikk i Oslo og Akershus',
                "author_link": 'http://ruter.no/',
                "author_icon": "http://www.prosam.org/img/logo/ruter.gif",
                "fields": [],
                "color": "#aaaaaa"
            }]
            
            for stop in stops[stationname]:

                attachment[0]['fields'].append({
                    'title': stop['Name'],
                    'value': '\n'.join(['%s - %s %s' % (departure['FormattedDepartureTime'], departure['LineRef'], departure['DestinationName']) for departure in ruter.GetDepartures(stop['ID'])[:5]]),
                    'short': False

                })

            self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], attachments=json.dumps(attachment))
        return

    def handle_presence_change(self, event):
        # A user changes state active/inactive
        return

    def handle_loop(self):
        # handle_loop() is used by handlers to pick up data when it's not triggered by message og presence change (i.e. watch, countdowns++)
        return

class Ruter(object):
    def __init__(self):
        return

    def GetLines(self):
        url = 'http://reisapi.ruter.no/Line/GetLines'
        return self._FetchData(url)

    def GetStops(self, lineid):
        stops = []

        stopurl = 'http://reisapi.ruter.no/Line/GetStopsByLineId/%s' % (lineid)
        stopdata = self._FetchData(stopurl)

        for stop in stopdata:
            stops.append(stop)

        return stops

    def GetDepartures(self, stopid):    
        url = 'http://reisapi.ruter.no/StopVisit/GetDepartures/%s' % (stopid)
        departures = []
        for entry in self._FetchData(url)[:5]:
            departuretime = dateutil.parser.parse(entry['MonitoredVehicleJourney']['MonitoredCall']['AimedDepartureTime']).replace(tzinfo=None)
            timediff = int((departuretime - datetime.now()).seconds/60) # Number of minutes until departure

            if departuretime < datetime.now():
                formattedtime = 'nå'
            elif timediff == 0: # Use 'nå' instead of number of minutes
                formattedtime = 'nå'
            elif timediff < 10: # Show number of minutes if it's less than 10 minutes
                formattedtime = '%s min' % timediff
            else: # Show time if it's more than 10 minutes
                formattedtime = datetime.strftime(departuretime, '%H:%M')

            departures.append({
                'LineRef': entry['MonitoredVehicleJourney']['LineRef'],
                'OriginName': entry['MonitoredVehicleJourney']['OriginName'],
                'DestinationName': entry['MonitoredVehicleJourney']['DestinationName'],
                'AimedDepartureTime': departuretime,
                'DepartureMinutes': timediff,
                'FormattedDepartureTime': formattedtime
            })
        departures = sorted(departures, key=lambda x: x['AimedDepartureTime'])
        return departures    

    def _FetchData(self, url):
        headers = {'Accept': 'application/json'}

        r = requests.get(url, headers=headers)
        return json.loads(r.text)

    def _UpdateStopsData(self):    
        lines = self.GetLines()
        ourlines = []

        allstops = {}
        for line in lines:
            if len(line['Name']) < 3 and str(line['ID']) == line['Name']:
                line['stops'] = []
                stops = self.GetStops(line['ID'])
                for stop in stops:
                    line['stops'].append(stop)
                    if '(' in stop['Name']:
                        name = stop['Name'][:stop['Name'].find('(')-1].lower()
                    elif '[' in stop['Name']:
                        name = stop['Name'][:stop['Name'].find('[')-1].lower()
                    else:
                        name = stop['Name'].lower()

                    if name not in allstops:
                        allstops[name] = []
                    if not any(s['ID'] == stop['ID'] for s in allstops[name]):
                        allstops[name].append(stop)  

                ourlines.append(line)
        
        #with open('lines.json', 'w') as outfile:
        #    json.dump(ourlines, outfile, sort_keys=True, indent=4, ensure_ascii=False)

        with open(self.loke.config['ruterstops'], 'w') as outfile:
            json.dump(allstops, outfile, sort_keys=True, indent=4, ensure_ascii=False)


#if __name__ == '__main__':
#    ruter = Ruter()
#    ruter._UpdateStopsData()

