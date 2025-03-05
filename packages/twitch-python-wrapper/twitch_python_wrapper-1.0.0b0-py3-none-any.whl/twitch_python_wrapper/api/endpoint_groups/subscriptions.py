from twitch_python_wrapper.api.client import APIClient


class Subscriptions:
    def __init__(self, client: APIClient):
        self.client = client

    def get_broadcaster_subscriptions(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-broadcaster-subscriptions>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def check_user_subscription(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#check-user-subscription>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")
