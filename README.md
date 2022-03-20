# loke
Loke, a simple bot

Install required modules into a virtualenv (python3) by using pip -r requirements.txt

To choose what modules to be used, comment/uncomment in main.py (both import-statements and the lines where they are used).
Also make sure you change the name config.py-sample, as well as the the files in the data/-folder so they will be usable.

## Docker
Docker appuser is running under uid 5050. Make sure uid 5050 have write access to the data folder, and map the data folder in the following way
```
docker run -v /home/loke/lokedata/:/app/data --restart unless-stopped -d loke:latest
```

## Modules

### AtB

Real time information from [AtB](https://www.atb.no) (Trondheim public transportation)

##### Syntax

```.atb <stopname>```

### Auto Response

Will respond to certain words as described in ```data/autoresponse.json```

### Avinor

Real time information from [Avinor](http://www.avinor.no) (Norwegian airport authorities)

##### Syntax

```.avinor <flightno> <airport> <date>```

<a name="brew" />

### Brew

Brewbot to keep track of brews

##### Syntax
```
.brew - list brews
.brew add - add new brew, will return ID
.brew <id> - Show information about brew
.brew <id> add <key> <description> - Add custom element to brew. Two special keys: name and brewdate
.brew <id> del <key> - Delete custom element from brew
.brew <id> gravity add <date> <gravity> - Add measured gravity. Date format: yyyy-mm-dd
.brew <id> gravity del <date> - Delete measured gravity. Date format: yyyy-mm-dd
```



### Bysykkel (Trondheim)

Shows real time information about stations in [Trondheim Bysykkel](https://trondheimbysykkel.no/)

##### Syntax

```.bysykkel```

### Chartertur

### Har mannen falt?

Returning information if the mountains Mannen and Veslemannen has fallen

##### Syntax

```
.harmannenfalt
.harveslemannenvalt
```

### Ruter

### Seen

##### Syntax

```
.seen <@user>
.seenall
```

### Transport for London

Returning real time information from [TfL](https://www.tfl.gov.uk)

##### Syntax

```
.tfl status
.tfl <station name>
```

### Weather

### Yr

##### Syntax

```.yr <place>```

