from twitch_python_wrapper.api.client import APIClient


class Raids:
    def __init__(self, client: APIClient):
        self.client = client

    def start_a_raid(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#start-a-raid>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def cancel_a_raid(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#cancel-a-raid>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")
