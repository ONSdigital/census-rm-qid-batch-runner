# Census RM QID Batch Runner

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

<!--->### In Kubernetes TODO<--->



## Tests and Checks

Run the unit tests and style/safety checks with

```bash
make test
```
