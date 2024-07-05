from typing import Type
import re


class Subscription:
    def __init__(self, subscribed: bool, month: int):
        self._subscribed = subscribed
        self._month = month

    @staticmethod
    def from_response(resp) -> "Subscription":
        has_sub = bool(int(re.search("subscriber=(.*?);", resp).group(1)))
        sub_months = re.search("@badge-info=subscriber\/(.*?);", resp)
        if sub_months:
            sub_months = int(sub_months.group(1))
        else:
            sub_months = 0
        return Subscription(has_sub, sub_months)

    @property
    def month(self) -> int:
        return self._month

    @property
    def subscribed(self) -> bool:
        return self._subscribed
