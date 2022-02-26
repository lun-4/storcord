import json


class FullDocument:
    def __init__(self, client, message):
        self.client = client
        self.message = message
        self.id = message.id

    @property
    def body(self):
        return json.loads(self.message.content)

    async def delete(self):
        await self.message.delete()


class ShardedDocument:
    def __init__(self, client, index_message, chunk_messages):
        self.id = index_message.id
        self.client = client
        self.index_message = index_message
        self.chunk_messages = chunk_messages

    @property
    def body(self):
        text = "".join((json.loads(m.content)["body"] for m in self.chunk_messages))
        return json.loads(text)

    async def delete(self):
        await self.index_message.delete()
        for chunk_message in self.chunk_messages:
            await chunk_message.delete()
