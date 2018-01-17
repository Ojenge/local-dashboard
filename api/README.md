# SupaBRCK Local Dashboard API

Implementation of a REST api to read and configure a SupaBRCK.

## Development environment

### Initializing

The development environment can be initialized like so:

```bash
mkvirtuenv dash
pip install -r dev_requirements.txt
```


### Running tests

```bash
python -m pytest
```

Running tests locally will largely test the sanity of your python code.

Mocking is implemented for functions requiring a live device environment.


### Generating a release

TBD