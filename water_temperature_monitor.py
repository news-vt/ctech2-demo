"""Water Temperature Sensor (ds18b20)

This script interacts with Blynk.io to upload water temperature values.

The temperature sensor (ds18b20) communicates over a 1-wire interface.
By default, this is GPIO 4 on the Raspberry Pi.
"""

from __future__ import annotations
import BlynkLib as bl
import BlynkTimer as bt
from pathlib import Path
import sys
import yaml
from datetime import datetime
import random
import time
import glob


base_dir = Path('/sys/bus/w1/devices')
device_folders = glob.glob(str(base_dir/'28*'))
if len(device_folders) == 0:
    print('No 1-wire devices found')
    sys.exit(1)
elif len(device_folders) > 1:
    print('Multiple 1-wire devices found:')
    for df in device_folders:
        print(df)

# Isolate 1-wire device to use.
device_folder = Path(device_folders[0])
device_file = device_folder/'w1_slave'
print(f'Using 1-wire device: {device_file}')


# Load configuration info.
# blynk_config_path = Path('config.yml').expanduser()
blynk_config_path = Path(sys.argv[0]).with_suffix('').with_suffix('.yml')
if blynk_config_path.exists():
    with open(blynk_config_path, 'r') as f:
        blynk_config = yaml.safe_load(f)
else:
    print(f"YAML config file not found")
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


def read_temperature_raw(device: Path):
    with open(device, 'r') as f:
        lines = f.readlines()
    return lines
 
def read_temperature(device: Path) -> tuple[float, float]:
    lines = read_temperature_raw(device)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temperature_raw(device)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

def blynk_set_temperature_value():
    update_time = datetime.now()
    temperature_value = read_temperature(device_file)
    blynk.virtual_write(BLYNK_PINS['temperature'], temperature_value[0])
    blynk.virtual_write(BLYNK_PINS['time'], f"{update_time}")
    print(f"Temperature Update: {temperature_value[0]} ºC / {temperature_value[1]} ºF ({update_time})")


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