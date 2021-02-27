import discord

from typing import Optional
from .collection import Collection


class Client:
    def __init__(self, discord_client, guild_id: int):
        self.discord = discord_client
        self.guild_id = guild_id
        self.guild = self.discord.get_guild(guild_id)
        assert self.guild is not None

    # async def create_index(self):
    #     index_channel = await self.guild.create_text_channel(
    #         name="stor-index", reason="storcord init"
    #     )
    #     await index_channel.send("{}")

    # async def ensure_index(self):
    #     index_channel = discord.utils.find(
    #         lambda c: c.name == "stor-index", self.guild.channels
    #     )
    #     if index_channel is None:
    #         await self.create_index()

    async def create_collection(self, name: str) -> Collection:
        channel = await self.guild.create_text_channel(
            name=f"stor-coll-{name}", reason="storcord create collection"
        )

        return Collection(self, channel)

    async def fetch_collection(self, name: str) -> Optional[Collection]:
        collection_channel = discord.utils.find(
            lambda c: c.name == f"stor-coll-{name}", self.guild.channels
        )

        if collection_channel is None:
            return None

        return Collection(self, collection_channel)
