import httpx
from dateutil.parser import isoparse

from twitch_python_wrapper.api.client import APIClient
from twitch_python_wrapper.api.objects import Pagination, Category, ChannelSearched


class Search:
    def __init__(self, client: APIClient):
        self.client = client

    def search_categories(self,
                          query: str,
                          first: int = None,
                          after: Pagination = None) -> Category | tuple[Category, ...] | tuple[tuple[Category, ...], Pagination] | None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#search-categories>`_

        Returns the games or categories that match the specified query.

        To match, the category's name must contain all parts of the query string. For example, if the query string is
            45, the response includes any category name that contains 42 in the title. If the query string is a phrase
            like *love computer*, the response includes any category name that contains the words love and computer
            anywhere in the name. The comparison is case-insensitive.

        :param query: The search string.

        :param first: The maximum number of items to return per page in the response. The minimum page size is 1 item
            per page and the maximum is 100 items per page. The default is 20

        :param after: The ``Pagination`` object to get the next page of results

        :return: A tuple of games or categories that match the query. Returns None if there are no matches.
        """

        url = self.client.url + "search/categories"

        if first and (first < 1 or first > 100): raise ValueError("Parameter first must be between 1 and 100")

        parameters = {"query": query}

        optional_params = {
            "first": first,
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

        if len(res["data"]) < 1: return None

        categories = list()
        for category in res["data"]:
            categories.append(Category(
                id=category["id"],
                name=category["name"],
                box_art_url="https://static-cdn.jtvnw.net/ttv-boxart/" + category["id"] + "-{width}x{height}.jpg",
                igdb_id=None
            ))

        if len(categories) < 2: return categories[0]

        if len(res["pagination"]) > 0: return tuple(categories), Pagination(cursor=res["pagination"]["cursor"])

        return tuple(categories)

    def search_channels(self,
                        query: str,
                        live_only: bool = None,
                        first: int = None,
                        after: Pagination = None) -> ChannelSearched | tuple[ChannelSearched, ...] | tuple[tuple[ChannelSearched, ...], Pagination] | None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#search-channels>`_

        Returns the channels that match the specified query and have streamed content within the past 6 months.

        The fields that the API uses for comparison depends on the value that the *live_only* query parameter is set to.
        If *live_only* is **false**, the API matches on the broadcaster’s login name. However, if *live_only* is **true**, the API
        matches on the broadcaster’s name and category name.

        To match, the beginning of the broadcaster’s name or category must match the query string. The comparison is
        case-insensitive. If the query string is angel_of_death, it matches all names that begin with angel_of_death.
        However, if the query string is a phrase like angel of death, it matches to names starting with angelofdeath or
        names starting with angel_of_death.

        By default, the results include both live and offline channels. To get only live channels set the *live_only*
        query parameter to **true**.

        :param query: The search string.

        :param live_only: A Boolean value that determines whether the response includes only channels that are currently
            streaming live. Set to **true** to get only channels that are streaming live; otherwise, **false** to get live and
            offline channels. The default is **false**.

        :param first: The maximum number of items to return per page in the response. The minimum page size is 1 item
            per page and the maximum is 100 items per page. The default is 20.

        :param after: The ``Pagination`` object to get the next page of results

        :return: A tuple of channels that match the query. Returns none if there are no matches.
        """

        url = self.client.url + "search/channels"

        if first and (first < 1 or first > 100): raise ValueError("Parameter first must be between 1 and 100")

        parameters = {"query": query}

        optional_params = {
            "live_only": live_only,
            "first": first,
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

        if len(res["data"]) < 1: return None

        channels = list()
        for channel in res["data"]:
            channels.append(ChannelSearched(
                broadcaster_language=channel["broadcaster_language"],
                broadcaster_login=channel["broadcaster_login"],
                display_name=channel["display_name"],
                game_id=channel["game_id"],
                game_name=channel["game_name"],
                id=channel["id"],
                is_live=channel["is_live"],
                tags=tuple(channel["tags"]),
                thumbnail_url=channel["thumbnail_url"],
                title=channel["title"],
                started_at=int(isoparse(channel["started_at"]).timestamp())
            ))

        if len(channels) < 2: return channels[0]

        if len(res["pagination"]) > 0: return tuple(channels), Pagination(cursor=res["pagination"]["cursor"])

        return tuple(channels)
