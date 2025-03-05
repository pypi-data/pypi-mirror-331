from twitch_python_wrapper.api.client import APIClient


class Predictions:
    def __init__(self, client: APIClient):
        self.client = client

    def get_predictions(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-predictions>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def create_prediction(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#create-prediction>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def end_prediction(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#end-prediction>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")
