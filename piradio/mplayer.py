import re
import subprocess
import socket
from threading import Thread
import socketserver
from functools import wraps

from flask import current_app


ICY_RE = re.compile(rb"ICY Info: StreamTitle='(.*)';StreamUrl='(.*)';")


class Reader(Thread):

    def __init__(self, fd, callback):
        super(Reader, self).__init__()
        self._fd = fd
        self._callback = callback

    def run(self):
        for line in iter(self._fd.readline, b''):
            self._callback(line)
        print('Reader dead')


class UnixServer(socketserver.UnixStreamServer):
    def setMPServer(self, mplayer):
        self.mplayer_server = mplayer


class SocketHandler(socketserver.StreamRequestHandler):

    def handle(self):

        def expect_prop(data):
            self.wfile.write(data)
            self.server.mplayer_server.remove_listener(expect_prop)

        data = self.rfile.readline()
        while data:
            print("[R] " + data.decode('utf-8'))

            if re.match(rb'(?:pausing_keep(?:_force)?) get_property .*', data):
                self.server.mplayer_server.add_listener(expect_prop)

            self.server.mplayer_server.send(data)
            data = self.rfile.readline()


class MPlayerServer(object):
    def __init__(self, socket_file):
        config = current_app.config
        self.sp = subprocess.Popen([config['MPLAYER_CMD'], '-slave', '-idle', '-quiet'],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        self.stdin = self.sp.stdin
        self.stdout = self.sp.stdout
        self.stdout_reader = Reader(self.stdout, self.data_received)
        self.stdout_reader.start()
        self.unix_server = UnixServer(socket_file, SocketHandler)
        self.unix_server.setMPServer(self)
        self._listeners = []

    def wait(self):
        self.stdout_reader.join()
        ret = self.sp.wait()
        return ret

    def add_listener(self, cb):
        self._listeners.append(cb)

    def remove_listener(self, cb):
        self._listeners.remove(cb)

    def data_received(self, data):
        print(b'[D] ' + data)
        for listener in self._listeners:
            listener(data)

    def send(self, data):
        self.stdin.write(data)
        self.stdin.flush()

    def serve_forever(self):
        return self.unix_server.serve_forever()


class MPlayerClient(object):
    def __init__(self, socket_file):
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket_file = socket_file
        self.socket.connect(self.socket_file)

    def _get_answer(self):
        data = b""

        while True:
            data += self.socket.recv(512)
            i = data.find(b'\n')

            if i >= 0:
                return data[:i]

    def play(self, url):
        self.socket.send(bytes("loadfile {0}\n".format(url), 'utf-8'))

    def pause(self):
        self.socket.send(b"pause\n")

    def stop(self):
        self.socket.send(b"stop\n")

    def get_property(self, prop, pausing_keep=False):
        self.socket.send(bytes("{1}get_property {0}\n".format(prop,
                               "pausing_keep_force " if pausing_keep else ""), 'utf-8'))
        answer = self._get_answer()

        m = re.match(bytes(r"ANS_{}=(.*)$".format(prop), 'utf-8'), answer)
        if m:
            return m.group(1).decode('utf-8')

    def close(self):
        self.socket.close()


def mplayer_client(f):
    @wraps(f)
    def _func(self, *args, **kwargs):
        client = MPlayerClient(self.socket_file)
        res = f(self, client, *args, **kwargs)
        client.close()
        return res
    return _func
