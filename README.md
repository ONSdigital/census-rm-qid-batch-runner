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

## Running the Script
### Locally
Run the script locally with

```bash
pipenv run python generate_qid_batch.py <path to config csv>
```

### In kubernetes
To start up the image and connect to it's shell in Kubernetes, point your kubectl context at the cluster you wish to run in, then run
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

## Tests and Checks

Run the unit tests and style/safety checks with

```bash
make test
```

## Docker
Build the image with
```bash
make build
```
