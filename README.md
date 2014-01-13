# piRadio

## Installing

*(virtualenv recommended)*

    $ pip install -r requirements.txt
    $ python setup.py install 


## Configuration

Initializing DB:

    $ piradio db upgrade

Edit `config.py` and change Flask's secret key.

## Running it

In a first shell:

    $ piradio runworker

From a second shell:

    $ piradio runserver

Open a browser:

    http://localhost:5000


## Managing stations

Adding a station:

    $ piradio add_station 'Rádio Comercial' http://195.23.102.196/comercialcbr96

Changing a logo:

    $ piradio edit_station 0 -l http://upload.wikimedia.org/wikipedia/commons/c/c3/Logo_Radio_Comercial.jpg

Listing stations:

    $ piradio list_stations

Bulk importing stations:

    $ curl https://gist.github.com/pferreir/ded13377e70bc72738d1/raw/95f5b455ac987134fcd7d48a16d9e5071bc4bf15/stations.yaml > /tmp/stations.yaml
    $ pirario import_stations /tmp/stations.yaml


## Credits

### Graphics assets
 * Oxygen typeface by Vernon Adams (vern@newtypography.co.uk)
 * Progress indicators based on [code by Tobias Ahlin](https://github.com/tobiasahlin/SpinKit)
 * Radio icon by [James Fenton](http://thenounproject.com/bitsnbobs/) from The [Noun Project](http://thenounproject.com/)