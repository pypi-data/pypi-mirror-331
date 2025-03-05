import httpx

from twitch_python_wrapper.api.client import APIClient
from twitch_python_wrapper.api.enums import SubscriptionStatus
from twitch_python_wrapper.api.objects import Conduit, Pagination, ConduitShard
from twitch_python_wrapper.enums import NotificationTransportMethod
from twitch_python_wrapper.objects import NotificationTransport


class Conduits:
    def __init__(self, client: APIClient):
        self.client = client

    def get_conduits(self) -> Conduit | tuple[Conduit, ...] | None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-conduits>`_

        Returns the `conduits <https://dev.twitch.tv/docs/eventsub/handling-conduit-events/>`_ for a client ID.

        :return: Tuple of information about the client's conduits. If there's just one, that one is returned
        """

        url = self.client.url + "eventsub/conduits"

        req = httpx.get(url,
                        headers=self.client.headers,
                        timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()["data"]

        if len(res) < 1: return None

        conduits = list()
        for conduit in res:
            conduits.append(Conduit(id=conduit["id"],
                                    shard_count=conduit["shard_count"]))

        if len(conduits) < 2: return conduits[0]

        return tuple(conduits)

    def create_conduits(self,
                        shard_count: int) -> Conduit:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#create-conduits>`_

        Creates a new `conduit <https://dev.twitch.tv/docs/eventsub/handling-conduit-events/>`_.

        :param shard_count: The number of shards to create for this conduit.

        :return: The conduit created.
        """

        url = self.client.url + "eventsub/conduits"

        req = httpx.post(url,
                         json={"shard_count": shard_count},
                         headers=self.client.headers,
                         timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()["data"][0]

        return Conduit(id=res["id"],
                       shard_count=res["shard_count"])

    def update_conduits(self,
                        conduit_id: str,
                        shard_count: int) -> Conduit:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#update-conduits>`_

        Updates a `conduit's <https://dev.twitch.tv/docs/eventsub/handling-conduit-events/>`_ shard count. To delete
        shards, update the count to a lower number, and the shards above the count will be deleted. For example, if the
        existing shard count is 100, by resetting shard count to 50, shards 50-99 are disabled.

        :param conduit_id: Conduit ID.

        :param shard_count: The new number of shards for this conduit.

        :return: The updated conduit.
        """

        url = self.client.url + "eventsub/conduits"

        req = httpx.patch(url,
                          json={"id": conduit_id, "shard_count": shard_count},
                          headers=self.client.headers,
                          timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()["data"][0]

        return Conduit(id=res["id"],
                       shard_count=res["shard_count"])

    def delete_conduit(self,
                        conduit_id: str) -> None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#delete-conduit>`_

        Deletes a specified `conduit <https://dev.twitch.tv/docs/eventsub/handling-conduit-events/>`_. Note that it may
        take some time for Eventsub subscriptions on a deleted `conduit
        <https://dev.twitch.tv/docs/eventsub/handling-conduit-events/>`_ to show as disabled when calling ``eventsub.get_eventsub_subscriptions()``

        :param conduit_id: Conduit ID.
        """

        url = self.client.url + "eventsub/conduits"

        req = httpx.delete(url,
                           params={"id": conduit_id},
                           headers=self.client.headers,
                           timeout=self.client.timeout)
        req.raise_for_status()

    def get_conduit_shards(self,
                           conduit_id: str,
                           status: SubscriptionStatus = None,
                           after: Pagination = None) -> ConduitShard | tuple[ConduitShard, ...] | tuple[tuple[ConduitShard, ...], Pagination] | None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-conduit-shards>`_

        Returns a tuple of all shards for a `conduit <https://dev.twitch.tv/docs/eventsub/handling-conduit-events/>`_.

        :param conduit_id: Conduit ID.

        :param status: Status to filter by.

        :param after: The ``Pagination`` object to get the next page of results.

        :return: Tuple of information about a conduit's shards.
        """

        url = self.client.url + "eventsub/conduits/shards"

        parameters = {"conduit_id": conduit_id}

        optional_params = {
            "status": status,
            "after": after.cursor
        }

        for key, value in optional_params:
            if value: parameters[key] = value

        req = httpx.get(url,
                        params=parameters,
                        headers=self.client.headers,
                        timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()

        if len(res["data"]) < 1: return None

        shards = list()
        for shard in res:
            transport = NotificationTransport(method=NotificationTransportMethod(shard["transport"]["method"]),
                                              callback=shard["transport"]["callback"] if shard["transport"]["callback"] else None,
                                              secret=shard["transport"]["secret"] if shard["transport"]["secret"] else None,
                                              session_id=shard["transport"]["session_id"] if shard["transport"]["session_id"] else None,
                                              conduit_id=shard["transport"]["conduit_id"] if shard["transport"]["conduit_id"] else None,
                                              connected_at=shard["transport"]["connected_at"] if shard["transport"]["connected_at"] else None,
                                              disconnected_at=shard["transport"]["disconnected_at"] if shard["transport"]["disconnected_at"] else None)

            shards.append(ConduitShard(id=shard["id"],
                                       status=SubscriptionStatus(shard["status"]),
                                       transport=transport))

        if len(shards) < 2: return shards[0]

        if len(res["pagination"]) > 0: return tuple(shards), Pagination(res["pagination"]["cursor"])

        return tuple(shards)

    # TODO: Allow the update of multiple conduit shards
    def update_conduit_shards(self,
                              conduit_id: str,
                              shards: ConduitShard) -> ConduitShard:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#update-conduit-shards>`_

        Updates a shard for a `conduit <https://dev.twitch.tv/docs/eventsub/handling-conduit-events/>`_.

        :param conduit_id: Conduit ID.

        :param shards: Shard to update.

        :return: Updated shard.

        """

        url = self.client.url + "eventsub/conduits/shards"

        validation = {
            (not shards.status):
                "shards.status must be None",
            (shards.transport.method == NotificationTransportMethod.CONDUIT):
                "shards.transport.method can't be CONDUIT",
            (shards.transport.callback is None and shards.transport.secret is None and shards.transport.session_id is None):
                "shards.transport.callback, shards.transport.secret and shards.transport.session_id are mutually exclusive",
            (shards.transport.conduit_id is not None or shards.transport.connected_at is not None or shards.transport.disconnected_at is not None):
                "shards.transport.conduit_id, shards.transport.connected_at and shards.transport.disconnected_at must be None"
        }

        for condition, error in validation.items():
            if condition: raise ValueError(error)

        body = {
            "conduit_id": conduit_id,
            "shards": [{
                "id": shards.id,
                "transport": {
                    "method": shards.transport.method.value
                }
            }]
        }

        if shards.transport.session_id is not None: body["shards"][0]["transport"]["session_id"] = shards.transport.session_id
        else:
            body["shards"][0]["transport"]["callback"] = shards.transport.callback
            body["shards"][0]["transport"]["secret"] = shards.transport.secret

        req = httpx.patch(url,
                          json=body,
                          headers=self.client.headers,
                          timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()["data"][0]

        transport = NotificationTransport(
            method=NotificationTransportMethod(res["transport"]["method"]),
            callback=res["transport"]["callback"],
            secret=None,
            session_id=res["transport"]["session_id"],
            conduit_id=None,
            connected_at=res["transport"]["connected_at"],
            disconnected_at=res["transport"]["disconnected_at"])
        return ConduitShard(
            id=res["id"],
            status=None,
            transport=transport
        )
