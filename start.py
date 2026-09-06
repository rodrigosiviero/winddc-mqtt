from __future__ import annotations

import argparse
import logging
from pathlib import Path

from config import load_config
from service import Controller

ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Windows DDC/CI to MQTT bridge")
    parser.add_argument("--config", type=Path, default=ROOT / "config.yml")
    parser.add_argument("--check", action="store_true", help="Read monitor identities without changing settings")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(ROOT / "winddc.log", encoding="utf-8"), logging.StreamHandler()],
    )
    controller = Controller(load_config(args.config))
    if args.check:
        for index, description in enumerate(controller.check()):
            print(f"{index}: {description}")
        return 0
    controller.start()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
