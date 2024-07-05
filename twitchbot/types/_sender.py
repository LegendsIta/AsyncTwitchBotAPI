import re

from twitchbot.types import Subscription


class Sender:
    def __init__(self, resp: str):
        self._user_id = re.search("user-id=(.*?);", resp).group(1)
        self._username, self._message = re.search(".*:(.*?)!.*?:(.*)", resp).groups()
        self._subscription = Subscription.from_response(resp)
        self._moderator = self._is_mod(resp)
        self._broadcaster = self._is_broadcaster(resp)
        self._vip = self._is_vip(resp)

    @staticmethod
    def _is_broadcaster(resp) -> bool:
        return bool(re.search("badges=broadcaster\/1", resp))

    @staticmethod
    def _is_vip(resp) -> bool:
        return bool(re.search("badges=vip\/1", resp))

    @staticmethod
    def _is_mod(resp) -> bool:
        return bool(re.search("badges=moderator\/1", resp))

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def username(self) -> str:
        return self._username

    @property
    def message(self) -> str:
        return self._message

    @property
    def subscription(self) -> Subscription:
        return self._subscription

    @property
    def is_broadcaster(self) -> bool:
        return self._broadcaster

    @property
    def is_moderator(self) -> bool:
        return self._moderator

    @property
    def vip(self):
        return self._vip
