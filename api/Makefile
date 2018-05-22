test:
	FLASK_TESTING=1 python -m pytest -vv --cov=local_api --cov-report html

test.verbose:	
	echo ${TEST}
	FLASK_TESTING=1 python -m pytest -vv -s

test.one:
	FLASK_TESTING=1 python -m pytest -vv -s -k ${TEST}

run:
	gunicorn --bind localhost:5000 --reload --worker-class eventlet --workers 1 run:app

.PHONY: test test.verbose gunicorn
