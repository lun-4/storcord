from quart import Quart, g

from .index import bp as index_bp
from .storcord import bp as storcord_bp

app = Quart(__name__)
app.bot = None


@app.before_request
def assign_globals():
    g.bot = app.bot


app.register_blueprint(index_bp)
app.register_blueprint(storcord_bp, url_prefix="/api/v1")
