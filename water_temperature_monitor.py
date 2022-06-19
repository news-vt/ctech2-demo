from __future__ import annotations
import BlynkLib as bl
import BlynkTimer as bt
from pathlib import Path
import sys
import yaml
from datetime import datetime
import random


def eprint(*args, **kwargs):
    """Print to standard error."""
    print(*args, file=sys.stderr, **kwargs)


# Load configuration info.
# blynk_config_path = Path('config.yml').expanduser()
blynk_config_path = Path(sys.argv[0]).with_suffix('').with_suffix('.yml')
if blynk_config_path.exists():
    with open(blynk_config_path, 'r') as f:
        blynk_config = yaml.safe_load(f)
else:
    eprint(f"YAML config file not found")
    sys.exit(1)



# Initialize Blynk.
blynk = bl.Blynk(
    auth=blynk_config['BLYNK_AUTH_TOKEN'],
    tmpl_id=blynk_config['BLYNK_TEMPLATE_ID'],
)

# Create BlynkTimer Instance
timer = bt.BlynkTimer()

# Dictionary of Blynk virtual pin numbers.
BLYNK_PINS = {
    'led_green': 0,
    'led_red': 1,
    'temperature': 2,
    'time': 3,
}


@blynk.on('connected')
def blynk_connected(ping: float):
    """Connection callback."""
    print(f"Blynk connected (ping: {ping} ms)")
    device_on()


@blynk.on('disconnected')
def blynk_disconnected():
    """Disconnection callback."""
    print(f"Blynk disconnected")


def device_on():
    blynk.virtual_write(BLYNK_PINS['led_green'], 1)
    blynk.virtual_write(BLYNK_PINS['led_red'], 0)


def device_off():
    blynk.virtual_write(BLYNK_PINS['led_green'], 0)
    blynk.virtual_write(BLYNK_PINS['led_red'], 1)


def read_temperature() -> float:
    return random.uniform(-100, 100)

def blynk_set_temperature_value():
    update_time = datetime.now()
    temperature_value = read_temperature()
    blynk.virtual_write(BLYNK_PINS['temperature'], temperature_value)
    blynk.virtual_write(BLYNK_PINS['time'], f"{update_time}")
    print(f"Temperature Update: {temperature_value} ºF ({update_time})")


# Add Timers
timer.set_interval(1, blynk_set_temperature_value)

print('Press CTRL+C to terminate ...')
while True:

    try:
        blynk.run()
        timer.run()
    except KeyboardInterrupt:
        device_off()
        sys.exit(0)