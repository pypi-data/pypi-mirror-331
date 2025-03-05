import httpx
from dateutil.parser import isoparse

from twitch_python_wrapper.api.client import APIClient
from twitch_python_wrapper.api.enums import EmoteType, EmoteFormat, EmoteThemeMode
from twitch_python_wrapper.api.objects import Emote, ChatBadgeSet, ChatBadge, ChatSettings, SharedChatSession, \
    SharedChatSessionParticipant, \
    UserChatColor


class Chat:
    def __init__(self, client: APIClient):
        self.client = client

    def get_chatters(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-chatters>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def get_channel_emotes(self,
                           broadcaster_id: str) -> tuple[Emote, str] | tuple[tuple[Emote, ...], str] | None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-channel-emotes>`_

        Returns the broadcaster's tuple of custom emotes. Broadcasters create these custom emotes for users who subscribe
        to or follow the channel or cheer Bits in the channel's chat window. `Learn More
        <https://dev.twitch.tv/docs/irc/emotes>`_

        For information about custom emotes, see `subscriber emotes
        <https://help.twitch.tv/s/article/subscriber-emote-guide>`_, `Bits tier emotes
        <https://help.twitch.tv/s/article/custom-bit-badges-guide?language=bg#slots>`_, and `follower emotes
        <https://blog.twitch.tv/en/2021/06/04/kicking-off-10-years-with-our-biggest-emote-update-ever/>`_.

        **NOTE:** Except custom follower emotes, users may use custom emotes in any Twitch chat.

        :param broadcaster_id: An ID that identifies the broadcaster whose emotes you want to get.

        :return: A tuple of emotes that the specified broadcaster created. If the broadcaster hasn't created custom
            emotes, this returns None.
        """

        url = self.client.url + "chat/emotes"

        req = httpx.get(url,
                        params={"broadcaster_id": broadcaster_id},
                        headers=self.client.headers,
                        timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()

        if len(res["data"]) < 1: return None

        emotes = list()
        for emote in res["data"]:
            formats = list()
            for emote_format in emote["format"]: formats.append(EmoteFormat(emote_format))
            scales = list()
            for scale in emote["scale"]: formats.append(scale)
            themes_modes = list()
            for theme_mode in emote["theme_mode"]: themes_modes.append(EmoteThemeMode(theme_mode))
            emotes.append(Emote(
                id=emote["id"],
                name=emote["name"],
                images=tuple(sorted((str(k), str(v)) for k, v in emote["images"].items())),
                tier=emote["tier"] if emote["tier"] != "" else None,
                emote_type=EmoteType(emote["emote_type"]),
                emote_set_id=emote["emote_set_id"],
                owner_id=None,
                format=tuple(formats),
                scale=tuple(scales),
                theme_mode=tuple(themes_modes)
            ))

        if len(emotes) < 2: return emotes[0], res["template"]

        return tuple(emotes), res["template"]

    def get_global_emotes(self) -> tuple[tuple[Emote, ...], str]:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-global-emotes>`_

        Returns a tuple of `global emotes <https://www.twitch.tv/creatorcamp/en/learn-the-basics/emotes/>`_. Global
        emotes are Twitch-created emotes that users can use in any Twitch chat.

        `Learn More <https://dev.twitch.tv/docs/irc/emotes>`_.

        :return: A tuple of global emotes and the emote URL template.
        """

        url = self.client.url + "chat/emotes/global"

        req = httpx.get(url,
                        headers=self.client.headers,
                        timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()

        emotes = list()
        for emote in res["data"]:
            formats = list()
            for emote_format in emote["format"]: formats.append(EmoteFormat(emote_format))
            scales = list()
            for scale in emote["scale"]: formats.append(scale)
            themes = list()
            for theme in emote["theme_mode"]: themes.append(EmoteThemeMode(theme))
            emotes.append(Emote(id=emote["id"],
                                name=emote["name"],
                                images=tuple(sorted((str(k), str(v)) for k, v in emote["images"].items())),
                                tier=None,
                                emote_type=None,
                                emote_set_id=None,
                                owner_id=None,
                                format=tuple(formats),
                                scale=tuple(scales),
                                theme_mode=tuple(themes)))

        return tuple(emotes), res["template"]

    def get_emote_sets(self,
                       emote_set_id: str | list[str]) -> tuple[Emote, str] | tuple[tuple[Emote, ...], str] | None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-emote-sets>`_

        Returns emotes for one or more specified emote sets.

        An emote set groups emotes that have a similar context. For example, Twitch places all the subscriber emotes
        that a broadcaster uploads for their channel in the same emote set.

        `Learn More <https://dev.twitch.tv/docs/irc/emotes>`_.

        :param emote_set_id: An ID that identifies the emote set to get. Set this parameter as a list for each emote set
            you want to get. You may specify a maximum of 25 IDs. The response contains only the IDs that were found and
            ignores duplicate IDs.
            To get emote set IDs, use the ``get_channel_emotes()`` method.

        :return: A tuple of emotes found in the specified emote sets. None if none of the IDs were found.
        """

        url = self.client.url + "chat/emotes/set"

        if isinstance(emote_set_id, list) and (len(emote_set_id) < 1 or len(emote_set_id) > 25):
            raise ValueError("Cannot look up for 25+ emote set IDs")

        req = httpx.get(url,
                        params={"emote_set_id": emote_set_id},
                        headers=self.client.headers,
                        timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()

        if len(res["data"]) < 1: return None

        emotes = list()
        for emote in res["data"]:
            formats = list()
            for emote_format in emote["format"]: formats.append(EmoteFormat(emote_format))
            scales = list()
            for scale in emote["scale"]: formats.append(scale)
            themes_modes = list()
            for theme_mode in emote["theme_mode"]: themes_modes.append(EmoteThemeMode(theme_mode))
            emotes.append(Emote(id=emote["id"],
                                name=emote["name"],
                                images=tuple(sorted((str(k), str(v)) for k, v in emote["images"].items())),
                                tier=None,
                                emote_type=EmoteType(emote["emote_type"]),
                                emote_set_id=emote["emote_set_id"],
                                owner_id=emote["owner_id"],
                                format=tuple(formats),
                                scale=tuple(scales),
                                theme_mode=tuple(themes_modes)))

        if len(emotes) < 2: return emotes[0], res["template"]

        return tuple(emotes), res["template"]

    def get_channel_chat_badges(self,
                                broadcaster_id: str) -> ChatBadgeSet | tuple[ChatBadgeSet, ...] | None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-channel-chat-badges>`_

        Gets the broadcaster's list of custom chat badges. The tuple is empty if the broadcaster hasn't created custom
        chat badges. For information about custom badges, see `subscriber badges
        <https://help.twitch.tv/s/article/subscriber-badge-guide>`_ and `Bits badges
        <https://help.twitch.tv/s/article/custom-bit-badges-guide>`_.

        :param broadcaster_id: The ID of the broadcaster whose chat badges you want to get.

        :return: A tuple of chat badges. The tuple is sorted in ascending order by ``set_id``, and within a set, the list is
            sorted in ascending order by ``id``.
        """

        url = self.client.url + "chat/badges"

        req = httpx.get(url,
                        params={"broadcaster_id": broadcaster_id},
                        headers=self.client.headers,
                        timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()["data"]

        if len(res) < 1: return None

        badge_sets = list()
        for badges_set in res:
            badges = list()
            for badge in badges_set["versions"]:
                badges.append(ChatBadge(id=badge["id"],
                                        image_url_1x=badge["image_url_1x"],
                                        image_url_2x=badge["image_url_2x"],
                                        image_url_4x=badge["image_url_4x"],
                                        title=badge["title"],
                                        description=badge["description"],
                                        click_action=badge["click_action"],
                                        click_url=badge["click_url"]))

            badge_sets.append(ChatBadgeSet(set_id=badges_set["set_id"],
                                           versions=tuple(badges)))

        if len(badge_sets) < 2: return badge_sets[0]

        return tuple(badge_sets)

    def get_global_chat_badges(self) -> tuple[ChatBadgeSet, ...]:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-global-chat-badges>`_

        Returns Twitch's tuple of chat badges, which users may use in any channel's chat room. For information about
        chat badges, see `Twitch Chat Badges Guide <https://help.twitch.tv/s/article/twitch-chat-badges-guide>`_.

        :return: A tuple of chat badges. The tuple is sorted in ascending order by ``set_id``, and within a set, the
        tuple is sorted n ascending order by ``ìd``.
        """

        url = self.client.url + "chat/badges/global"

        req = httpx.get(url,
                        headers=self.client.headers,
                        timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()["data"]

        badge_sets = list()
        for badges_set in res:
            badges = list()
            for badge in badges_set["versions"]:
                badges.append(ChatBadge(id=badge["id"],
                                        image_url_1x=badge["image_url_1x"],
                                        image_url_2x=badge["image_url_2x"],
                                        image_url_4x=badge["image_url_4x"],
                                        title=badge["title"],
                                        description=badge["description"],
                                        click_action=badge["click_action"],
                                        click_url=badge["click_url"]))

            badge_sets.append(ChatBadgeSet(set_id=badges_set["set_id"],
                                           versions=tuple(badges)))

        return tuple(badge_sets)

    def get_chat_settings(self,
                          broadcaster_id: str,
                          moderator_id: str = None) -> ChatSettings:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-chat-settings>`_

        Returns the broadcaster's chat settings.

        For an overview of chat settings, see `Chat Commands for Broadcasters and Moderators
        <https://help.twitch.tv/s/article/chat-commands#AllMods>`_ and `Moderator Preferences
        <https://help.twitch.tv/s/article/setting-up-moderation-for-your-twitch-channel#modpreferences>`_

        :param broadcaster_id: The ID of the broadcaster whose chat settings you want to get. Required

        :param moderator_id: The ID of the broadcaster or one of the broadcaster's moderators. This field is required
            only if you want to include the ``non_moderator_chat_delay`` and ``non_moderator_chat_delay_duration``
            settings in the response. If you specify this field, this ID must match the user ID in the user access token

        :return: The chat settings
        """

        url = self.client.url + "chat/settings"

        parameters = {"broadcaster_id": broadcaster_id}

        optional_params = {
            "moderator_id": moderator_id
        }

        for key, value in optional_params.items():
            if value: parameters[key] = value

        req = httpx.get(url,
                        params=parameters,
                        headers=self.client.headers,
                        timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()["data"][0]

        return ChatSettings(broadcaster_id=res["broadcaster_id"],
                            emote_mode=res["emote_mode"],
                            follower_mode=res["follower_mode"],
                            follower_mode_duration=res["follower_mode_duration"],
                            moderator_id=res["moderator_id"] if "moderator_id" in res else None,
                            non_moderator_chat_delay=res["non_moderator_chat_delay"] if "non_moderator_chat_delay" in res else None,
                            non_moderator_chat_delay_duration=res["non_moderator_chat_delay_duration"] if "non_moderator_chat_delay_duration" in res else None,
                            slow_mode=res["slow_mode"],
                            slow_mode_wait_time=res["slow_mode_wait_time"],
                            subscriber_mode=res["subscriber_mode"],
                            unique_chat_mode=res["unique_chat_mode"])

    def get_shared_chat_session(self,
                                broadcaster_id: str) -> SharedChatSession:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-shared-chat-session>`_

        Returns the active shared chat session for a channel

        :param broadcaster_id: The User ID of the channel broadcaster

        :return: The active shared chat session
        """

        url = self.client.url + "shared_chat/session"

        req = httpx.get(url,
                        params={"broadcaster_id": broadcaster_id},
                        headers=self.client.headers,
                        timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()["data"][0]

        participants = list()
        for participant in res["participants"]:
            participants.append(SharedChatSessionParticipant(broadcaster_id=participant["broadcaster_id"]))

        return SharedChatSession(session_id=res["session_id"],
                                 host_broadcaster_id=res["host_broadcaster_id"],
                                 participants=tuple(participants),
                                 created_at=int(isoparse(res["created_at"]).timestamp()),
                                 updated_at=int(isoparse(res["updated_at"]).timestamp()))

    def get_user_emotes(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-user-emotes>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def update_chat_settings(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#update-chat-settings>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def send_chat_announcement(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#send-chat-announcement>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def send_a_shoutout(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#send-a-shoutout>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def send_chat_message(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#send-chat-message>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def get_user_chat_color(self,
                            user_id: str | list[str]) -> UserChatColor | tuple[UserChatColor, ...] | None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-user-chat-color>`_

        Returns the color used for the user's name in chat

        :param user_id: The ID o the user whose username color you want to get. To specify more than one user, set this
        parameter to a list for each user to get. The maximum number of IDs that you may specify is 100.

        :return: The user(s) chat color the use for their name
        """

        url = self.client.url + "chat/color"

        if isinstance(user_id, list) and (len(user_id) < 1 or len(user_id) > 100):
            raise ValueError("Cannot look up for 100+ user IDs")

        req = httpx.get(url,
                        params={"user_id": user_id},
                        headers=self.client.headers,
                        timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()["data"]

        if len(res) < 1: return None

        users = list()
        for user in res:
            users.append(UserChatColor(
                user_id=user["user_id"],
                user_login=user["user_login"],
                user_name=user["user_name"],
                color=user["color"] if user["color"] != "" else None
            ))

        if len(users) < 2: return users[0]

        return tuple(users)

    def update_user_chat_color(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#update-user-chat-color>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")
