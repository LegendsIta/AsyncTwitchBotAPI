#!/usr/bin/env python
"""
AsyncTwitchBotApi is a library that enables you to create Twitch chatbots with customizable commands,
filters for execution, and scheduled automatic messages using IRC integration.

Author: LegendsIta <https://github.com/LegendsIta>

This module provides an IRC client for connecting to and interacting with Twitch IRC server.
"""

import socket
import logging
import asyncio

logger = logging.getLogger("IRCClient")


class IRCClient:
    """
    IRC Client for Twitch IRC server interaction.

    Attributes:
        _sock: Socket object for the IRC connection.
        _host (str): Twitch IRC server hostname.
        _port (int): Twitch IRC server port.
        _username (str): Twitch bot's username.
        _oauth (str): OAuth token for authentication.
        _channel (str): Current channel the bot is joined to.
        _loop: Asyncio event loop.
        _reader: StreamReader object for reading data from the IRC connection.
        _writer: StreamWriter object for writing data to the IRC connection.

    Methods:
        __init__(username: str, oauth: str):
            Initializes IRCClient instance with Twitch credentials.

        _is_connected() -> bool:
            Checks if the client is currently connected to the Twitch IRC server.

        async connect():
            Connects to the Twitch IRC server using provided credentials.

        async get_response() -> str:
            Retrieves and processes a response from the Twitch IRC server.

        async send_message(message: str):
            Sends a message to the current channel in Twitch IRC.

        async _send_pong():
            Sends a PONG response to a received ping request from the Twitch IRC server.

        async join_channel(channel: str):
            Joins a specified channel on the Twitch IRC server.

        async quit_channel():
            Quits the current channel on the Twitch IRC server.

        async disconnect():
            Disconnects from the Twitch IRC server, closing all connections.

    Exceptions:
        IsNotInChannelError:
            Raised when an operation requires being in a channel, but the client is not currently in any channel.

        NotConnectedError:
            Raised when an operation requires an active connection to the Twitch IRC server, but no connection exists.
    """
    def __init__(self, username: str, oauth: str):
        """
        Initializes IRCClient instance with Twitch credentials.

        Args:
            username (str): Twitch bot's username.
            oauth (str): OAuth token for authentication.
        """
        self._sock = None
        self._host = "irc.chat.twitch.tv"
        self._port = 6667
        self._username = username
        self._oauth = oauth
        self._channel = None
        self._loop = asyncio.get_event_loop()
        self._reader = None
        self._writer = None

    def _is_connected(self) -> bool:
        """
        Checks if the client is currently connected to the Twitch IRC server.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self._sock is not None and self._sock.fileno() != -1

    async def connect(self):
        """
        Connects to the Twitch IRC server using provided credentials.
        """
        if not self._is_connected():
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.setblocking(False)
            self._reader, self._writer = await asyncio.open_connection(self._host, self._port, loop=self._loop)
            self._writer.write("CAP REQ :twitch.tv/tags\n".encode("utf-8"))
            self._writer.write("PASS {0}\n".format(self._oauth).encode("utf-8"))
            self._writer.write("NICK {0}\n".format(self._username).encode("utf-8"))
            await self._writer.drain()

    async def get_response(self):
        """
        Retrieves and processes a response from the Twitch IRC server.

        Returns:
             str: Response data from the IRC server.
        """
        try:
            if self._reader is None:
                raise NotConnectedError()

            data = await self._reader.read(2028)

            data = data.decode()

            if "PING :tmi.twitch.tv" in data:
                await self._send_pong()
            elif "Welcome, GLHF!" in data:
                logger.info("connected!")
            elif ":tmi.twitch.tv CAP * ACK :twitch.tv/tags" not in data:
                return data
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            logger.error(f"Error while receiving data: {e}")
        return ""

    async def send_message(self, message):
        """
        Sends a message to the current channel in Twitch IRC.

        Args:
            message (str): Message to send.
        """
        if not self._is_connected():
            raise NotConnectedError()

        try:
            if self._writer is None:
                raise NotConnectedError()

            self._writer.write(f"PRIVMSG #{self._channel} :{message}\n".encode("utf-8"))
            await self._writer.drain()
        except Exception as e:
            logger.error(f"Error while sending message: {e}")

    async def _send_pong(self):
        """
        Sends a PONG response to a received ping request from the Twitch IRC server.
        """
        try:
            if self._writer is None:
                raise NotConnectedError()

            self._writer.write("PONG :tmi.twitch.tv\n".encode())
            await self._writer.drain()
            logger.info("I answered the ping request!")
        except Exception as e:
            logger.error(f"Error while sending message: {e}")

    async def join_channel(self, channel: str):
        """
        Joins a specified channel on the Twitch IRC server.

        Args:
            channel (str): Channel name to join.
        """
        try:
            if self._writer is None:
                raise NotConnectedError()

            self._writer.write(f"JOIN #{channel}\n".encode("utf-8"))
            await self._writer.drain()
            self._channel = channel
            logger.info(f"Join into #{self._channel}!")
        except Exception as e:
            logger.error(f"Error while joining channel: {e}")

    async def quit_channel(self):
        """
        Quits the current channel on the Twitch IRC server.
        """
        try:
            if self._writer is None:
                raise NotConnectedError()

            self._writer.write(f"PART #{self._channel}\n".encode("utf-8"))
            await self._writer.drain()
            self._channel = None
        except OSError as e:
            if e.errno == 57:
                logger.warning("Socket is not connected.")
            else:
                logger.error(f"Error while quitting channel: {e}")
        except Exception as e:
            logger.error(f"Error while quitting channel: {e}")

    async def disconnect(self):
        """
        Disconnects from the Twitch IRC server, closing all connections.
        """
        try:
            if self._writer:
                self._writer.write("QUIT\n".encode("utf-8"))
                await self._writer.drain()
                self._writer.close()
                await self._writer.wait_closed()
                self._writer = None
            if self._reader:
                self._reader.feed_eof()
                self._reader = None
            if self._sock:
                self._sock.close()
                self._sock = None
            logger.info("Disconnected from Twitch IRC server.")
        except Exception as e:
            logger.error(f"Error while disconnecting: {e}")


class IsNotInChannelError(Exception):
    """
    Exception raised when an operation requires being in a channel, but the client is not currently in any channel.
    """
    def __init__(self):
        super(IsNotInChannelError, self).__init__("You are not in any channel!")


class NotConnectedError(Exception):
    """
    Exception raised when an operation requires an active connection to the Twitch IRC server, but no connection exists.
    """
    def __init__(self):
        super(NotConnectedError, self).__init__("You are not connected to the Twitch IRC server!")
