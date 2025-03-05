import httpx
from dateutil.parser import isoparse

from twitch_python_wrapper.api.client import APIClient
from twitch_python_wrapper.api.enums import CheermoteType
from twitch_python_wrapper.api.objects import Cheermote, CheerTier


class Bits:
    def __init__(self, client: APIClient):
        self.client = client

    def get_bits_leaderboard(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-bits-leaderboard>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """
        raise NotImplementedError("Not Implemented Yet")

    def get_cheermotes(self,
                       broadcaster_id: str = None) -> tuple[Cheermote, ...]:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-cheermotes>`_

        Returns a tuple of Cheermotes that users can use to cheer Bits in any Bits-enabled channel's chat room.
        Cheermotes are animated emotes that viewers can assign Bits to.

        :param broadcaster_id: The ID of the broadcaster whose custom Cheermotes you want to get. Specify the
            broadcaster's ID if you want to include the broadcaster's Cheermotes in the response (not all broadcasters
            upload Cheermotes). If not specified, the response contains only global Cheermotes. If the broadcaster uploaded
            Cheermotes, the ``type`` field in the response is set to **channel_custom**.

        :return: A tuple of Cheermotes. The list is in ascending order by the ``order`` field's value.
        """

        url = self.client.url + "bits/cheermotes"

        if broadcaster_id: parameters = {"broadcaster_id": broadcaster_id}
        else: parameters = {}

        req = httpx.get(url,
                        params=parameters,
                        headers=self.client.headers,
                        timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()["data"]

        cheermotes = list()
        for cheermote in res:
            cheer_tiers = list()
            for tier in cheermote["tiers"]:
                cheer_tiers.append(CheerTier(min_bits=tier["min_bits"],
                                       id=tier["id"],
                                       color=tier["color"],
                                       images=tuple(sorted((str(k), str(v)) for k, v in tier["images"].items())),
                                       can_cheer=tier["can_cheer"],
                                       show_in_bits_card=tier["show_in_bits_card"]))

            cheermotes.append(Cheermote(prefix=cheermote["prefix"],
                                        tiers=tuple(cheer_tiers),
                                        type=CheermoteType(cheermote["type"]),
                                        order=cheermote["order"],
                                        last_update=int(isoparse(cheermote["last_updated"]).timestamp()),
                                        is_charitable=cheermote["is_charitable"]))

        return tuple(cheermotes)

    def get_extension_transactions(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-extension-transactions>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")
