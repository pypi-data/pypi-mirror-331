import asyncio
import json
import ssl
import time
from typing import Callable, Literal

import certifi
import websockets
from dateutil.parser import isoparse

from twitch_python_wrapper.api.client import APIClient
from twitch_python_wrapper.enums import SubscriptionType, NotificationTransportMethod
from twitch_python_wrapper.eventsub.enums import MessageType
from twitch_python_wrapper.eventsub.objects import Metadata
from twitch_python_wrapper.objects import NotificationTransport

BuiltinNotifications = Literal[
    "builtins.message.welcome",
    "builtins.message.keepalive",
    "builtins.message.notification",
    "builtins.message.reconnect",
    "builtins.message.revocation"
]

class EventSubClient:
    """
    Twitch EventSub client
    """

    session_id = None
    _ssl = ssl.create_default_context()
    _ssl.load_verify_locations(certifi.where())


    def __init__(self,
                 client_id: str,
                 access_token: str,
                 url: str = None,
                 timeout: int = 10) -> None:
        """
        Initializer of Twitch's EventSub client.

        :param client_id: Twitch application client ID, see `step 9
            <https://dev.twitch.tv/docs/authentication/register-app/>`_.

        :param access_token: Twitch **user** access token. In future updates this will be managed by the wrapper, but
            until then see `Twitch application authentication <https://dev.twitch.tv/docs/authentication/>`_.

        :param url: Twitch's EventSub WebSocket server URL, no need to specify it unless reconnection (which is handled
            automatically). Valid values are between 10 and 600

        :param timeout: Timeout in seconds used when expecting keepalive messages, default is ``10``.
        """

        if timeout < 10 or timeout > 600: raise ValueError("Parameter timeout must be between 10 and 600")

        self._timeout = timeout
        self._api = APIClient(client_id, access_token, self._timeout - 1)

        self._url = url if url else "wss://eventsub.wss.twitch.tv/ws?keepalive_timeout_seconds=" + str(self._timeout)
        self._registered_event_handlers: list[dict] = []
        self._previous_messages: list[str] = []
        self.__ws = None

    def on(self,
           subscription: SubscriptionType | BuiltinNotifications,
           version: str = None,
           condition: dict = None):
        """
        Decorator for setting a function as an event handler.
        Use ``register()`` when needing to set multiple subscriptions to a single function.

        :param subscription: Subscription to receive notifications, see `column "Name"
            <https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/>`_.

        :param version: Version of the subscription, see `column "Version"
            <https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/>`_

        :param condition: Conditions of the subscription, look up for `your subscription type here
            <https://dev.twitch.tv/docs/eventsub/eventsub-reference/#conditions>`_
        """

        validation = {
            ((not version and not condition) and isinstance(subscription, SubscriptionType)):
                "When subscription is a SubscriptionType, version and condition must be supplied",
            ((version and condition) and not isinstance(subscription, SubscriptionType)):
                "When subscription is a string, version and condition must not be supplied",
        }

        for validation_condition, error in validation.items():
            if validation_condition: raise ValueError(error)

        def callback(function: Callable[[Metadata, dict], None]):
            self.register(function, subscription, version, condition)
            return function

        return callback

    def register(self,
                 function: Callable[[Metadata, dict], None],
                 subscription: SubscriptionType | BuiltinNotifications,
                 version: str = None,
                 condition: dict = None) -> None:
        """
        Registers a function as an event handler.
        Use ``@on()`` when needing to set one subscription to one function.

        :param function: Function to register as an event handler.

        :param subscription: Subscription to receive notifications, see `column "Name"
            <https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/>`_.

        :param version: Version of the subscription, see `column "Version"
            <https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types/>`_

        :param condition: Conditions of the subscription, look up for `your subscription type here
            <https://dev.twitch.tv/docs/eventsub/eventsub-reference/#conditions>`_
        """

        handler = {
            "subscription": subscription,
            "condition": condition,
            "version": version,
            "callback": function,
            "registered": False
        }

        self._registered_event_handlers.append(handler)

        if self.session_id: self.__create_subscription(handler, self.session_id)

    def __create_subscription(self,
                              handler: dict,
                              session_id: str) -> None:
        if handler["registered"]: return

        self._api.eventsub.create_eventsub_subscription(
            subscription_type=handler["subscription"],
            version=handler["version"],
            condition=handler["condition"],
            transport=NotificationTransport(
                method=NotificationTransportMethod.WEBSOCKET,
                callback=None,
                secret=None,
                session_id=session_id,
                conduit_id=None,
                connected_at=None,
                disconnected_at=None
            )
        )
        handler["registered"] = True

    def _trigger_notification(self,
                              metadata: Metadata,
                              payload: dict) -> None:
        handler = None

        if not metadata.subscription_type or not isinstance(metadata.subscription_type, SubscriptionType): return

        for event_handler in self._registered_event_handlers:
            if event_handler["subscription"] != metadata.subscription_type: continue
            handler = event_handler
            break

        if handler: handler["callback"](metadata, payload)

    def _trigger_message(self,
                         metadata: Metadata,
                         payload: dict) -> None:
        message_type = metadata.message_type.value
        if "_" in message_type: message_type = message_type.split("_")[1]
        subscription = "builtins.message." + message_type
        handler = None

        for event_handler in self._registered_event_handlers:
            if event_handler["subscription"] != subscription: continue
            handler = event_handler
            break

        if handler: handler["callback"](metadata, payload)

    async def connect(self):
        """
        Connect to the Twitch EventSub
        """

        while True:
            async with websockets.connect(self._url, ssl=self._ssl if self._url.startswith("wss") else None) as self.__ws:
                try:
                    while True:
                        # Receiving raw message, then parsing to JSON, and finally parsing to respective objects
                        raw_message = await asyncio.wait_for(self.__ws.recv(), timeout=self._timeout + 1)
                        message = json.loads(raw_message)
                        metadata = Metadata(
                            message_id=message["metadata"]["message_id"],
                            message_type=MessageType(message["metadata"]["message_type"]),
                            message_timestamp=int(isoparse(message["metadata"]["message_timestamp"]).timestamp()),
                            subscription_type=SubscriptionType(message["metadata"]["subscription_type"]) if "subscription_type" in message["metadata"] else None,
                            subscription_version=message["metadata"]["subscription_version"] if "subscription_version" in message["metadata"] else None
                        )
                        payload = message["payload"]

                        # Resiliency against replay attacks:
                        # Checks if message_timestamp is older than 10 minutes, or
                        # if the received message_id has been received before
                        # See https://dev.twitch.tv/docs/eventsub/#guarding-against-replay-attacks
                        if metadata.message_timestamp < time.time() - 10*60 or self._previous_messages.count(metadata.message_id) > 0: continue
                        self._previous_messages.append(metadata.message_id)

                        match metadata.message_type:
                            # https://dev.twitch.tv/docs/eventsub/handling-websocket-events/#welcome-message
                            case MessageType.SESSION_WELCOME:
                                self.session_id = payload["session"]["id"]
                                if not self._timeout: self._timeout = payload["session"]["keepalive_timeout_seconds"]

                                for handler in self._registered_event_handlers:
                                    if not isinstance(handler["subscription"], SubscriptionType): continue
                                    self.__create_subscription(handler, self.session_id)

                            # https://dev.twitch.tv/docs/eventsub/handling-websocket-events/#notification-message
                            case MessageType.NOTIFICATION:
                                self._trigger_notification(metadata, payload)

                            # https://dev.twitch.tv/docs/eventsub/handling-websocket-events/#revocation-message
                            case MessageType.REVOCATION:
                                handler = None

                                for event_handler in self._registered_event_handlers:
                                    if event_handler["subscription"] != SubscriptionType(payload["subscription"]["type"]
                                    or event_handler["condition"] != payload["subscription"]["condition"]):
                                        continue
                                    handler = event_handler
                                    break

                                if handler: self._registered_event_handlers.remove(handler)

                            # https://dev.twitch.tv/docs/eventsub/handling-websocket-events/#reconnect-message
                            case MessageType.SESSION_RECONNECT:
                                self._url = payload["session"]["reconnect_url"]
                                await self.__ws.close()
                                break

                        self._trigger_message(metadata, payload)

                except asyncio.TimeoutError: await self.__ws.close()

                except websockets.ConnectionClosed: await self.__ws.close()

                except asyncio.CancelledError or KeyboardInterrupt:
                    await self.__ws.close()
                    break

            # Waits 5 seconds before attempting a reconnection
            await asyncio.sleep(5)
