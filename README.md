# fabos-nexus-adapter
Adapter service to query a nexus instance and update an SLM service offering version option by key

# set environment

all variables available:

| Variable Name | Description | Default |
| ------------- | ----------- | ------- |
| NEXUS_URL     |     The URL of the nexus to pull data from     |    (required)     |
| NEXUS_USER    |      The nexus username to access the data       |   (required)       |
| NEXUS_PASSWORD       |     The nexus password to access the data        |      (required)    |
| MODEL_FILETYPE       |         The filetype to filter the fetched data    |    (required, e.g. '.model')      |
| SLM_HOST       |     The SLM host to push service offering options        |    (required)     |
| SLM_KEYCLOAK_HOST        |    The SLM keycloak host         |   ${SLM_HOST}:7080      |
| SLM_SERVICE_REGISTRY_HOST       |    The SLM service registry host           |   ${SLM_HOST}:9020       |
| SLM_USER       |     The SLM user used to add the service offering options        |   (required)      |
| SLM_PASSWORD       |   The SLM password used to add the service offering options            |   (required)      |
| SLM_OFFERING_UUID       |    The SLM service offering UUID         |    (required)     |
| SLM_OFFERING_VERSION_UUID       |   The SLM service offering version UUID           |    (required)     |
| SLM_OFFERING_VERSION_OPTION_KEY       |    The key of the SLM service offering version option to update          | (required)        
UPDATE_INTERVAL    |    The update interval **in seconds** | *60* |


# usage

1. create your `.env`-file based on `sample.env` with the variables to use ...
2. start the compose with
    ```console
    docker compose up
    ```