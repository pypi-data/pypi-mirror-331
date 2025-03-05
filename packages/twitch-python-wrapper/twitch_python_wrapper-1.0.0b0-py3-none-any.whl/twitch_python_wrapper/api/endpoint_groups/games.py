import httpx

from twitch_python_wrapper.api.client import APIClient
from twitch_python_wrapper.api.objects import Pagination, Category


class Games:
    def __init__(self, client: APIClient):
        self.client = client

    def get_top_games(self,
                      first: int = None,
                      after: Pagination = None,
                      before: Pagination = None) -> tuple[Category, ...] | tuple[tuple[Category, ...], Pagination]:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-top-games>`_

        Returns information about all broadcasts on Twitch

        :param first: The maximum number of items to return per page in the response. The minimum page size is 1 item
            per page and thw maximum is 100 items per page. The default is 20.

        :param after: The ``Pagination`` object to get the next page of results.

        :param before: The ``Pagination`` object to get the previous page of results.

        :return: A tuple of broadcasts. The broadcasts are sorted by the number of viewers, with the mos popular first.
        """

        url = self.client.url + "games/top"

        if first and (first < 1 or first > 100): raise ValueError("Parameter first must be between 1 and 100")

        parameters = {}

        optional_params = {
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
        req.raise_for_status()
        res = req.json()

        games = list()
        for game in res["data"]:
            games.append(Category(
                id=game["id"],
                name=game["name"],
                box_art_url=game["box_art_url"],
                igdb_id=game["igdb_id"] if game["igdb_id"] != "" else None
            ))

        if len(res["pagination"]) > 0: return tuple(games), Pagination(res["pagination"]["cursor"])

        return tuple(games)

    def get_games(self,
                  game_id: str | list[str] = None,
                  name: str | list[str] = None,
                  igdb_id: str | list[str] = None) -> Category | tuple[Category, ...] | None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-games>`_

        Returns information about specified categories or games.

        You may get up to 100 categories or games by specifying their ID or name. You may specify all IDs, all names or
        a combination of IDs and names. If you specify a combination of Ids and names, the total number of IDs and names
        must not exceed 100.

        :param game_id: The ID of the category or game to get. Set this parameter to a list for each category or game
            you want to get. You may specify a maximum of 100 IDs.

        :param name: The name of the category or game you want to get. The name must exactly match the category's or
            game's title. Set this parameter to a list for each category or game you want to get. You may specify a
            maximum of 100 names.

        :param igdb_id: The `IGDB <https://www.igdb.com/>`_ ID of the game to get. Set this parameter to a list for each
            game you want to get. You may specify a maximum of 100 IDs.

        :return:

        :raise ValueError: If game_id, name and/or igdb_id are a list and those/that list(s) has more than 100 IDs in
            total.
        """

        url = self.client.url + "games"

        sum_of_lookups = 0

        if isinstance(game_id, list): sum_of_lookups += len(game_id)
        elif game_id: sum_of_lookups += 1

        if isinstance(name, list): sum_of_lookups += len(name)
        elif name: sum_of_lookups += 1

        if isinstance(igdb_id, list): sum_of_lookups += len(igdb_id)
        elif igdb_id: sum_of_lookups += 1

        if sum_of_lookups > 100: raise ValueError("Cannot look up for 100+ IDs and/or names")

        parameters = {}

        optional_params = {
            "id": game_id,
            "name": name,
            "igdb_id": igdb_id
        }

        for key, value in optional_params.items():
            if key: parameters[key] = value

        req = httpx.get(url,
                        params=parameters,
                        headers=self.client.headers,
                        timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()["data"]

        if len(res) < 1: return None

        games = list()
        for game in res:
            games.append(Category(
                id=game["id"],
                name=game["name"],
                box_art_url=game["box_art_url"],
                igdb_id=game["igdb_id"]
            ))

        if len(games) < 2: return games[0]

        return tuple(games)
