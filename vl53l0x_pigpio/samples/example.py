#!/usr/bin/env python

import click
import time
import pigpio
from vl53l0x_pigpio.driver import VL53L0X
from vl53l0x_pigpio.my_logger import get_logger


@click.command()
@click.option(
    "--count", "-c", type=int, default=10, show_default=True, help="count"
)
@click.option(
    "--interval", "-i", type=float, default=1.0, show_default=True,
    help="interval seconds"
)
@click.option("--debug", "-d", is_flag=True, default=False, help="debug flag")
def main(
    count: int, interval: float, debug: bool
) -> None:
    log = get_logger(__name__, debug)
    log.debug("count=%s, interval=%s", count, interval)

    pi = pigpio.pi()
    if not pi.connected:
        raise click.ClickException("cannot connect pigpiod")

    try:
        with VL53L0X(pi, debug=debug) as sensor:
            for i in range(count):
                distance: int = sensor.get_range()
                if distance > 0:
                    click.echo(f"{i + 1}/{count}: {distance} mm")
                else:
                    click.echo(f"{i + 1}/{count}: 無効なデータ。")
                time.sleep(interval)
    finally:
        pi.stop()


if __name__ == "__main__":
    main()
