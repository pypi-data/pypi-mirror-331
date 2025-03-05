import httpx
from dateutil.parser import isoparse

from twitch_python_wrapper.api.client import APIClient
from twitch_python_wrapper.api.objects import BroadcasterTeam, Team, TeamUser


class Teams:
    def __init__(self, client: APIClient):
        self.client = client

    def get_channel_teams(self,
                          broadcaster_id: str) -> BroadcasterTeam | tuple[BroadcasterTeam, ...] | None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-channel-teams>`_

        Returns the list of Twitch teams that the broadcaster is a member of.

        :param broadcaster_id: The ID of the broadcaster whose teams you want to get.

        :return: A tuple of teams that the broadcaster is a member of. Returns None if the broadcaster is not a member
            of a team.
        """

        url = self.client.url + "teams/channel"

        req = httpx.get(url,
                        params={"broadcaster_id": broadcaster_id},
                        headers=self.client.headers,
                        timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()["data"]

        if len(res) < 1: return None

        teams = list()
        for team in res:
            teams.append(BroadcasterTeam(
                broadcaster_id=team["broadcaster_id"],
                broadcaster_login=team["broadcaster_login"],
                broadcaster_name=team["broadcaster_name"],
                background_image_url=team["background_image_url"],
                banner=team["banner"],
                created_at=int(isoparse(team["created_at"]).timestamp()),
                updated_at=int(isoparse(team["updated_at"]).timestamp()),
                info=team["info"],
                thumbnail_url=team["thumbnail_url"],
                team_name=team["team_name"],
                team_display_name=team["team_display_name"],
                id=team["id"]
            ))

        if len(teams) < 2: return teams[0]

        return tuple(teams)

    def get_teams(self,
                  name: str = None,
                  team_id: str = None) -> Team | None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-teams>`_

        Gets information about the specified Twitch team. `Read More <https://help.twitch.tv/s/article/twitch-teams>`.

        :param name: The name of the team to get. This parameter and the *team_id* parameter are mutually exclusive; you
            must specify the team’s name or ID but not both.

        :param team_id: The ID of the team to get. This parameter and the *name* parameter are mutually exclusive; you
            must specify the team’s name or ID but not both.

        :return: A tuple that contains the single team that you requested.

        :raise ValueError: If name and team_id are none.
        """

        url = self.client.url + "teams"

        if name is None and team_id is None: raise ValueError("Parameters name and team_id are mutually exclusive")

        parameters = {}

        optional_params = {
            "name": name,
            "id": team_id
        }

        for key, value in optional_params.items():
            if value: parameters[key] = value

        req = httpx.get(url,
                        params=parameters,
                        headers=self.client.headers,
                        timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()["data"]

        if len(res) < 1: return None
        res = res[0]

        users = list()
        for user in res["users"]:
            users.append(TeamUser(
                user_id=user["user_id"],
                user_login=user["user_login"],
                user_name=user["user_name"]
            ))

        return Team(
            users=tuple(users),
            background_image_url=res["background_image_url"],
            banner=res["banner"],
            created_at=int(isoparse(res["created_at"]).timestamp()),
            updated_at=int(isoparse(res["updated_at"]).timestamp()),
            info=res["info"],
            thumbnail_url=res["thumbnail_url"],
            team_name=res["team_name"],
            team_display_name=res["team_display_name"],
            id=res["id"]
        )
