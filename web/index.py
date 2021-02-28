from quart import Blueprint, g

bp = Blueprint("index", __name__)


@bp.route("/", methods=["GET"])
async def index():
    print("AAAA")
    return "whats popping"
