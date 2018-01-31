# SupaBRCK Local Dashboard API

Implementation of a REST api to read and configure a SupaBRCK.

## Development environment

### Initializing

The development environment can be initialized like so:

```bash
mkvirtuenv dash
pip install -r dev_requirements.txt
```

### Runtime dependencies

- brck-sdk


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
FLASK_APP=./local_api/__init__.py flask db upgrade
```

The default database will be located in: `./local_api/dashboard.sqlite`

This value may be overriden by a `DATABASE_URL` environmental variable.

    See the production artificacts for the DB location when local dash is installed via `opkg`.


### Running

The application may either be started using any of these approaches

```shell
python run.py
# or with flask_script
FLASK_APP=./local_api/__init__.py flask run
# or using gunicorn
gunicorn --bind localhost:8000 --workers 2 run:app
```


### TODOS

- [x] Battery status API
- [x] Connection status API
- [x] Storage status API
- [ ] SOC/Turn-on/Turn-off configuration API
- [ ] Plex
- [ ] FTP
- [ ] Authentication

### Generating a release

TBD
