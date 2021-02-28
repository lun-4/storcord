from quart import Quart, g

from .index import bp as index_bp

app = Quart(__name__)
app.bot = None


@app.before_request
def assign_globals():
    g.bot = app.bot


app.register_blueprint(index_bp)
