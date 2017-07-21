# coding=UTF-8
import zeep
from datetime import datetime
import pytz

from loke import LokeEventHandler
import re
import json

class AtBHandler(LokeEventHandler):
    # Handler description

    def handler_version(self):
        # Handler information
        return("AtB")

    def __init__(self, loke):
        # Initiate the handler
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: %s" % self.handler_version())

        self.atb = AtB()

    def handle_message(self, event):
        # A message is recieved from Slack
        atbmatch = re.match(r'\.atb (.*)', event['text'], re.I)
        if atbmatch:
            stopname = atbmatch.group(1).lower()

            # Load a full dict of all stops/ids for AtB
            with open(self.loke.config['atbstops'], 'r') as fil:
                stops = json.load(fil) 

            # Check if provided stopname exist in dict and list all trips for the stop ids related to the name
            if stopname in stops: # Check if stopname is in dict
                trips = self.atb.GetMultipleStopStatus(stops[stopname]) # Fetch data from AtB
                for stop in trips: # We want one response to Slack for each stop
                    message = '* %s (id: %s):*\n' % (stopname.title(), stop[0]['StopId']) # Message title
                    message += '```'        
                    for trip in stop[:8]: # Only fetch 8 for each stop
                        ca = ''
                        if trip['RealTime'] is False: # Add Ca prefix if realtime data is not present
                            ca = 'Ca '
                        if trip['ArrivalMinutes'] == 0: # Use 'nå' instead of number of minutes
                            message += '%snå - %s %s\n' % (ca, trip['LineNumber'], trip['LineDestination'])
                        elif trip['ArrivalMinutes'] < 10: # Show number of minutes if it's less than 10 minutes
                            message += '%s%s min - %s %s\n' % (ca, trip['ArrivalMinutes'], trip['LineNumber'], trip['LineDestination'])
                        else: # Show time if it's more than 10 minutes
                            message += '%s%s - %s %s\n' % (ca, trip['DepartureTime'].strftime('%H:%M'), trip['LineNumber'], trip['LineDestination'])
                    message += '```'        
                    self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text=message)

        return

    def handle_presence_change(self, event):
        # A user changes state active/inactive
        return

    def handle_loop(self):
        # handle_loop() is used by handlers to pick up data when it's not triggered by message og presence change (i.e. watch, countdowns++)
        return

class AtB(object):
    def __init__(self):
        wsdlurl = 'http://st.atb.no/SMWS/SMService.svc?wsdl'
        self.client = zeep.Client(wsdl=wsdlurl)

    def GetMultipleStopStatus(self, stoplist):
        # Do one request to AtB containing multiple stops

        # stoplist argument is a list of ids to query
        requestfilter = []
        for stop in stoplist:
            requestfilter.append({'MonitoringRef': stop})
            
        # Generate query based on list of ids
        response = self.client.service.GetMultipleStopMonitoring(
            ServiceRequestInfo={
                'RequestorRef':'Loke', 
                'RequestTimestamp': datetime.now(), 
            }, 
            Request={
                'version': '1.4',
                'RequestTimestamp': datetime.now(), 
                'StopMonitoringFilter': requestfilter
            },
            RequestExtension={}
        )

        stops = [] # A list to contain one entry pr stopid
        for stop in response.Answer.StopMonitoringDelivery:
            trips = [] # A list to contain one entry pr trip. Each entry is a dict
            for item in stop.MonitoredStopVisit:
                # use expectedtime as common term, regardless if we have real time data available or not
                if item.MonitoredVehicleJourney.MonitoredCall.ExpectedDepartureTime is None: 
                    expectedtime = item.MonitoredVehicleJourney.MonitoredCall.AimedDepartureTime.replace(tzinfo=None)
                    real = False
                else:    
                    expectedtime = item.MonitoredVehicleJourney.MonitoredCall.ExpectedDepartureTime
                    real = True 
                
                timediff = int((expectedtime - datetime.now()).seconds/60) # Number of minutes until departure

                trip = {} # Dict containing all data for trip
                trip['ArrivalMinutes'] = timediff
                trip['RealTime'] = real
                trip['DepartureTime'] = expectedtime
                trip['LineNumber'] = item.MonitoredVehicleJourney.LineRef
                trip['LineOrigin'] = item.MonitoredVehicleJourney.OriginName
                trip['LineDestination'] = item.MonitoredVehicleJourney.MonitoredCall.DestinationDisplay
                trip['StopId'] = item.MonitoringRef

                trips.append(trip)
            
            # Only add entry to the stops list if we have trips
            if len(trips) > 0:
                stops.append(trips)    
        return stops

    def GetStopStatus(self, stopid):
        # Do one request to AtB containing one stop id
        
        # Generate query based on id
        response = self.client.service.GetStopMonitoring(
            ServiceRequestInfo={
                'RequestorRef':'Loke', 
                'RequestTimestamp': datetime.now(), 
            }, 
            Request={
                'version': '1.4',
                'RequestTimestamp': datetime.now(), 
                'MonitoringRef': '%s' % (stopid,)
            },
            RequestExtension={}
        )
        trips = [] # A list to contain one entry pr trip. Each entry is a dict

        for item in response.Answer.StopMonitoringDelivery[0].MonitoredStopVisit:
            # use expectedtime as common term, regardless if we have real time data available or not
            if item.MonitoredVehicleJourney.MonitoredCall.ExpectedDepartureTime is None:
                expectedtime = item.MonitoredVehicleJourney.MonitoredCall.AimedDepartureTime.replace(tzinfo=None)
                real = False
            else:    
                expectedtime = item.MonitoredVehicleJourney.MonitoredCall.ExpectedDepartureTime
                real = True 
            
            timediff = int((expectedtime - datetime.now()).seconds/60) # Number of minutes until departure

            trip = {} # Dict containing all data for trip
            trip['ArrivalMinutes'] = timediff
            trip['RealTime'] = real
            trip['DepartureTime'] = expectedtime
            trip['LineNumber'] = item.MonitoredVehicleJourney.LineRef
            trip['LineOrigin'] = item.MonitoredVehicleJourney.OriginName
            trip['LineDestination'] = item.MonitoredVehicleJourney.MonitoredCall.DestinationDisplay
            trip['StopId'] = item.MonitoringRef

            trips.append(trip)

        return trips 

