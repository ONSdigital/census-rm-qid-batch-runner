# Census RM QID Batch Runner [![Build Status](https://travis-ci.com/ONSdigital/census-rm-qid-batch-runner.svg?branch=master)](https://travis-ci.com/ONSdigital/census-rm-qid-batch-runner)

A python script to tell RM to generate unaddressed QID/UAC pairs from a CSV config file.

## Dependencies

Install dependencies with 
```bash
make install
```

The script needs a rabbit instance to talk to you can use the instance from [census-rm-docker-dev]() or the docker-compose file here to run just a rabbit container with

```bash
docker-compose up -d
``` 

Look in [rabbit_context.py](/rabbit_context.py) to see the rabbit config.

## Generating the QID UAC pairs
### Locally
Run the script locally with

```bash
pipenv run python generate_qid_batch.py <path to config csv>
```

### In kubernetes
To start up the image and connect to its shell in Kubernetes, point your kubectl context at the cluster you wish to run in, then run
```bash
make start-pod
```
Give this a minute to start up, then you should be connected to a bash shell in the pod
Then you can run the script with
```bash
python generate_qid_batch.py unaddressed_batch.csv
```

If you need to run a different config file, you can copy it into the pod once it is started with kubectl. 
While the pod is running, in a different shell window run
```bash
kubectl cp <local path to csv> qid-batch-runner:/app
```

Return to the connected shell in the pod, the file should then be available in the pod in `/app`.

When you are finished exit the pod with `ctrl + D` or by running `exit`. This will disconnect and delete the pod.

# Generating the print files

## Locally build the image

```bash
docker build . -t eu.gcr.io/census-rm-richardweeks01/census-rm-qid-batch-runner:latest
```

Push the image to your project
```bash
docker push eu.gcr.io/census-rm-richardweeks01/census-rm-qid-batch-runner:latest
```

## Running in GCP

You will need to add the Role 'Storage Admin' to the GCP Project Compute Engine Service Account.


Start a Kubernetes Pod
```bash
kubectl apply -f qid-batch-runner.yml
```

Enter the Pod to execute script
```bash
kubectl exec -it qid-batch-runner /bin/bash
```

Run the script
```bash
python generate_print_file.py unaddressed_batch.csv print_files
```

# Tests and Checks

Run the unit tests and style/safety checks with

```bash
make test
```

## Docker
Build the image with
```bash
make build
```
