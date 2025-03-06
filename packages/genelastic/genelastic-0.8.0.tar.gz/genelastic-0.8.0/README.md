# genelastic

Storing of genetics data into an Elasticsearch database.

## Prerequisites

- `python` >= 3.11
- `make`

## Installation

To install dependencies, run the following command:

```bash
python -m venv .venv
source .venv/bin/activate
make install.deps
```

## Configuration

To start the **API server**, the following environment variables should be defined:

- `GENAPI_ES_URL`: URL of the Elasticsearch server,
- `GENAPI_ES_ENCODED_API_KEY`: Encoded API key,
- `GENAPI_ES_INDEX_PREFIX`: Prefix to identify indices of interest,
- `GENAPI_ES_CERT_FP`: Certificate fingerprint of the Elasticsearch server.

Then, run the following command:

```bash
make start-api
```

To start the **UI server**, the following environment variables should be defined:

- `GENUI_API_URL`: URL of the API server.

Then, run the following command:

```bash
make start-ui
```

## Developers

This project uses [pre-commit](https://pre-commit.com/) to manage Git hooks scripts. To install project hooks, run:

```bash
pre-commit install
```

After that, each commit will succeed only if all hooks (defined in `.pre-commit-config.yaml`) pass.

If necessary (though not recommended),
you can skip these hooks by using the `--no-verify` / `-n` option when committing:

```bash
git commit -m "My commit message" --no-verify # This commit will not run installed hooks.
```
