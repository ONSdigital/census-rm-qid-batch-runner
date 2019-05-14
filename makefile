install:
	pipenv install --dev

check:
	pipenv check

lint:
	pipenv run flake8

test: check lint
	pipenv run pytest
