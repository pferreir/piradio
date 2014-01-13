import os
import re
from .mplayer import MPlayerServer

from .models import StateInfo, db
from .util import reset_state
from .app import app

RE_PLAYING_URL = re.compile(rb'Playing (.*)\.')
RE_ICY_INFO = re.compile(rb"ICY Info:\s*StreamTitle='([^;]*)';")


class Worker(object):
    """
    Representes a worker "process" that controls mplayer
    """

    def __init__(self, socket_file):
        self.socket_file = socket_file
        self._check_existing()

        reset_state()

        self.mplayer_server = MPlayerServer(socket_file)
        self.mplayer_server.add_listener(self.received_data)

    def _check_existing(self):
        if os.path.exists(self.socket_file):
            os.unlink(self.socket_file)
            print("Removed stale socket file")

    def received_data(self, data):
        m_playing = RE_PLAYING_URL.match(data)
        m_icy = RE_ICY_INFO.match(data)

        with app.app_context():

            if m_playing:
                url_t = m_playing.group(1).decode('utf-8')

                StateInfo.set("url", url_t)
                StateInfo.set("playing", False)
                StateInfo.set("song", None)

                db.session.commit()

            elif m_icy:
                stream_title = m_icy.group(1).decode('utf-8')
                song = StateInfo.get("song", stream_title)

                song.value = stream_title

                db.session.add(song)
                db.session.commit()

            elif data.startswith(b'Starting playback...'):
                playing = StateInfo.get("playing", True)
                playing.value = True

                db.session.add(playing)
                db.session.commit()

    def serve_forever(self):
        mps = self.mplayer_server

        try:
            mps.serve_forever()
        finally:
            reset_state()
            mps.send(b'quit\n')
            mps.wait()
            print("Stopped MPlayer")
            os.unlink(socket_file)


def run():
    worker = Worker(app.config['MPLAYER_SOCKET_FILE'])
    worker.serve_forever()
