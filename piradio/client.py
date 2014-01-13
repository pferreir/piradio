from .mplayer import mplayer_client
from .models import Station, StateInfo, db
from .util import reset_state


class Client(object):
    """
    Client interface that communicates with worker
    Abstracts out MPlayer and DB communication
    """

    def __init__(self, socket_file):
        self.socket_file = socket_file

    def search(self, term):
        stations = Station.query.filter(
            Station.norm_name.like("%{}%".format(term))).all()
        return [{
            'id': st.id,
            'name': st.name,
            'url': st.url,
            'has_logo': st.logo is not None
        } for st in stations]

    @mplayer_client
    def play(self, client, station_id):
        station = Station.query.get(station_id)
        client.play(station.url)

    @mplayer_client
    def stop(self, client):
        client.stop()
        reset_state()

    @mplayer_client
    def pause(self, client):
        client.pause()

        return client.get_property("pause", pausing_keep=True) == "yes"

    @mplayer_client
    def get_player_state(self, client):
        return {
            "is_paused":  client.get_property("pause", pausing_keep=True) == "yes"
        }

    @mplayer_client
    def get_playing_info(self, client):
        state_info = dict((si.key, si.value) for si in StateInfo.query.all())

        # client-side join inevitable because of JSON
        url = state_info.get('url')

        if url is None:
            station_info = None
        else:
            station = Station.query.filter_by(url=url).one()
            station_info = {
                'id': station.id,
                'name': station.name,
                'url': station.url,
                'has_logo': station.logo and len(station.logo) > 0
            }

        return {
            "station": station_info,
            "playing": state_info.get("playing", False),
            "song": state_info.get("song"),
            "paused":  client.get_property("pause", pausing_keep=True) == "yes"
        }
