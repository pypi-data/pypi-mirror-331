from twitch_python_wrapper.api.client import APIClient


class Ads:
    def __init__(self, client: APIClient):
        self.client = client

    def start_commercial(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#start-commercial>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def get_ad_schedule(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-ad-schedule>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def snooze_next_ad(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#snooze-next-ad>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")
