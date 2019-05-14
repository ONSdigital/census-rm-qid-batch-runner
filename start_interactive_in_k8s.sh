#!/usr/bin/env bash

kubectl run qid-batch-runner -it --rm --command --generator=run-pod/v1 \
    --env=RABBITMQ_SERVICE_HOST=rabbitmq \
    --env=RABBITMQ_SERVICE_PORT=5672 \
    --image-pull-policy=Always \
    --image=eu.gcr.io/census-rm-ci/rm/census-rm-qid-batch-runner:latest \
    --restart=Never \
    -- /bin/bash
