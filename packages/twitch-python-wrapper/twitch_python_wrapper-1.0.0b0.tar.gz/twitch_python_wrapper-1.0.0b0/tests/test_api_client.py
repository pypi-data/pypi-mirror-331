import os

from dotenv import load_dotenv

from twitch_python_wrapper.api.client import APIClient

load_dotenv()

class TestAPIClient:
    client = APIClient(os.getenv("CLIENT_ID"), os.getenv("APP_ACCESS_TOKEN"))

    def test_get_users(self):
        assert self.client.users.get_users(login="foo_bar_baz_qux") is None
        assert hash(self.client.users.get_users(login="twitchdev")) == 95983915723945059
        assert hash(self.client.users.get_users(user_id="141981764")) == 95983915723945059
        us = self.client.users.get_users(login=["twitchdev", "twitch"])
        for u in us:
            h = hash(u)
            assert h == 95983915723945059 or h == -4084956926418039017
        us = self.client.users.get_users(user_id=["141981764", "12826"])
        for u in us:
            h = hash(u)
            assert h == 95983915723945059 or h == -4084956926418039017
        us = self.client.users.get_users(login="twitchdev", user_id="12826")
        for u in us:
            h = hash(u)
            assert h == 95983915723945059 or h == -4084956926418039017

    def test_get_videos(self):
        assert self.client.videos.get_videos(video_id="123456789123") is None
        assert hash(self.client.videos.get_videos(video_id="335921245")) == 4462134045647488878

    def test_get_clips(self):
        assert self.client.clips.get_clips(clip_id="AwkwardHelplessSalamanderSwiftRage") is None
        assert hash(self.client.clips.get_clips(clip_id="ObedientRelievedPepperoniSwiftRage")) == 4781649331344373151
        assert hash(self.client.clips.get_clips(broadcaster_id="141981764", first=5)) == 5772613717331245050

    def test_get_cheermotes(self):
        assert hash(self.client.bits.get_cheermotes(broadcaster_id="141981764")) == -3447302537155689151

    def test_get_channel_information(self):
        assert hash(self.client.channels.get_channel_information(broadcaster_id="141981764")) == -3908995204320117461
        assert hash(self.client.channels.get_channel_information(broadcaster_id="12826")) == 5805505296450211110
        assert hash(self.client.channels.get_channel_information(broadcaster_id=["141981764", "12826"])) == 1514345465058598088

    def test_get_channel_emotes(self):
        assert hash(self.client.chat.get_channel_emotes(broadcaster_id="141981764")) == 196265680831279960
        assert hash(self.client.chat.get_channel_emotes(broadcaster_id="12826")) == -5584805614351045098

    def test_get_emote_sets(self):
        assert hash(self.client.chat.get_emote_sets(emote_set_id="301590448")) == 8199447653793326264
        assert hash(self.client.chat.get_emote_sets(emote_set_id="374814395")) == -1838195492418291180

    def test_get_channel_chat_badges(self):
        assert hash(self.client.chat.get_channel_chat_badges(broadcaster_id="12826")) ==8269109171712613325
        assert hash(self.client.chat.get_channel_chat_badges(broadcaster_id="197886470")) == -3076710540262200488

    def test_get_global_chat_badges(self):
        assert hash(self.client.chat.get_global_chat_badges()) == -2677478051108591865

    def test_get_chat_settings(self):
        assert hash(self.client.chat.get_chat_settings(broadcaster_id="141981764")) == 8585977543539151482
        assert hash(self.client.chat.get_chat_settings(broadcaster_id="12826")) == -1391188202663767236

    def test_get_user_chat_color(self):
        assert hash(self.client.chat.get_user_chat_color(user_id="141981764")) == 8406074055112061289
        assert hash(self.client.chat.get_user_chat_color(user_id="12826")) == 7968065401081294306

    def test_get_content_classification_labels(self):
        assert hash(self.client.ccls.get_content_classification_labels(locale="en-US")) == -4466657788493661200

    def test_get_games(self):
        assert hash(self.client.games.get_games(name="Just Chatting")) == -9147344911711028063
        assert hash(self.client.games.get_games(game_id="509658")) == -9147344911711028063
        gs = self.client.games.get_games(name=["Just Chatting", "Software and Game Development"])
        for g in gs:
            h = hash(g)
            assert h == -9147344911711028063 or h == -4867558018606174595
        gs = self.client.games.get_games(game_id=["509658", "1469308723"])
        for g in gs:
            h = hash(g)
            assert h == -9147344911711028063 or h == -4867558018606174595
        gs = self.client.games.get_games(name="Just Chatting", game_id="1469308723")
        for g in gs:
            h = hash(g)
            assert h == -9147344911711028063 or h == -4867558018606174595

    def test_get_channel_teams(self):
        assert hash(self.client.teams.get_channel_teams(broadcaster_id="96909659")) == 8370246977236723964
