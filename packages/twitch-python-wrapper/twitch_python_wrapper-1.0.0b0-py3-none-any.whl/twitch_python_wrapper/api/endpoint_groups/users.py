import httpx
from dateutil.parser import isoparse

from twitch_python_wrapper.api.client import APIClient
from twitch_python_wrapper.api.enums import UserType, BroadcasterType
from twitch_python_wrapper.api.objects import User


class Users:
    def __init__(self, client: APIClient):
        self.client = client

    def get_users(self,
                  user_id: str | list[str] = None,
                  login: str | list[str] = None) -> User | tuple[User, ...] | None:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-users>`_

        Returns information about one or more users.

        You may look up users using their user ID, login name, or both but the sum total of the number of users you may
        look up is 100. For example, you may specify 50 IDs and 50 names or 100 IDs or names, but you cannot specify 100
        IDs and 100 names.

        If you don’t specify IDs or login names, the request returns information about the user in the access token if
        you specify a user access token.

        To include the user’s verified email address in the response, you must use a user access token that includes the
        **user:read:email** scope.

        :param user_id: The ID of the user to get. To specify more than one user, set this parameter to a list for each
            user to get. The maximum of IDs you may specify is 100.

        :param login: The login name of the user to get. To specify more than one user, set this parameter to a list for
            each user to get. The maximum number of login names you may specify is 100.

        :return: A tuple of users.
        """

        url = self.client.url + "users"

        sum_of_lookups = 0

        if isinstance(user_id, list): sum_of_lookups += len(user_id)
        elif user_id: sum_of_lookups += 1

        if isinstance(login, list): sum_of_lookups += len(login)
        elif login: sum_of_lookups += 1

        # TODO: Remove check for user_id and login being mutually exclusive only if token is user access token
        if sum_of_lookups > 100: raise ValueError("Cannot look up for 100+ user IDs and/or logins")

        parameters = {}

        optional_params = {
            "id": user_id,
            "login": login
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

        users = list()
        for user in res:
            users.append(User(
                id=user["id"],
                login=user["login"],
                display_name=user["display_name"],
                type=UserType(user["type"]),
                broadcaster_type=BroadcasterType(user["broadcaster_type"]),
                description=user["description"],
                profile_image_url=user["profile_image_url"],
                offline_image_url=user["offline_image_url"],
                email=user["email"] if "email" in user else None,
                created_at=int(isoparse(user["created_at"]).timestamp())
            ))

        if len(users) < 2: return users[0]

        return tuple(users)

    def update_user(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#update-user>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def get_user_block_list(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-user-block-list>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def block_user(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#block-user>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def unblock_user(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#unblock-user>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def get_user_extensions(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-user-extensions>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def get_user_active_extensions(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-user-active-extensions>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")

    def update_user_extensions(self):
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#update-user-extensions>`_

        :raise NotImplementedError: This feature is not implemented yet.
        """

        raise NotImplementedError("Not Implemented Yet")
