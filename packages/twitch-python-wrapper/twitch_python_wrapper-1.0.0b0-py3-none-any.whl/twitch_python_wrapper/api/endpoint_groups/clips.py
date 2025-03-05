from datetime import datetime

import httpx
import pytz
from dateutil.parser import isoparse

from twitch_python_wrapper.api.client import APIClient
from twitch_python_wrapper.api.objects import Pagination, Clip


class Clips:
    def __init__(self, client: APIClient):
        self.client = client

    def create_clip(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#create-clip>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def get_clips(self,
                  broadcaster_id: str = None,
                  game_id: str = None,
                  clip_id: str | list[str] = None,
                  started_at: int = None,
                  ended_at: int = None,
                  first: int = None,
                  before: Pagination = None,
                  after: Pagination = None,
                  is_featured: bool = None) -> Clip | tuple[Clip, ...] | tuple[tuple[Clip, ...], Pagination] | None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-clips>`_

        Returns one or more video clips that were captured from streams. For information about clips, see
        `How to use clips <https://help.twitch.tv/s/article/how-to-use-clips>`_.

        When using pagination for clips, note that the maximum number of results returned over multiple requests will be
        approximately 1,000. If additional results are necessary, paginate over different query parameters such as
        multiple ``started_at`` and ``ended_at`` timeframes to refine the search.

        :param broadcaster_id: An ID that identifies the broadcaster whose video clips you want to get. Use this
            parameter to get clips that were captured from the broadcaster's streams.

        :param game_id: An ID that identifies the game whose clips you want to get. Use this parameter to get clips that
            were captured from streams that were playing this game.

        :param clip_id: An ID that identifies the clip to get. To specify more than one ID, set this parameter to a list
            of each clip you want to get. You may specify a maximum of 100 IDs.

        :param started_at: The start date used to filter clips. The API returns only clips within the start and end date
            window. Specify the date and time in seconds timestamp.

        :param ended_at: The end date used to filter clips. If not specified, the time windows is the start date plus
            one week. Specify the date and time in seconds timestamp.

        :param first: The maximum number of clips to return per page in the response. The minimum page size is 1 clip
            per page and the maximum is 100. The default is 20.

        :param before: The ``Pagination`` object to get the previous page of results.

        :param after: The ``Pagination`` object to get the next page of results.

        :param is_featured: A Boolean value that determines whether the tuple includes featured clips. If **true**,
            returns only clips that are featured. If **false**, returns only clips that aren't featured. All clips are
            returned if this parameter is not set (or set to ``None``)

        :return: A tuple of video clips. For clips returned by *game_id* or *broadcaster_id*, the tuple is in descending
            order by view count. For tuples returned by *id*, te list is in the same order as the input IDs.

        :raise ValueError: If broadcaster_id, game_id nor clip_id are specified, all three of them are mutually
            exclusive; If clip_id is a list and that list has more than 100 IDs; If first isn't between 1 and 100.

        """

        url = self.client.url + "clips"

        validation = {
            (broadcaster_id is None and game_id is None and clip_id is None):
                "Parameters broadcaster_id, game_id and clip_id are mutually exclusive",
            (isinstance(clip_id, list) and (len(clip_id) < 1 or len(clip_id) > 100)):
                "Cannot look up for clip 100+ IDs",
            (first and (first < 1 or first > 100)):
                "Parameter first must be between 1 and 100"
        }

        for condition, error in validation.items():
            if condition: raise ValueError(error)

        parameters = {}

        optional_params = {
            "broadcaster_id": broadcaster_id,
            "game_id": game_id,
            "id": clip_id,
            "started_at": datetime.fromtimestamp(started_at, tz=pytz.utc).isoformat("T")[:-6] + "Z" if started_at else None,
            "ended_at": datetime.fromtimestamp(ended_at, tz=pytz.utc).isoformat("T")[:-6] + "Z" if ended_at else None,
            "first": first,
            "before": before.cursor if before else None,
            "after": after.cursor if after else None,
            "is_featured": is_featured
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

        clips = list()
        for clip in res["data"]:
            clips.append(Clip(
                id=clip["id"],
                url=clip["url"],
                embed_url=clip["embed_url"],
                broadcaster_id=clip["broadcaster_id"],
                broadcaster_name=clip["broadcaster_name"],
                creator_id=clip["creator_id"],
                creator_name=clip["creator_name"],
                video_id=clip["video_id"] if clip["video_id"] != "" else None,
                game_id=clip["game_id"],
                language=clip["language"],
                title=clip["title"],
                view_count=clip["view_count"],
                created_at=int(isoparse(clip["created_at"]).timestamp()),
                thumbnail_url=clip["thumbnail_url"],
                duration=clip["duration"],
                vod_offset=clip["vod_offset"],
                is_featured=clip["is_featured"]
            ))

        if len(clips) < 2: return clips[0]

        if len(res["pagination"]) > 0: return tuple(clips), Pagination(res["pagination"]["cursor"])

        return tuple(clips)
