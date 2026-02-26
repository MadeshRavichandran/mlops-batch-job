# MLOps Batch Job – 

## Overview

This project implements a minimal production-style MLOps batch job in Python.

It demonstrates:

- Reproducibility (config-driven + deterministic seed)
- Observability (structured logs + machine-readable metrics)
- Deployment readiness (Dockerized, one-command execution)
- Proper failure handling (metrics written on both success and error)

The job computes a rolling mean trading signal from OHLCV data.

---

## What the Program Does

1. Loads configuration from `config.yaml`
2. Validates required fields (`seed`, `window`, `version`)
3. Loads `data.csv`
4. Validates schema (requires `close` column)
5. Computes rolling mean on `close`
6. Generates binary signal:

   signal = 1 if close > rolling_mean else 0

7. Outputs structured metrics JSON
8. Writes detailed logs

---

## Project Structure

run.py  
config.yaml  
data.csv  
requirements.txt  
Dockerfile  
README.md  
metrics.json  
run.log  

---

## Configuration (config.yaml)

```yaml
seed: 42
window: 5
version: "v1"
```

---

## Local Execution

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the batch job

```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

---

## Success Output (metrics.json)

```json
{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.4991,
  "latency_ms": 124,
  "seed": 42,
  "status": "success"
}
```

---

## Failure Example

Simulate failure (missing file):

```bash
python run.py --input wrong.csv --config config.yaml --output metrics.json --log-file run.log
```

Output:

```json
{
  "version": "v1",
  "status": "error",
  "error_message": "Input data file not found"
}
```

Important:

- `metrics.json` is written in both success and failure cases.
- Exit code is:
  - `0` on success
  - Non-zero on failure

This ensures proper observability in production systems.

---

## Logging (run.log)

Logs include:

- Job start timestamp
- Config validation
- Rows loaded
- Rolling mean computation
- Signal generation
- Metrics summary
- Job end status
- Exception details

---

## Docker Execution

### Build Image

```bash
docker build -t mlops-task .
```

### Run Container

```bash
docker run --rm mlops-task
```

Expected behavior:

- Prints final metrics JSON to stdout
- Generates `metrics.json` and `run.log` inside container
- Exit code:
  - `0` for success
  - Non-zero for failure

---

## Reproducibility

- Config-driven execution
- Deterministic seed (`numpy.random.seed`)
- No hardcoded paths
- Fully CLI-based

---

## Error Handling

The system gracefully handles:

- Missing input file
- Invalid CSV format
- Empty file
- Missing `close` column
- Invalid config structure
- Missing config fields

All failures:

- Produce structured error JSON
- Write metrics file
- Exit with non-zero status

---

