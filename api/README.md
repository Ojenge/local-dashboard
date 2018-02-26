# SupaBRCK Local Dashboard API

Implementation of a REST api to read and configure a SupaBRCK.

## Development environment

### Initializing

The development environment can be initialized like so:

```bash
mkvirtuenv dash
# checkout brck-sdk
python setup.py install
pip install -r dev_requirements.txt
```

### Runtime dependencies

    prod_requirements.txt

### Running tests

```bash
make test

# OR (for more verbose test result)

python -m pytest -vv
```

Running tests locally will largely test the sanity of your python code.

Mocking is implemented for functions requiring a live device environment.


### Running Database Migrations

```shell
FLASK_CONFIG=production FLASK_APP=./local_api/__init__.py flask db upgrade
```

    Note that the OPKG installer runs database migrations as part of the post-installation process.

### Running

The application may either be started using any of these approaches

```shell
make run
# or directly via gunicorn
gunicorn --bind localhost:5000 --reload --worker-class eventlet --workers 1 run:app
```


### Features

- [x] Authentication (os user/application user)
- [x] System status API (storage, connectivity battery)
- [x] SIM connectivity API
- [x] LAN Connectivity API
- [ ] WiFi connectivity API
- [x] Storage status API
- [x] Power management API (SOC)
- [ ] Plex
- [ ] FTP

### Generating a release

- Standard process via `brck-feeds` and brck-ci.
