import socket
import logging
import asyncio

logger = logging.getLogger("IRCClient")


class IRCClient:
    def __init__(self, username: str, oauth: str):
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
        return self._sock is not None and self._sock.fileno() != -1

    async def connect(self):
        if not self._is_connected():
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.setblocking(False)
            self._reader, self._writer = await asyncio.open_connection(self._host, self._port, loop=self._loop)
            self._writer.write("CAP REQ :twitch.tv/tags\n".encode("utf-8"))
            self._writer.write("PASS {0}\n".format(self._oauth).encode("utf-8"))
            self._writer.write("NICK {0}\n".format(self._username).encode("utf-8"))
            await self._writer.drain()

    async def get_response(self):
        try:
            if self._reader is None:
                raise NotConnectedError()

            data = await self._reader.read(2028)

            data = data.decode()

            if "PING :tmi.twitch.tv" in data:
                await self._send_pong()
            elif "Welcome, GLHF!" in data:
                logger.info("connected!")
            else:
                return data
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            logger.error(f"Error while receiving data: {e}")
        return ""

    async def send_message(self, message):
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
        try:
            if self._writer is None:
                raise NotConnectedError()

            self._writer.write("PONG :tmi.twitch.tv\n".encode())
            await self._writer.drain()
            logger.info("I answered the ping request!")
        except Exception as e:
            logger.error(f"Error while sending message: {e}")

    async def join_channel(self, channel: str):
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
    def __init__(self):
        super(IsNotInChannelError, self).__init__("You are not in any channel!")


class NotConnectedError(Exception):
    def __init__(self):
        super(NotConnectedError, self).__init__("You are not connected to the Twitch IRC server!")
