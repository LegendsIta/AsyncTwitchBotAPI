#!/usr/bin/env python
#
# AsyncTwitchBotApi is a library that enables you to create Twitch chatbots with customizable commands,
# filters for execution, and scheduled automatic messages using IRC integration.
#
# Author: LegendsIta <https://github.com/LegendsIta>
#
"""This module contains an object that represents a Twitch Subscription of Twitch Sender."""

import re


class Subscription:
    """
        Represents a Twitch subscriber's subscription status and months.

        This class encapsulates information about whether a user is subscribed and for how many months.

        Attributes:
            _subscribed (bool): True if the user is subscribed, False otherwise.
            _month (int): Number of months the user has been subscribed.

        Methods:
            __init__(subscribed: bool, month: int):
                Initializes a Subscription object with the given subscription status and months.

            from_response(resp) -> Subscription:
                Parses a raw Twitch chat response to create a Subscription object.

            month() -> int:
                Returns the number of months the user has been subscribed.

            subscribed() -> bool:
                Returns True if the user is subscribed, False otherwise.
        """
    def __init__(self, subscribed: bool, month: int):
        self._subscribed = subscribed
        self._month = month

    @staticmethod
    def from_response(resp) -> "Subscription":
        """
        Parses a raw Twitch chat response to create a Subscription object.

        Args:
            resp (str): Raw response string received from Twitch chat.

        Returns:
            Subscription: Subscription object created from the response.
        """
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
