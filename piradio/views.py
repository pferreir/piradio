from functools import wraps

from flask import (
    render_template,
    jsonify,
    Response,
    Blueprint,
    current_app,
    request
)
from .client import Client
from .models import Station

views = Blueprint("views", __name__)


def use_client(f):
    @wraps(f)
    def _func(*args, **kwargs):
        client = Client(current_app.config['MPLAYER_SOCKET_FILE'])
        return f(client, *args, **kwargs)
    return _func


@views.route('/')
def home():
    return render_template('pages/home.html',
                           stations=Station.query.all())


@views.route('/play/<station_id>', methods=['POST'])
@use_client
def play(client, station_id):
    client.play(station_id)
    return jsonify({
        "result": "OK"
        })


@views.route('/search/', methods=['GET'])
@use_client
def search(client):
    term = request.args.get('q', '').strip()

    if not term:
        return jsonify({
            "result": "Missing query term"
            }), 400

    return jsonify({
        "result": client.search(term)
        })


@views.route('/stop/', methods=['POST'])
@use_client
def stop(client):
    client.stop()
    return jsonify({
        "result": "OK"
        })


@views.route('/pause/', methods=['POST'])
@use_client
def pause(client):
    return jsonify({
        "paused": client.pause()
        })


@views.route('/player_state.json', methods=['GET'])
@use_client
def player_state(client):
    return jsonify(client.get_player_state())


@views.route('/logo/<station_id>')
def logo(station_id):
    station = Station.query.get(station_id)
    (ctype, data) = station.logo.split(b'\0', 1)

    return Response(data, mimetype=ctype.decode('utf-8'))


@views.route('/playing.json')
@use_client
def playing(client):
    return jsonify(client.get_playing_info())
