#!/usr/bin/env bash
cd /app

pipenv install --dev

OUTPUT=$(pipenv run python generate_qid_batch.py test_batch.csv)
BATCH_ID=${OUTPUT: -36}

sleep 15

mkdir print_files
pipenv run python acceptance_test_check.py --batch-id $BATCH_ID