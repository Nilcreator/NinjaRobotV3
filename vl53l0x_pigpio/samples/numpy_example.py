"""
An example of using the VL53L0X driver with numpy.
"""

import click
import pigpio
import numpy as np
from vl53l0x_pigpio.driver import VL53L0X


@click.command()
@click.option(
    "--samples", "-s", type=int, default=100, show_default=True,
    help="number of samples"
)
@click.option("--debug", "-d", is_flag=True, default=False, help="debug flag")
def main(samples: int, debug: bool) -> None:
    pass
