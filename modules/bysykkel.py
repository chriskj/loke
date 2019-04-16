import json
import requests
from loke import LokeEventHandler

class Bysykkel(object):
    def __init__(self):
        self.identifier = 'ckj-development'
    
    def get_stations(self):
        """Return list of stations"""
        url = 'https://gbfs.urbansharing.com/trondheimbysykkel.no/station_information.json'
        
        data = self._FetchData(url)
        return data['data']['stations']
        
    def get_status(self, stations:list = None):
        """Return list of stations w/ status"""
        url = 'https://gbfs.urbansharing.com/trondheimbysykkel.no/station_status.json'

        data = self._FetchData(url)

        if stations:
            results = []
            for station in data['data']['stations']:
                if station.get('station_id') in stations:
                    results.append(station)
            return results

        else:
            return data['data']['stations']
    

    def _FetchData(self, url):
        headers = {'IDENTIFIER': self.identifier}

        r = requests.get(url, headers=headers)
        return json.loads(r.text)


class BysykkelHandler(LokeEventHandler):
    # Handler to fetch Restplass-data

    def handler_version(self):
        # Handler information
        return("Bysykkel")

    def __init__(self, loke):
        # Initiate the handler
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: %s" % self.handler_version())

    def handle_message(self, event):
        # A message is recieved from Slack
        if event['text'] == '.bysykkel': # Responds to call .bysykkel
            bs = Bysykkel()
            stations = {}
            for entry in bs.get_stations():
                stations[entry['station_id']] = entry

            # stationstatus = bs.get_status(['47', '268', '95', '14'])
            stationstatus = bs.get_status()

            attachment = [{
                "author_name": 'Trondheim Bysykkel - Realtime',
                'author_link': 'https://trondheimbysykkel.no/',
                "author_icon": 'https://image.flaticon.com/icons/svg/71/71422.svg',
                "fields": [
                ],
                "color": "#FF0000",
                "mrkdwn_in": ["fields"]
            }]
            
            # Used to split columns
            num_stations = int(len(stationstatus)/2)+1

            # Column 1
            attachment[0]['fields'].append({
                'title': 'Bikes available 1/1',
                'value': '```',
                'short': 'true'
            })

            for station in sorted(stationstatus, key=lambda x: stations[x['station_id']]['name'])[0:num_stations]:
                l1 = len(str(station['num_bikes_available']))
                attachment[0]['fields'][-1]['value'] += '%s / %s%s - %s\n' % (station['num_bikes_available'], int(station['num_bikes_available'])+int(station['num_docks_available']), ' '*(2-l1), stations[station['station_id']]['name'])
            
            attachment[0]['fields'][-1]['value'] += '```'


            # Column 2
            attachment[0]['fields'].append({
                'title': '2/2',
                'value': '```',
                'short': 'true'
            })

            for station in sorted(stationstatus, key=lambda x: stations[x['station_id']]['name'])[num_stations:]:
                l1 = len(str(station['num_bikes_available']))
                attachment[0]['fields'][-1]['value'] += '%s / %s%s - %s\n' % (station['num_bikes_available'], int(station['num_bikes_available'])+int(station['num_docks_available']), ' '*(2-l1), stations[station['station_id']]['name'])
            
            attachment[0]['fields'][-1]['value'] += '```'    
            
            
            
            self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], attachments=json.dumps(attachment))    

        

    def handle_presence_change(self, event):
        # A user changes state active/inactive
        return

    def handle_loop(self):
        # handle_loop() is used by handlers to pick up data when it's not triggered by message or presence change (i.e. watch, countdowns++)
        return

