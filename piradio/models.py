from flask import json
from flask.ext.sqlalchemy import SQLAlchemy

from .util import strip_accents

db = SQLAlchemy()


class Keyword(db.Model):
    __tablename__ = 'keywords'

    text = db.Column(db.String(), primary_key=True)

    def __init__(self, text):
        self.name = text


class StationKeywords(db.Model):
    __tablename__ = 'station_keywords'

    station_id = db.Column(db.ForeignKey('stations.id'), primary_key=True)
    keyword = db.Column(db.ForeignKey('keywords.text'), primary_key=True)


class StateInfo(db.Model):
    __tablename__ = 'state_info'

    key = db.Column(db.String, primary_key=True)
    _value = db.Column(db.String)

    def __init__(self, key, value):
        self.key = key
        self.value = value

    @property
    def value(self):
        return json.loads(self._value)

    @value.setter
    def value(self, value):
        self._value = json.dumps(value)

    @classmethod
    def get(cls, key, default=None):
        val = cls.query.get(key)
        if val:
            return val
        else:
            return cls(key, default)

    @classmethod
    def set(cls, key, val):
        entry = cls.query.get(key)
        if entry is None:
            entry = cls(key, val)
            db.session.add(entry)
        else:
            entry.value = val
        return entry


class Station(db.Model):
    __tablename__ = 'stations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    norm_name = db.Column(db.String)
    url = db.Column(db.String, unique=True)
    _logo = db.Column('logo', db.LargeBinary())

    @property
    def logo(self):
        return self._logo

    @logo.setter
    def logo(self, value):
        self._logo = b'\0'.join(value)

    # keywords = db.relationship("Keyword",
    #                            secondary=StationKeywords,
    #                            backref='stations')

    def __init__(self, name, url, logo=None):
        self.name = name
        self.norm_name = strip_accents(name)
        self.url = url

        if logo is not None:
            self.logo = logo
