install:
	pipenv install --dev

check:
	# TODO reinstate this once https://github.com/pypa/pipenv/issues/4188 is resolved
   #pipenv check

lint:
	pipenv run flake8

test: check lint
	pipenv run pytest

build: install test
	docker build . -t eu.gcr.io/census-rm-ci/rm/census-rm-qid-batch-runner:latest

delete-pod:
	kubectl delete deploy qid-batch-runner

apply-deployment:
	kubectl apply -f qid-batch-runner.yml

connect-to-pod:
	kubectl exec -it `kubectl get pods -o name | grep -m1 qid-batch-runner | cut -d'/' -f 2` -- /bin/bash
