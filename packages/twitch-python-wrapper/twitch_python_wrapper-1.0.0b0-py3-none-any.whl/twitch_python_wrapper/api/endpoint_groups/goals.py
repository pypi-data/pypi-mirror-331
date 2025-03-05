from twitch_python_wrapper.api.client import APIClient


class Goals:
    def __init__(self, client: APIClient):
        self.client = client

    def get_creator_goals(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-creator-goals>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")
