import httpx

from twitch_python_wrapper.api.client import APIClient
from twitch_python_wrapper.api.enums import ContentClassificationLabelId
from twitch_python_wrapper.api.objects import Channel


class Channels:
    def __init__(self, client: APIClient):
        self.client = client

    def get_channel_information(self,
                                broadcaster_id: str | list[str]) -> Channel | tuple[Channel, ...] | None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-channel-information>`_

        Gets information about one or more channels

        :param broadcaster_id: The ID of the broadcaster whose channel you want to get. To specify more than one ID,
            set this parameter to a list of each broadcaster you want to get. You may specify a maximum of 100 IDs.

        :return: A tuple that contains information about the specified channels. If it's just one channel just that
            object is returned. If the specified channel(s) weren't found it'll return None
        """

        url = self.client.url + "channels"

        if isinstance(broadcaster_id, list) and (len(broadcaster_id) < 1 or len(broadcaster_id) > 100):
            raise ValueError("Cannot look up for 100+ broadcaster IDs")

        req = httpx.get(url,
                        params={"broadcaster_id": broadcaster_id},
                        headers=self.client.headers,
                        timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()["data"]

        if len(res) < 1: return None

        channels = list()
        for channel in res:
            content_classification_labels = list()
            for label in channel["content_classification_labels"]:
                content_classification_labels.append(ContentClassificationLabelId(label))
            channels.append(Channel(
                broadcaster_id=channel["broadcaster_id"],
                broadcaster_login=channel["broadcaster_login"],
                broadcaster_name=channel["broadcaster_name"],
                broadcaster_language=channel["broadcaster_language"],
                game_name=channel["game_name"],
                game_id=channel["game_id"],
                title=channel["title"],
                delay=channel["delay"],
                tags=tuple(channel["tags"]),
                content_classification_labels=tuple(content_classification_labels),
                is_branded_content=channel["is_branded_content"]
            ))

        if len(channels) < 2: return channels[0]

        return tuple(channels)

    def modify_channel_information(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#modify-channel-information>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def get_channel_editors(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-channel-editors>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def get_followed_channels(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-followed-channels>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def get_channel_followers(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-channel-followers>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")
