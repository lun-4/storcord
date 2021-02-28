import json
from quart import Blueprint, g, request, jsonify

bp = Blueprint("storcord", __name__)


def storcord(guild_id):
    cog = g.bot.get_cog("Storcord")
    return cog.clients[guild_id]


@bp.route("/<int:guild_id>/collections/<name>", methods=["POST", "PUT"])
async def new_coll(guild_id: int, name):
    await storcord(guild_id).create_collection(name)
    return "", 204


@bp.route("/<int:guild_id>/collections/<name>/document", methods=["PUT"])
async def new_document(guild_id: int, name):
    coll = await storcord(guild_id).get_collection(name)
    j = await request.get_json()
    assert isinstance(j, dict)
    await coll.insert_one(j)
    return "", 204


@bp.route("/<int:guild_id>/collections/<name>/find", methods=["PUT"])
async def find(guild_id: int, name):
    coll = await storcord(guild_id).get_collection(name)
    j = await request.get_json()
    assert isinstance(j, dict)
    result = await coll.find_one(j)
    if result is None:
        return "rip", 404

    return jsonify({"result": json.loads(result.content)})
