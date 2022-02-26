import os
import json
from quart import Blueprint, g, request, jsonify

bp = Blueprint("storcord", __name__)


def auth(handler):
    async def _wrapped(*args, **kwargs):
        token = request.headers.get("authorization")
        if token != os.environ["STORCORD_AUTH_TOKEN"]:
            return "no auth lol", 401
        return await handler(*args, **kwargs)

    _wrapped.__name__ = handler.__name__
    return _wrapped


def storcord(guild_id):
    cog = g.bot.get_cog("Storcord")
    return cog.clients[guild_id]


@bp.route("/<int:guild_id>/collections/<name>", methods=["POST", "PUT"])
@auth
async def new_coll(guild_id: int, name):
    await storcord(guild_id).create_collection(name)
    return "", 204


@bp.route("/<int:guild_id>/collections/<name>/document", methods=["PUT"])
@auth
async def new_document(guild_id: int, name):
    coll = await storcord(guild_id).get_collection(name)
    j = await request.get_json()
    assert isinstance(j, dict)
    await coll.insert_one(j)
    return "", 204


@bp.route("/<int:guild_id>/collections/<name>/find", methods=["PUT"])
@auth
async def find(guild_id: int, name):
    coll = await storcord(guild_id).get_collection(name)
    j = await request.get_json()
    assert isinstance(j, dict)
    docs = await coll.find(j)
    return jsonify({"result": docs})


@bp.route("/<int:guild_id>/collections/<name>/delete", methods=["PUT"])
@auth
async def delete(guild_id: int, name):
    coll = await storcord(guild_id).get_collection(name)
    j = await request.get_json()
    assert isinstance(j, dict)
    return jsonify({"found": await coll.delete(j)})
