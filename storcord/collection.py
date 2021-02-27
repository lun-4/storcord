import json


class Collection:
    def __init__(self, client, channel):
        self.client = client
        self.discord = client.discord
        self.guild = client.guild
        self.channel = channel

    def __repr__(self) -> str:
        return f"<Collection guild={self.guild!r} channel={self.channel!r}>"

    async def find_one(self, query_params: dict):
        # work with copy of params
        query_params = dict(query_params)

        query_id = query_params.get("_id")
        if query_id is not None:
            query_params.pop("_id")
            return await self.channel.fetch_message(query_id)

        async for message in self.channel.history(limit=None):
            possible_match_raw = json.loads(message.content)
            possible_match = possible_match_raw["_doc"]

            match = True
            for query_key, query_value in query_params.items():
                possible_match_value = possible_match.get(query_key)
                # TODO work with nested dicts
                if possible_match_value != query_value:
                    match = False

            if match:
                return message

        return None

    async def insert_one(self, doc: dict):
        doc_as_message = json.dumps({"_type": "full", "_doc": doc})
        message = await self.channel.send(doc_as_message)
        return message

    async def delete_one(self, query_params: dict):
        result = await self.find_one(query_params)
        if result is None:
            return False

        await result.delete()
        return True
