"""Provide a CLI for MIR meter customer display."""

import argparse
import asyncio
import logging
import sys

from bleak import BleakScanner
from .client import MIRMeter

_LOGGER = logging.getLogger(__package__)
_LOGGER.setLevel(logging.DEBUG)
_LOGGER.addHandler(logging.StreamHandler())
_LOGGER.handlers[0].setFormatter(logging.Formatter("%(asctime)-15s %(name)-8s %(levelname)s: %(message)s"))


async def cli() -> None:
    parser = argparse.ArgumentParser(description="MIR meter console program")
    parser.add_argument("device", help="Device bluetooth name or mac address")
    parser.add_argument("pin", help="Device pin code")
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()

        meter = MIRMeter(BleakScanner, args.device, int(args.pin))
        if await meter.find_device():
            if await meter.check_pin():
                await meter.get_data()
            else:
                print("An incorrect PIN code or meter has blocked you for a while")
        else:
            print("Could not find bluetooth device")


if __name__ == "__main__":
    asyncio.run(cli())
