from twitch_python_wrapper.api.client import APIClient


class Entitlements:
    def __init__(self, client: APIClient):
        self.client = client

    def get_drops_entitlements(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-drops-entitlements>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def update_drops_entitlements(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#update-drops-entitlements>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")
