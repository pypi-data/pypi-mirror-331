from twitch_python_wrapper.api.client import APIClient


class Charity:
    def __init__(self, client: APIClient):
        self.client = client

    def get_charity_campaign(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-charity-campaign>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def get_charity_campaign_donations(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-charity-campaign-donations>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")
