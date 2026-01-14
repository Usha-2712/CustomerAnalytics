from __future__ import annotations

import argparse
from pathlib import Path

import boto3


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload generated data files to S3.")
    parser.add_argument("--bucket", required=True, help="S3 bucket name (must already exist).")
    parser.add_argument("--prefix", default="data-analytics-demo", help="S3 key prefix/folder.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"

    required = ["events.csv", "orders.csv"]
    missing = [name for name in required if not (data_dir / name).exists()]
    if missing:
        raise SystemExit(f"Missing files in {data_dir}. Run scripts/generate_data.py first. Missing: {missing}")

    s3 = boto3.client("s3")

    uploads = [
        ("events.csv", f"{args.prefix}/events/events.csv"),
        ("orders.csv", f"{args.prefix}/orders/orders.csv"),
    ]

    # Optional Parquet uploads (if you generated them)
    if (data_dir / "events.parquet").exists() and (data_dir / "orders.parquet").exists():
        uploads.extend(
            [
                ("events.parquet", f"{args.prefix}/events/events.parquet"),
                ("orders.parquet", f"{args.prefix}/orders/orders.parquet"),
            ]
        )

    for local_name, key in uploads:
        src = data_dir / local_name
        print(f"Uploading {src.name} -> s3://{args.bucket}/{key}")
        s3.upload_file(str(src), args.bucket, key)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


