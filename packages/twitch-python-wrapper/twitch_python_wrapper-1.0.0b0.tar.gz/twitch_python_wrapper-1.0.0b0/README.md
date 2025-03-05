# Twitch Python Wrapper
A Python wrapper for the Twitch API, EventSub and Authentication <sup>**SOON**</sup>.

No need to hassle about WebSockets nor data structures

## Installation
`pip install twitch-python-wrapper`

## What this wraps
This wraps around Twitch's

- [API](https://dev.twitch.tv/docs/api/),
- [EventSub](https://dev.twitch.tv/docs/eventsub/), and
- [Authentication](https://dev.twitch.tv/docs/authentication/) <sup>**SOON**</sup>

## Usage
### API
```python
from twitch_python_wrapper.api.client import APIClient


# While you can set the 'access_token' parameter to a user access token,
# those endpoints that can only be used with a user access token are
# not yet supported by this wrapper
client = APIClient(
    client_id="CLIENT_ID",
    access_token="APP_ACCESS_TOKEN"
)
user = client.users.get_users(login="twitchdev")

# Change the 'id' attribute to get whatever you want!
print(user.id)
```

### EventSub

Using decorators, great for getting just one event in a function
```python
from twitch_python_wrapper.eventsub.client import EventSubClient
from twitch_python_wrapper.eventsub.objects import Metadata
from twitch_python_wrapper.enums import SubscriptionType


# The parameter 'access_token' MUST be a user access token
client = EventSubClient(
    client_id="CLIENT_ID",
    access_token="USER_ACCESS_TOKEN"
)

# Event triggered when WebSocket Welcome Message is received
@client.on("builtins.message.welcome")
def connected(metadata: Metadata, payload: dict):
    print("Connected with EventSub")
    
# Change the broadcaster_user_id by your own and
# this event should fire everytime you edit your stream info
@client.on(
    SubscriptionType.CHANNEL_UPDATE,
    "2",
    {"broadcaster_user_id": "1337"}
)
def on_channel_update(metadata: Metadata, payload: dict):
    # https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channel-update-notification-payload
    name = payload["event"]["broadcaster_user_name"]
    title = payload["event"]["title"]
    language = payload["event"]["language"]
    category = payload["event"]["category_name"]
    
    print(f"{name} updated their stream info")
    print(f"Stream title -> {title}")
    print(f"Stream language -> {language}")
    print(f"Stream category -> {category}")
```

Without decorators, great for getting multiple events to a function
```python
from twitch_python_wrapper.eventsub.client import EventSubClient
from twitch_python_wrapper.eventsub.objects import Metadata
from twitch_python_wrapper.enums import SubscriptionType


# The parameter access_token MUST be a user access token
client = EventSubClient("CLIENT_ID", "USER_ACCESS_TOKEN")

# Event triggered when WebSocket Welcome Message is received
def connected(metadata: Metadata, payload: dict):
    print("Connected with EventSub")
    
# Change the broadcaster_user_id by your own and
# this event should fire everytime you edit your stream info
def on_channel_update(metadata: Metadata, payload: dict):
    # https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/#channel-update-notification-payload
    name = payload["event"]["broadcaster_user_name"]
    title = payload["event"]["title"]
    language = payload["event"]["language"]
    category = payload["event"]["category_name"]
    
    print(f"{name} updated their stream info")
    print(f"Stream title -> {title}")
    print(f"Stream language -> {language}")
    print(f"Stream category -> {category}")

    
client.register(connected, "builtins.message.welcome")

broadcasters = ["1337", "12826", "141981764"]
for broadcaster in broadcasters:
    client.register(
        on_channel_update,
        SubscriptionType.CHANNEL_UPDATE,
        "2",
        {"broadcaster_user_id": broadcaster}
    )
```

### Authentication
_**SOON**_
