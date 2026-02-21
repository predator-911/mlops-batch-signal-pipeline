# MLOps Batch Signal Pipeline

## Overview

This project implements a miniature MLOps-style batch processing pipeline designed to demonstrate:

- Deterministic execution using configuration
- Structured metrics output
- Comprehensive logging
- Robust error handling
- Docker-based containerized deployment

The pipeline processes cryptocurrency OHLCV data and computes a rolling mean–based trading signal using the `close` price.

---

## Project Structure


mlops-batch-signal-pipeline/
│
├── run.py
├── config.yaml
├── data.csv
├── requirements.txt
├── Dockerfile
├── README.md
├── metrics.json
└── run.log


---

## Configuration

The application is driven by `config.yaml`:

```yaml
seed: 42
window: 5
version: "v1"

seed ensures deterministic execution.

window defines the rolling mean window size.

version is included in structured output for traceability.

Processing Logic

The pipeline performs the following steps:

Loads configuration.

Sets NumPy random seed.

Loads and validates input CSV.

Computes rolling mean on the close column.

Generates signal:

1 if close > rolling_mean

0 otherwise

Computes metrics:

rows_processed

signal_rate

latency_ms

Writes structured JSON output.

Logs full execution trace.

Local Setup

Install dependencies:

pip install -r requirements.txt
Local Execution
python run.py --input data.csv --config config.yaml \
    --output metrics.json --log-file run.log
Docker Execution (Mandatory Requirement)

Build the Docker image:

docker build -t mlops-task .

Run the container:

docker run --rm mlops-task

The container will:

Execute the batch job automatically

Generate metrics.json

Generate run.log

Print metrics to stdout

Exit with code 0 on success

Expected Output Format

Successful execution produces:

{
  "version": "v1",
  "rows_processed": 10000,
  "metric": "signal_rate",
  "value": 0.4989,
  "latency_ms": 29,
  "seed": 42,
  "status": "success"
}

If an error occurs:

{
  "version": "v1",
  "status": "error",
  "error_message": "Description of error"
}
Logging

Execution logs are written to run.log and include:

Job start

Configuration details

Data ingestion summary

Rolling mean computation

Signal generation

Metrics summary

Completion status

Error messages (if any)

Dependencies

pandas

numpy

pyyaml

Notes

The close column is exclusively used for all calculations.

Execution is reproducible via configuration-based seeding.

No hard-coded paths or parameters are used.

The pipeline is designed to run as a containerized batch job.
