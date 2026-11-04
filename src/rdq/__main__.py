import argparse
import hashlib
from datetime import date

import pandas as pd

from .generator import WorldConfig, generate_world


def checksum(frame: pd.DataFrame) -> str:
    digest = hashlib.sha256()
    digest.update(repr(tuple(frame.columns)).encode("utf-8"))
    digest.update(repr(tuple(str(dtype) for dtype in frame.dtypes)).encode("utf-8"))
    digest.update(pd.util.hash_pandas_object(frame, index=True).to_numpy().tobytes())
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a fictional synthetic retail world.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--stores", type=int, default=10)
    parser.add_argument("--products", type=int, default=200)
    parser.add_argument("--history-days", type=int, default=365)
    parser.add_argument("--future-days", type=int, default=28)
    parser.add_argument("--start-date", type=date.fromisoformat, default=date(2024, 1, 1))
    args = parser.parse_args()
    try:
        config = WorldConfig(**vars(args))
        world = generate_world(config)
    except ValueError as error:
        parser.error(str(error))

    print(f"Synthetic retail world | seed={config.seed}")
    for name, frame in world.items():
        print(f"\n{name}: {len(frame):,} rows | SHA-256 {checksum(frame)}")
        print(frame.head(3).to_string(index=False))


if __name__ == "__main__":
    main()
