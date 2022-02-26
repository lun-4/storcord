import json

from .document import FullDocument, ShardedDocument

# from https://stackoverflow.com/a/312464
def yield_chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i : i + n]


class Collection:
    def __init__(self, client, channel):
        self.client = client
        self.discord = client.discord
        self.guild = client.guild
        self.channel = channel

    def __repr__(self) -> str:
        return f"<Collection guild={self.guild!r} channel={self.channel!r}>"

    async def _resolve_document(self, message, *, follow: bool = False):
        index_or_full = json.loads(message.content)
        if index_or_full["type"] == "full":
            return FullDocument(message)
        elif index_or_full["type"] == "shard_index":
            message_ids = index_or_full["chunks"]
            shard_messages = []
            for message_id in message_ids:
                shard_messages.append(await self.channel.fetch_message(message_id))
            return ShardedDocument(self, message, shard_messages)
        elif index_or_full["type"] == "shard":
            pass  # ignore

    async def find(self, query_params: dict, only_one: bool = False):
        # work with copy of params
        query_params = dict(query_params)

        query_id = query_params.get("_id")
        if query_id is not None:
            query_params.pop("_id")
            document = await self.channel.fetch_message(query_id)
            return document if only_one else [document]

        documents = []

        async for message in self.channel.history(limit=None):
            document = await self._resolve_document(message)
            if document is None:
                continue

            is_match = True
            for query_key, query_value in query_params.items():
                possible_match_value = document.body.get(query_key)
                # TODO work with nested dicts
                if possible_match_value != query_value:
                    is_match = False

            if is_match and only_one:
                return document
            elif is_match:
                documents.append(document)

        if only_one:
            return None
        else:
            return documents

    async def insert_one(self, doc: dict):
        # try to generate it as full, if it doesn't work, shard it up
        doc_as_message = json.dumps({"type": "full", "body": doc})
        if len(doc_as_message) > 10:
            chunks = []
            doc_as_string = json.dumps(doc)
            print(doc_as_string)
            for chunk in yield_chunks(doc_as_string, 10):
                chunk_document = json.dumps({"type": "shard", "body": chunk})
                assert len(chunk_document) < 2000
                chunks.append(chunk_document)

            # now that we have chunk bodies, we need to send them all
            # and then construct our index for the shard
            chunk_messages = []
            for chunk_body in chunks:
                chunk_message = await self.channel.send(chunk_body)
                chunk_messages.append(chunk_message)

            index_string = json.dumps(
                {
                    "type": "shard_index",
                    "chunks": [m.id for m in chunk_messages],
                }
            )
            assert len(index_string) < 2000
            index_message = await self.channel.send(index_string)

            return ShardedDocument(self, index_message, chunk_messages)
        else:
            message = await self.channel.send(doc_as_message)
            return FullDocument(message)

    async def delete(self, query_params: dict):
        documents = await self.find(query_params)
        for doc in documents:
            await doc.delete()

        return len(documents)
