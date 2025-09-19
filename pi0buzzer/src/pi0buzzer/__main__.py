
import click
import pigpio
import json
from .driver import Buzzer, MusicBuzzer

@click.group()
def cli():
    pass

@cli.command()
@click.argument('pin', type=int)
def init(pin):
    """Initializes the buzzer on the specified GPIO pin."""
    pi = pigpio.pi()
    if not pi.connected:
        raise click.ClickException("Could not connect to pigpio daemon. Is it running?")
    buzzer = Buzzer(pi, pin)
    buzzer.off()
    pi.stop()
    click.echo(f"Buzzer initialized on GPIO {pin} and config saved to buzzer.json")

@cli.command()
@click.option('--pin', type=int, default=None, help='GPIO pin for the buzzer')
def playmusic(pin):
    """Play music with the buzzer using the keyboard."""
    pi = pigpio.pi()
    if not pi.connected:
        raise click.ClickException("Could not connect to pigpio daemon. Is it running?")

    if pin is None:
        try:
            with open('buzzer.json', 'r') as f:
                config = json.load(f)
                pin = config['pin']
        except FileNotFoundError:
            raise click.ClickException("Buzzer not initialized. Please run 'pi0buzzer init <pin>' first or specify a pin with --pin.")

    music_buzzer = MusicBuzzer(pi, pin)
    music_buzzer.play_music()
    pi.stop()

if __name__ == '__main__':
    cli()
