from typing import List

from lifesaver import Cog
from lifesaver.config import Config

from discord.ext import commands

from storcord.client import Client


class StorcordConfig(Config):
    guilds: List[int]


@Cog.with_config(StorcordConfig)
class Storcord:
    def __init__(self, bot):
        super().__init__(bot)

        self.clients = {
            guild_id: Client(bot, guild_id) for guild_id in self.config.guilds
        }

    @Cog.listener()
    async def on_ready(self):
        pass

    @commands.command()
    async def init(self, ctx):
        pass

    @commands.command()
    async def find(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Storcord(bot))
