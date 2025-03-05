from twitch_python_wrapper.api.client import APIClient


class HypeTrain:
    def __init__(self, client: APIClient):
        self.client = client

    def get_hype_train_events(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-hype-train-events>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")
