from twitch_python_wrapper.api.client import APIClient


class Polls:
    def __init__(self, client: APIClient):
        self.client = client

    def get_polls(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-polls>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def create_poll(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#create-poll>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def end_poll(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#end-poll>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")
