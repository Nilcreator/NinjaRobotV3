#
# (c) 2025 Yoichi Tanibayashi
#
"""キャリブレーション機能のサンプルコード"""
import click
import pigpio
from pathlib import Path
from vl53l0x_pigpio import VL53L0X
from vl53l0x_pigpio.config_manager import get_default_config_filepath, load_config, save_config

@click.command()
@click.option("--distance", "-d", type=int, default=100, show_default=True, help="distance to target [mm]")
@click.option("--count", "-c", type=int, default=10, show_default=True, help="count")
@click.option(
    "--config-file", "-C", type=click.Path(path_type=Path),
    default=get_default_config_filepath(), show_default=True,
    help="Path to the configuration file"
)
@click.option("--debug", is_flag=True, default=False, help="debug flag")
def main(distance: int, count: int, config_file: Path, debug: bool) -> None:
    

    pi = pigpio.pi()
    if not pi.connected:
        raise click.ClickException("cannot connect to pigpiod")

    try:
        # Load existing offset if config file exists
        initial_offset = 0
        if config_file.exists():
            config = load_config(config_file)
            if "offset_mm" in config:
                initial_offset = config["offset_mm"]
                click.echo(f"既存のオフセット値 {initial_offset} mm を {config_file} から読み込みました。")

        with VL53L0X(pi, debug=debug, config_file_path=config_file) as sensor:
            # Set initial offset if loaded from config
            if initial_offset != 0:
                sensor.set_offset(initial_offset)

            click.echo(f"{distance}mmの距離にターゲットを置いてください。")
            click.echo("準備ができたらEnterキーを押してください...")
            input()

            offset = sensor.calibrate(distance, count)
            click.echo(f"計算されたオフセット値: {offset} mm")

            click.echo("オフセット値をセンサーに設定します。")
            sensor.set_offset(offset)

            # Save the new offset to the config file
            config_data = {"offset_mm": offset}
            save_config(config_file, config_data)
            click.echo(f"新しいオフセット値を {config_file} に保存しました。")

            click.echo("オフセット適用後の距離を測定します...")
            measured_distance = sensor.get_range()
            click.echo(f"補正後の測定距離: {measured_distance} mm")

    finally:
        pi.stop()

if __name__ == "__main__":
    main()
