import sys

import requests
import yaml

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from .app import app
from .models import db


manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


from .models import Station


def get_logo(logo_url):
    r = requests.get(logo_url)
    ctype = r.headers.get('content-type')

    if not ctype and not ctype.startswith('image/'):
        print("File doesn't seem to be an image! ({})".format(ctype))

    return (ctype.encode('utf-8'), r.content)


@manager.command
def list_stations():
    stations = Station.query.all()
    for station in stations:
        print("{} {}: {}".format(station.id, station.name, station.url))


@manager.command
def add_station(name, url, logo_url=None):
    station = Station(name, url)

    if logo_url:
        station.logo = get_logo(logo_url)

    db.session.add(station)
    db.session.commit()


@manager.command
def edit_station(station_id, name=None, url=None, logo_url=None):
    station = Station.query.get(station_id)

    if station is None:
        print("No such station ({}) found!".format(station_id))
        return

    if name is not None:
        station.name = name

    if url is not None:
        station.url = url

    if logo_url is not None:
        (ctype, data) = get_logo(logo_url)
        station.logo = (ctype, data)

    db.session.commit()


@manager.command
def import_stations(yaml_file, exclude_duplicates=False):
    """
    Import stations from YAML File
    """
    count = 0

    with open(yaml_file, 'r') as f:
        for data in yaml.load(f):
            if exclude_duplicates:
                station = Station.query.filter_by(url=data['url']).first()
                if station:
                    print("Excluded ({}) {} ({})".format(
                        station.id, station.name, station.url))
                    continue

            logo_data = data.get('logo')
            if logo_data:
                logo_data = logo_data.split(b'\0', 1)

            station = Station(data['name'], data['url'], logo_data)
            db.session.add(station)
            db.session.commit()
            count += 1
    print("Added {} radio stations".format(count))


@manager.command
def export_stations(yaml_file=None, with_logo=False):
    """
    Export stations to YAML File if provided, else stdout
    """
    f = open(yaml_file, 'w') if yaml_file else sys.stdout

    stations = []

    for station in Station.query.all():
        data = {
            'name': station.name,
            'url': station.url
        }

        if with_logo:
            data['logo'] = station.logo

        stations.append(data)

    yaml.dump(stations, f)
    f.close()


@manager.command
def runworker():
    from .worker import run
    run()


def main():
    manager.run()


if __name__ == "__main__":
    main()
