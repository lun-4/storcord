from typing import List
import json

from lifesaver import Cog
from lifesaver.config import Config

from discord.ext import commands

from storcord.client import Client


class StorcordConfig(Config):
    guilds: List[int]


@Cog.with_config(StorcordConfig)
class Storcord(Cog):
    def __init__(self, bot):
        super().__init__(bot)
        if self.bot.is_ready():
            self._init_clients()

    def _init_clients(self):
        self.clients = {
            guild_id: Client(self.bot, guild_id) for guild_id in self.config.guilds
        }

    @Cog.listener()
    async def on_ready(self):
        self._init_clients()

    @commands.command()
    async def newcoll(self, ctx, name: str):
        client = self.clients[ctx.guild.id]
        coll = await client.create_collection(name)
        return await ctx.send(repr(coll))

    @commands.command()
    async def insert(self, ctx, name: str, *, doc: str):
        print(repr(name), repr(doc))
        client = self.clients[ctx.guild.id]
        coll = await client.get_collection(name)
        if coll is None:
            return await ctx.send("collction not found")

        await coll.insert_one(json.loads(doc))
        await ctx.ok()

    @commands.command()
    async def find(self, ctx, name: str, *, doc: str):
        print(repr(name), repr(doc))
        client = self.clients[ctx.guild.id]
        coll = await client.get_collection(name)
        if coll is None:
            return await ctx.send("collction not found")

        result = await coll.find_one(json.loads(doc))
        await ctx.send(repr(result.content))


def setup(bot):
    bot.add_cog(Storcord(bot))
