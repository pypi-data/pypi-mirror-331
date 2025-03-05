from typing import Literal

import httpx
from dateutil.parser import isoparse

from twitch_python_wrapper.api.client import APIClient
from twitch_python_wrapper.api.enums import VideoType
from twitch_python_wrapper.api.objects import Pagination, Video, MutedSegment


class Videos:
    def __init__(self, client: APIClient):
        self.client = client

    def get_videos(self,
                   video_id: str | list[str] = None,
                   user_id: str = None,
                   game_id: str = None,
                   language: str = None,
                   period: Literal["all", "day", "month", "week"] = None,
                   sort: Literal["time", "trending", "views"] = None,
                   video_type: Literal["all", "archive", "highlight", "upload"] = None,
                   first: int = None,
                   after: Pagination = None,
                   before: Pagination = None) -> Video | tuple[Video, ...] | tuple[tuple[Video, ...], Pagination] | None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-videos>`_

        Returns information about one or more published videos. You may get videos by ID, by user, or by game/category.

        You may apply several filters to get a subset of the videos. The filters are applied as an AND operation to each
        video. For example, if *language* is set to ‘de’ and *game_id* is set to 21779, the response includes only videos
        that show playing League of Legends by users that stream in German. The filters apply only if you get videos by
        user ID or game ID.

        :param video_id: IDs that identify the videos you want to get. To get more than one video, set this parameter to
            a list for each video you want to get. Yoy may specify a maximum of 100 IDs. The *video_id*, *user_id*, and
            *game_id* parameters are mutually exclusive.

        :param user_id: The ID of the user whose list of videos you want to get. The *video_id*, *user_id*, and
            *game_id* parameters are mutually exclusive.

        :param game_id: A category or game ID. The response contains a maximum of 500 videos that show this content. To
        get category/game IDs, use the ``search.search_categories()`` function. The *video_id*, *user_id*, and *game_id*
        parameters are mutually exclusive.

        :param language: A filter used to filter the list of videos by the language that the video owner broadcasts in.
            For example, to get videos that were broadcast in German, set this parameter to the ISO 639-1 two-letter
            code for German (i.e., DE). For a list of supported languages, see `Supported Stream Language
            <https://help.twitch.tv/s/article/languages-on-twitch#streamlang>`_. If the language is not supported, use
            “other.” Specify this parameter only if you specify the *game_id* parameter.

        :param period: A filter used to filter the list of videos by when they were published. For example, videos
            published in the last week. Possible values are: all, day. month and week The default is "all", which
            returns videos published in all periods. Specify this parameter only if you specify the *game_id* or
            *user_id* parameter.

        :param sort: The order to sort the returned videos in. Possible values are: time, trending and views. The
            default is "time". Specify this parameter only if you specify the *game_id* or *user_id* parameter.

        :param video_type: A filter used to filter the list of videos by the video's type. Possible case-sensitive
            values are: all, archive, highlight and upload. The default is "all", which returns all video types. Specify
            this parameter only if you specify the *game_id* or *user_id* parameter.

        :param first: The maximum number of items to return per page in the response. The minimum page size is 1 item
        per page and the maximum is 100. The default is 20. Specify this parameter only if you specify the *game_id* or
        *user_id* parameter.

        :param after: The ``Pagination`` object to get the next page of results. Specify this parameter only if you
            specify the *game_id* or *user_id* query parameter.

        :param before: The ``Pagination`` object to get the previous page of results. Specify this parameter only if you
            specify the *game_id* or *user_id* query parameter.

        :return: A tuple of published videos that match the filter criteria.
        """

        url = self.client.url + "videos"

        validation = {
            (video_id is None and user_id is None and game_id is None):
                "Parameters video_id, user_id and game_id are mutually exclusive",
            (isinstance(video_id, list) and (len(video_id) < 1 or len(video_id) > 100)):
                "Cannot look up for 100+ video IDs",
            (language and language != "other" and len(language) != 2):
                "Parameter language must be a two-letter language code or 'other'",
            (language and game_id is None):
                "If you supply language then you must also supply game_id",
            (period and (game_id is None and user_id is None)):
                "If you supply period then you must also supply game_id or user_id",
            (sort and (game_id is None and user_id is None)):
                "If you supply sort then you must also supply game_id or user_id",
            (video_type and (game_id is None and user_id is None)):
                "If you supply video_type then you must also supply game_id or user_id",
            (first and (game_id is None and user_id is None)):
                "If you supply first then you must also supply game_id or user_id",
            (after and user_id is None):
                "If you supply after then you must also supply a user_id",
            (before and user_id is None):
                "If you supply before then you must also supply user_id",
            (first and (first < 1 or first > 100)):
                "Parameter first must be between 1 and 100"
        }

        for condition, error in validation.items():
            if condition: raise ValueError(error)

        parameters = {}

        optional_params = {
            "id": video_id,
            "user_id": user_id,
            "game_id": game_id,
            "language": language,
            "period": period,
            "sort": sort,
            "video_type": video_type,
            "first": first,
            "after": after.cursor if after else None,
            "before": before.cursor if before else None
        }

        for key, value in optional_params.items():
            if value: parameters[key] = value

        req = httpx.get(url,
                        params=parameters,
                        headers=self.client.headers,
                        timeout=self.client.timeout)

        if req.status_code == 404: return None

        req.raise_for_status()
        res = req.json()

        if len(res["data"]) < 1: return None

        videos = list()
        for video in res["data"]:
            muted_segments = list()
            if video["muted_segments"]:
                for segment in video["muted_segments"]:
                    muted_segments.append(MutedSegment(
                        duration=segment["duration"],
                        offset=segment["offset"]
                    ))

            videos.append(Video(
                id=video["id"],
                stream_id=video["stream_id"],
                user_id=video["user_id"],
                user_login=video["user_login"],
                user_name=video["user_name"],
                title=video["title"],
                description=video["description"],
                created_at=int(isoparse(video["created_at"]).timestamp()),
                published_at=int(isoparse(video["published_at"]).timestamp()),
                url=video["url"],
                thumbnail_url=video["thumbnail_url"],
                viewable=video["viewable"],
                view_count=video["view_count"],
                language=video["language"],
                type=VideoType(video["type"]),
                duration=video["duration"],
                muted_segments=tuple(muted_segments)
            ))

        if len(videos) < 2: return videos[0]

        if len(res["pagination"]) > 0: return tuple(videos), Pagination(res["pagination"]["cursor"])

        return tuple(videos)

    def delete_videos(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#delete-videos>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")
