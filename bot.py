import asyncio
import logging

import lifesaver

import hypercorn
from hypercorn.asyncio.tcp_server import TCPServer

from web.app import app as webapp

log = logging.getLogger(__name__)


async def _boot_hypercorn(app, config, *, loop):
    """Manually creates a Hypercorn server.
    We don't use Hypercorn's functions for server creation because it involves
    modifying the loop in undesirable ways. It also silently devours all
    KeyboardInterrupt exceptions.
    """
    socket = config.create_sockets()

    async def _callback(reader, writer):
        await TCPServer(app, loop, config, reader, writer)

    server = await asyncio.start_server(
        _callback,
        backlog=config.backlog,
        sock=socket.insecure_sockets[0],
    )
    return server


class StorcordBot(lifesaver.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # webapp (quart) setup
        webapp.config.from_mapping(self.config.web.app)
        webapp.bot = self
        self.webapp = webapp

        self.http_server_config = hypercorn.Config.from_mapping(self.config.web.http)
        self.http_server = None
        self.loop.create_task(self._boot_http_server())

    async def close(self):
        log.info("closing web server")
        if self.http_server:
            self.http_server.close()
            await self.http_server.wait_closed()
        await super().close()

    async def _boot_http_server(self):
        log.info("creating http server")
        try:
            self.http_server = await _boot_hypercorn(
                self.webapp, self.http_server_config, loop=self.loop
            )
            log.info("created server: %r", self.http_server)

            await self.http_server.serve_forever()
        except Exception:
            log.exception("failed to create server")
