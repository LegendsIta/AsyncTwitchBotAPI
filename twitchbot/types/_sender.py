#!/usr/bin/env python
"""
AsyncTwitchBotApi is a library that enables you to create Twitch chatbots with customizable commands,
filters for execution, and scheduled automatic messages using IRC integration.

Author: LegendsIta <https://github.com/LegendsIta>

This module contains an object that represents a Twitch Chat Sender.
"""

import re
from twitchbot.types import Subscription


class Sender:
    """
    Represents a Twitch chat message sender.

    This class extracts and manages information about a user who sent a message in a Twitch chat.

    Attributes:
        _user_id (str): The user's unique Twitch ID.
        _username (str): The username of the sender.
        _message (str): The message sent by the user.
        _subscription (Subscription): Subscription details of the user.
        _moderator (bool): Indicates if the user is a moderator.
        _broadcaster (bool): Indicates if the user is a broadcaster.
        _vip (bool): Indicates if the user is a VIP.

    Methods:
        __init__(resp: str):
            Initializes the Sender object using a raw response string from Twitch chat.

        _is_broadcaster(resp) -> bool:
            Checks if the user is a broadcaster based on the response string.

        _is_vip(resp) -> bool:
            Checks if the user is a VIP based on the response string.

        _is_mod(resp) -> bool:
            Checks if the user is a moderator based on the response string.

        user_id() -> int:
            Returns the user's Twitch ID.

        username() -> str:
            Returns the username of the sender.

        message() -> str:
            Returns the message sent by the user.

        subscription() -> Subscription:
            Returns the subscription details of the user.

        is_broadcaster() -> bool:
            Returns True if the user is a broadcaster, False otherwise.

        is_moderator() -> bool:
            Returns True if the user is a moderator, False otherwise.

        vip() -> bool:
            Returns True if the user is a VIP, False otherwise.
    """
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
