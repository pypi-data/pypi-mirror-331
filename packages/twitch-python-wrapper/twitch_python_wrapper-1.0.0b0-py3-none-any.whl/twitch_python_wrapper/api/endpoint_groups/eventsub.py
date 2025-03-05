import httpx
from dateutil.parser import isoparse

from twitch_python_wrapper.api.client import APIClient
from twitch_python_wrapper.api.enums import SubscriptionStatus
from twitch_python_wrapper.api.objects import Subscription, Pagination
from twitch_python_wrapper.enums import SubscriptionType
from twitch_python_wrapper.objects import NotificationTransport


class EventSub:
    def __init__(self, client: APIClient):
        self.client = client

    def create_eventsub_subscription(self,
                                     subscription_type: SubscriptionType,
                                     version: str,
                                     condition: dict,
                                     transport: NotificationTransport) -> tuple[Subscription, int, int, int]:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#create-eventsub-subscription>`_

        Creates an EventSub subscription.

        :param subscription_type: The type of subscription to create. For a list of subscription that you can create,
            see `Subscription Types
            <https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types#subscription-types>`_.

        :param version: The version number that identifies the definition of the subscription type that you want the
            response to use.

        :param condition: A dictionary object that contains the parameter values that are specific to the specified
            subscription type. For the object's required and optional fields, see the subscription type's documentation.

        :param transport: The transport details that you want Twitch to use when sending you notifications.

        :return: The subscription you created, the total number of subscriptions you've created, the sum of all of your
            subscription costs. `Learn More
            <https://dev.twitch.tv/docs/eventsub/manage-subscriptions/#subscription-limits>`_, and the maximum total cost
            that you're allowed to incur for all subscriptions you create.
        """

        url = self.client.url + "eventsub/subscriptions"

        validation = {
            (transport.method == "webhook" and ((transport.callback is None or transport.secret is None) and (transport.session_id is not None or transport.conduit_id is not None))):
                "If transport.method is webhook then transport.callback and transport.secret must not be None and transport.session_id and transport.conduit_id must be None",
            (transport.method == "websocket" and ((transport.session_id is None) and (transport.callback is not None or transport.secret is not None or transport.conduit_id is not None))):
                "If transport.method is websocket then transport.session_id must not be None and transport.callback, transport.secret and transport.conduit_id must be None",
            (transport.method == "conduit" and ((transport.conduit_id is None) and (transport.callback is not None or transport.secret is not None or transport.session_id is not None))):
                "If transport.method is conduit then transport.conduit_id must not be None and transport.callback, transport.secret and transport.session_id must be None"
        }

        for validation_condition, error in validation.items():
            if validation_condition: raise ValueError(error)

        body = {
            "type": subscription_type.value,
            "version": version,
            "condition": condition,
            "transport": {
                "method": transport.method
            }
        }
        match transport.method:
            case "webhook":
                body["transport"]["callback"] = transport.callback
                body["transport"]["secret"] = transport.secret
            case "websocket":
                body["transport"]["session_id"] = transport.session_id
            case "conduit":
                body["transport"]["conduit_id"] = transport.conduit_id

        req = httpx.post(url,
                         json=body,
                         headers=self.client.headers,
                         timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()

        sub = res["data"][0]
        transport = NotificationTransport(
            method=sub["transport"]["method"],
            callback=sub["transport"]["callback"] if "callback" in sub["transport"] else None,
            secret=sub["transport"]["secret"] if "secret" in sub["transport"] else None,
            session_id=sub["transport"]["session_id"] if "session_id" in sub["transport"] else None,
            conduit_id=sub["transport"]["conduit_id"] if "conduit_id" in sub["transport"] else None,
            connected_at=sub["transport"]["connected_at"] if "connected_at" in sub["transport"] else None,
            disconnected_at=sub["transport"]["disconnected_at"] if "disconnected_at" in sub["transport"] else None
        )

        subscription = Subscription(
            id=sub["id"],
            status=sub["status"],
            type=SubscriptionType(sub["type"]),
            version=sub["version"],
            condition=tuple(sorted((str(k), str(v)) for k, v in sub["condition"].items())),
            created_at=int(isoparse(sub["created_at"]).timestamp()),
            transport=transport,
            cost=sub["cost"]
        )

        return subscription, res["total"], res["total_cost"], res["max_total_cost"]

    def delete_eventsub_subscription(self,
                                     subscription_id: str) -> None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#delete-eventsub-subscription>`_

        Deletes an EventSub subscription

        :param subscription_id: The ID of the subscription to delete
        """

        url = self.client.url + "eventsub/subscriptions"

        req = httpx.delete(url,
                           params={"id": subscription_id},
                           headers=self.client.headers,
                           timeout=self.client.timeout)
        req.raise_for_status()

    # https://dev.twitch.tv/docs/api/reference/#get-eventsub-subscriptions
    def get_eventsub_subscriptions(self,
                                   status: SubscriptionStatus = None,
                                   subscription_type: SubscriptionType = None,
                                   user_id: str = None,
                                   after: Pagination = None) -> None | tuple[tuple[Subscription, ...], int, int, int] | tuple[tuple[Subscription, ...], int, int, int, Pagination]:
        url = self.client.users + "eventsub/subscriptions"

        parameters = {}

        optional_params = {
            "status": status.value if status else None,
            "type": subscription_type.value if subscription_type else None,
            "user_id": user_id,
            "after": after.cursor if after else None
        }

        if ("after" in optional_params and len(optional_params) > 2) or len(optional_params) > 1:
            raise ValueError("Can't specify more than one filter")

        for key, value in optional_params.items():
            if value: parameters[key] = value

        req = httpx.get(url,
                        params=parameters,
                        headers=self.client.headers,
                        timeout=self.client.timeout)

        req.raise_for_status()
        res = req.json()

        if len(res["data"]) < 1: return None

        subscriptions = list()
        for sub in res["data"]:
            transport = NotificationTransport(
                method=sub["transport"]["method"],
                callback=sub["transport"]["callback"] if "callback" in sub["transport"] else None,
                secret=sub["transport"]["secret"] if "secret" in sub["transport"] else None,
                session_id=sub["transport"]["session_id"] if "session_id" in sub["transport"] else None,
                conduit_id=sub["transport"]["conduit_id"] if "conduit_id" in sub["transport"] else None,
                connected_at=sub["transport"]["connected_at"] if "connected_at" in sub["transport"] else None,
                disconnected_at=sub["transport"]["disconnected_at"] if "disconnected_at" in sub["transport"] else None
            )

            subscriptions.append(Subscription(
                id=sub["id"],
                status=sub["status"],
                type=SubscriptionType(sub["type"]),
                version=sub["version"],
                condition=tuple(sorted((str(k), str(v)) for k, v in sub["condition"].items())),
                created_at=int(isoparse(sub["created_at"]).timestamp()),
                transport=transport,
                cost=sub["cost"]
            ))

        if len(res["pagination"]) > 0:
            return tuple(subscriptions), res["total"], res["total_cost"], res["max_total_cost"], Pagination(res["pagination"]["cursor"])

        return tuple(subscriptions), res["total"], res["total_cost"], res["max_total_cost"]
