# loke

Loke is a simple Slack command bot. It connects through the current Slack
Events API using Socket Mode, so it does not need a public HTTP endpoint.

## Set up the Slack app

1. Open [Your Apps](https://api.slack.com/apps), choose **Create New App** and
   **From an app manifest**. Select the workspace, choose YAML, and paste the
   contents of [`slack-manifest.yaml`](slack-manifest.yaml).
2. Under **Settings → Basic Information → App-Level Tokens**, generate a token
   with the `connections:write` scope. Save the `xapp-...` value as
   `SLACK_APP_TOKEN`.
3. Under **Features → OAuth & Permissions**, choose **Install to Workspace**
   (or **Reinstall to Workspace** after changing scopes). Save the
   **Bot User OAuth Token** (`xoxb-...`) as `SLACK_BOT_TOKEN`.
4. If the bot should accept direct messages, open **Features → App Home**,
   enable the Messages tab, and allow users to send messages from it.
5. Invite the app to every public or private channel in which it should read
   and answer commands: `/invite @Loke`.

The manifest subscribes to messages in public channels, private channels, DMs,
and group DMs. It requests the matching history scopes plus `chat:write`.
`files:read` and `files:write` are used by the Brew module; remove those two
scopes if that module is disabled.

> Slack's modern granular-permission apps cannot use the legacy RTM API or
> `presence_sub`. As a result, presence-triggered behavior in `SeenHandler` and
> `TurstatusHandler` is no longer invoked. `.seen` still records message
> activity, and the other message commands continue to work.

## Run locally

Python 3.13 is the supported runtime.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp config.py-sample config.py
mkdir -p data
cp data-examples/*.json-sample data/
export SLACK_BOT_TOKEN='xoxb-...'
export SLACK_APP_TOKEN='xapp-...'
python main.py
```

Rename the copied sample data files to remove `-sample`, and update their paths
and module-specific credentials in `config.py`. Choose which modules are loaded
by commenting or uncommenting entries in `HANDLERS` in `main.py`. A module that
cannot initialize is logged and skipped so it does not prevent the Slack bot
from connecting.

Run the Slack transport tests with:

```bash
python -m unittest discover -s tests -p '*_test.py'
```

## Docker

```bash
docker build -t loke:latest .
docker run \
  --name loke \
  --restart unless-stopped \
  -e SLACK_BOT_TOKEN='xoxb-...' \
  -e SLACK_APP_TOKEN='xapp-...' \
  -v /home/loke/lokedata/:/app/data \
  -d loke:latest
```

The container runs as uid 5050, so that uid must have read/write access to the
mounted data directory. Keep both Slack tokens out of the image and source
control.

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

