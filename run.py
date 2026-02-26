import argparse
import yaml
import pandas as pd
import numpy as np
import json
import logging
import sys
import time
from pathlib import Path


def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def write_metrics(output_path, content):
    with open(output_path, "w") as f:
        json.dump(content, f, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)
    args = parser.parse_args()

    start_time = time.time()

    try:
        setup_logging(args.log_file)
        logging.info("Job started")

        #Load & Validate Config
        if not Path(args.config).exists():
            raise FileNotFoundError("Config file not found")

        with open(args.config, "r") as f:
            config = yaml.safe_load(f)

        required_fields = ["seed", "window", "version"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required config field: {field}")

        seed = config["seed"]
        window = config["window"]
        version = config["version"]

        np.random.seed(seed)
        logging.info(f"Config validated: seed={seed}, window={window}, version={version}")

        #Load & Validate Dataset
        try:
            df = pd.read_csv(args.input, encoding="utf-8-sig", quotechar='"')
        except Exception:
            raise ValueError("Invalid CSV format")

        if df.empty:
            raise ValueError("Input CSV is empty")

        df.columns = df.columns.str.strip().str.lower()

        logging.info(f"Columns found: {df.columns.tolist()}")

        if "close" not in df.columns:
            raise ValueError("Missing required column: close")
        
        #Rolling Mean
        logging.info("Computing rolling mean")
        df["rolling_mean"] = df["close"].rolling(window=window).mean()

        df["signal"] = 0
        valid_rows = df["rolling_mean"].notna()
        df.loc[valid_rows, "signal"] = (
            df.loc[valid_rows, "close"] > df.loc[valid_rows, "rolling_mean"]
        ).astype(int)

        logging.info("Signal generation completed")

        #Metrics + Timing
        rows_processed = len(df)
        signal_rate = df.loc[valid_rows, "signal"].mean()
        latency_ms = int((time.time() - start_time) * 1000)

        metrics = {
            "version": version,
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": round(float(signal_rate), 4),
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success",
        }

        write_metrics(args.output, metrics)

        logging.info(f"Metrics: {metrics}")
        logging.info("Job completed successfully")

        print(json.dumps(metrics, indent=2))
        sys.exit(0)

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        version = "unknown"

        try:
            if Path(args.config).exists():
                with open(args.config, "r") as f:
                    temp_config = yaml.safe_load(f)
                    version = temp_config.get("version", "unknown")
        except:
            pass

        error_output = {
            "version": version,
            "status": "error",
            "error_message": str(e),
        }

        write_metrics(args.output, error_output)

        logging.exception("Job failed")
        print(json.dumps(error_output, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()