from twitch_python_wrapper.api.client import APIClient


class Whispers:
    def __init__(self, client: APIClient):
        self.client = client

    def send_whisper(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#send-whisper>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")
