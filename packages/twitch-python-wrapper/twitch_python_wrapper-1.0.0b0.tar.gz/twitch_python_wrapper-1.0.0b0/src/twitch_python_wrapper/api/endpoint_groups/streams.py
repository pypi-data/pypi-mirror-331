from typing import Literal

import httpx
from dateutil.parser import isoparse

from twitch_python_wrapper.api.client import APIClient
from twitch_python_wrapper.api.objects import Pagination, Stream


class Streams:
    def __init__(self, client: APIClient):
        self.client = client

    def get_stream_key(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-stream-key>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def get_streams(self,
                    user_id: str | list[str] = None,
                    user_login: str | list[str] = None,
                    game_id: str | list[str] = None,
                    stream_type: Literal["all", "live"] = None,
                    language: str = None,
                    first: int = None,
                    before: Pagination = None,
                    after: Pagination = None) -> Stream | tuple[Stream, ...] | tuple[tuple[Stream, ...], Pagination] | None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-streams>`_

        Returns a tuple of all streams. The tuple is in descending order by the number of viewers watching the stream.
        Because viewers come and go during a stream, it’s possible to find duplicate or missing streams in the list as
        you page through the results.

        :param user_id: A user ID used to filter the list of streams. Returns only the streams of those users that are
            broadcasting. You may specify a maximum of 100 IDs. To specify multiple IDs, set this parameter to a list
            for each user.

        :param user_login: A user login name used to filter the list of streams. Returns only the streams of those users
            that are broadcasting. You may specify a maximum of 100 login names. To specify multiple names, set this
            parameter to a list for each user.

        :param game_id: A game (category) ID used to filter the list of streams. Returns only the streams that are
            broadcasting the game (category). You may specify a maximum of 100 IDs. To specify multiple IDs, set this
            parameter to a list for each game.

        :param stream_type: The type of stream to filter the list of streams by. Possible values are: "all" and "live".
            The default is *all*.

        :param language: A language code used to filter the list of streams. Returns only streams that broadcast in the
            specified language. Specify the language using an ISO 639-1 two-letter language code or *other* if the
            broadcast uses a language not in the list of `supported stream languages
            <https://help.twitch.tv/s/article/languages-on-twitch#streamlang>`_. You may specify a maximum of 100
            language codes. To specify multiple languages, set this parameter to a list for each language.

        :param first: 	The maximum number of items to return per page in the response. The minimum page size is 1 item
            per page and the maximum is 100 items per page. The default is 20.

        :param before: The ``Pagination`` object to get the previous page of results.

        :param after: The ``Pagination`` object to get the next page of results.

        :return: A tuple of streams.
        """

        url = self.client.url + "streams"

        validation = {
            (isinstance(user_id, list) and (len(user_id) < 1 or len(user_id) > 100)):
                "Cannot look up for 100+ user IDs",
            (isinstance(user_login, list) and (len(user_login) < 1 or len(user_login) > 100)):
                "Cannot look up for 100+ user logins",
            (isinstance(game_id, list) and (len(game_id) < 1 or len(game_id) > 100)):
                "Cannot look up for 100+ game IDs",
            (language and language != "other" and len(language) != 2):
                "Parameter language must be a two-letter language code or 'other'",
            (first and (first < 1 or first > 100)):
                "Parameter first must be between 1 and 100"
        }

        for condition, error in validation.items():
            if condition: raise ValueError(error)

        parameters = {}

        optional_params = {
            "user_id": user_id,
            "user_login": user_login,
            "game_id": game_id,
            "type": stream_type,
            "language": language,
            "first": first,
            "before": before.cursor if before else None,
            "after": after.cursor if after else None
        }

        for key, value in optional_params.items():
            if value: parameters[key] = value

        req = httpx.get(url,
                        params=parameters,
                        headers=self.client.headers,
                        timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()

        streams = list()
        for stream in res["data"]:
            streams.append(Stream(
                id=stream["id"],
                user_id=stream["user_id"],
                user_login=stream["user_login"],
                user_name=stream["user_name"],
                game_id=stream["game_id"],
                game_name=stream["game_name"],
                type=stream["type"] if stream["type"] != "" else None,
                title=stream["title"],
                tags=tuple(stream["tags"]),
                viewer_count=stream["viewer_count"],
                started_at=int(isoparse(stream["started_at"]).timestamp()),
                language=stream["language"],
                thumbnail_url=stream["thumbnail_url"],
                is_mature=stream["is_mature"]
            ))

        if len(streams) < 2: return streams[0]

        if len(res["pagination"]) > 0: return tuple(streams), Pagination(res["pagination"]["cursor"])

        return tuple(streams)

    def get_followed_streams(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-followed-streams>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def create_stream_marker(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#create-stream-marker>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def get_stream_markers(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-stream-markers>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")
