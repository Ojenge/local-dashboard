docs:
	snowboard html -o documentation/api.html documentation/api.apib
	
docs-serve:
	snowboard html -s -o documentation/api.html documentation/api.apib

.PHONY: docs docs-serve
