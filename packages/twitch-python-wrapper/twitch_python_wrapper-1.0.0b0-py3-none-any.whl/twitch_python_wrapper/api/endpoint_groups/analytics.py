from twitch_python_wrapper.api.client import APIClient


class Analytics:
    def __init__(self, client: APIClient):
        self.client = client

    def get_extension_analytics(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-extension-analytics>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def get_game_analytics(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-game-analytics>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")
