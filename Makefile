install:
	pipenv install --dev

check:
	pipenv check

lint:
	pipenv run flake8

test: check lint
	pipenv run pytest

build: install test
	docker build . -t eu.gcr.io/census-rm-ci/rm/census-rm-qid-batch-runner:latest

delete-pod:
	kubectl delete deploy qid-batch-runner

start-pod:
	kubectl apply -f qid-batch-runner.yml

connect-to-pod:
	kubectl exec -it qid-batch-runner /bin/bash
