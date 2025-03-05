class APIClient:
    """
    Twitch API client
    """

    def __init__(self,
                 client_id: str,
                 access_token: str,
                 timeout: float = 5.0) -> None:
        """
        Initializer of Twitch's API client.

        :param client_id: Twitch application client ID, see `step 9
            <https://dev.twitch.tv/docs/authentication/register-app/>`_.
        :param access_token: Twitch application access token. In future updates this will be managed by the wrapper, but
            until then see `Twitch application authentication <https://dev.twitch.tv/docs/authentication/>`_.
        :param timeout: Timeout in seconds used when making the endpoint requests, default is ``5.0``.
        """

        self.url = "https://api.twitch.tv/helix/"
        self.__headers = {
            "Authorization": "Bearer " + access_token,
            "Client-Id": client_id
        }
        self.timeout = timeout

        from twitch_python_wrapper.api.endpoint_groups.ads import Ads
        from twitch_python_wrapper.api.endpoint_groups.analytics import Analytics
        from twitch_python_wrapper.api.endpoint_groups.bits import Bits
        from twitch_python_wrapper.api.endpoint_groups.channels import Channels
        from twitch_python_wrapper.api.endpoint_groups.channel_points import ChannelPoints
        from twitch_python_wrapper.api.endpoint_groups.charity import Charity
        from twitch_python_wrapper.api.endpoint_groups.chat import Chat
        from twitch_python_wrapper.api.endpoint_groups.clips import Clips
        from twitch_python_wrapper.api.endpoint_groups.conduits import Conduits
        from twitch_python_wrapper.api.endpoint_groups.ccls import CCLs
        from twitch_python_wrapper.api.endpoint_groups.entitlements import Entitlements
        from twitch_python_wrapper.api.endpoint_groups.extensions import Extensions
        from twitch_python_wrapper.api.endpoint_groups.eventsub import EventSub
        from twitch_python_wrapper.api.endpoint_groups.games import Games
        from twitch_python_wrapper.api.endpoint_groups.goals import Goals
        from twitch_python_wrapper.api.endpoint_groups.hype_train import HypeTrain
        from twitch_python_wrapper.api.endpoint_groups.moderation import Moderation
        from twitch_python_wrapper.api.endpoint_groups.polls import Polls
        from twitch_python_wrapper.api.endpoint_groups.predictions import Predictions
        from twitch_python_wrapper.api.endpoint_groups.schedule import Schedule
        from twitch_python_wrapper.api.endpoint_groups.search import Search
        from twitch_python_wrapper.api.endpoint_groups.streams import Streams
        from twitch_python_wrapper.api.endpoint_groups.subscriptions import Subscriptions
        from twitch_python_wrapper.api.endpoint_groups.teams import Teams
        from twitch_python_wrapper.api.endpoint_groups.users import Users
        from twitch_python_wrapper.api.endpoint_groups.videos import Videos
        from twitch_python_wrapper.api.endpoint_groups.whispers import Whispers

        self.ads = Ads(self)
        self.analytics = Analytics(self)
        self.bits = Bits(self)
        self.channels = Channels(self)
        self.channel_points = ChannelPoints(self)
        self.charity = Charity(self)
        self.chat = Chat(self)
        self.clips = Clips(self)
        self.conduits = Conduits(self)
        self.ccls = CCLs(self)
        self.entitlements = Entitlements(self)
        self.extensions = Extensions(self)
        self.eventsub = EventSub(self)
        self.games = Games(self)
        self.goals = Goals(self)
        self.hype_train = HypeTrain(self)
        self.moderation = Moderation(self)
        self.polls = Polls(self)
        self.predictions = Predictions(self)
        self.schedule = Schedule(self)
        self.search = Search(self)
        self.streams = Streams(self)
        self.subscriptions = Subscriptions(self)
        self.teams = Teams(self)
        self.users = Users(self)
        self.videos = Videos(self)
        self.whispers = Whispers(self)

    @property
    def headers(self) -> dict:
        return self.__headers
