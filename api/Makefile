test:	
	FLASK_TESTING=1 python -m pytest -vv

run:
	gunicorn --bind localhost:5000 --worker-class eventlet --workers 1 run:app

.PHONY: testi gunicorn
