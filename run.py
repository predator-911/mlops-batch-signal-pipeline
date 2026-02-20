import argparse
import logging
import sys
import os
import json
import time
import yaml
import pandas as pd
import numpy as np


def write_error(output_path, version, message):
    error_payload = {
        "version": version,
        "status": "error",
        "error_message": message
    }
    with open(output_path, "w") as f:
        json.dump(error_payload, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Mini MLOps Batch Pipeline")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--config", required=True, help="Path to config YAML file")
    parser.add_argument("--output", required=True, help="Path to output metrics JSON")
    parser.add_argument("--log-file", required=True, help="Path to log file")

    args = parser.parse_args()

    logging.basicConfig(
        filename=args.log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("Job started")
    start_time = time.time()

    version = "unknown"

    try:
        # ==========================
        # Load Configuration
        # ==========================
        if not os.path.exists(args.config):
            raise FileNotFoundError("Configuration file not found.")

        with open(args.config, "r") as f:
            config = yaml.safe_load(f)

        seed = config.get("seed")
        window = config.get("window")
        version = config.get("version")

        if seed is None or window is None or version is None:
            raise ValueError("Invalid configuration file structure.")

        np.random.seed(seed)

        logging.info(f"Config loaded: seed={seed}, window={window}, version={version}")

        # ==========================
        # Load Data
        # ==========================
        if not os.path.exists(args.input):
            raise FileNotFoundError("Input CSV file not found.")

        df = pd.read_csv(args.input)

        if df.empty:
            raise ValueError("Input CSV file is empty.")

        if "close" not in df.columns:
            raise ValueError("Required column 'close' not found in dataset.")

        rows_processed = len(df)

        logging.info(f"Data loaded: {rows_processed} rows")

        # ==========================
        # Rolling Mean Calculation
        # ==========================
        df["rolling_mean"] = df["close"].rolling(window=window).mean()
        logging.info(f"Rolling mean calculated with window={window}")

        # ==========================
        # Signal Generation
        # ==========================
        df["signal"] = (df["close"] > df["rolling_mean"]).astype(int)
        df["signal"] = df["signal"].fillna(0)

        logging.info("Signals generated")

        # ==========================
        # Metrics Calculation
        # ==========================
        signal_rate = float(df["signal"].mean())
        latency_ms = int((time.time() - start_time) * 1000)

        metrics = {
            "version": version,
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": round(signal_rate, 4),
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success"
        }

        with open(args.output, "w") as f:
            json.dump(metrics, f, indent=2)

        logging.info(
            f"Metrics: signal_rate={round(signal_rate,4)}, rows_processed={rows_processed}"
        )
        logging.info(f"Job completed successfully in {latency_ms}ms")

        print(json.dumps(metrics, indent=2))
        sys.exit(0)

    except Exception as e:
        logging.error(str(e))
        write_error(args.output, version, str(e))
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
