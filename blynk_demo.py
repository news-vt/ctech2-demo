"""This code is the simplest example of using Blynk with Python.

To use it, you first need to go to <https://blynk.cloud> and create a template and device.
Once you do those 2 things, come back here and paste the `BLYNK_AUTH_TOKEN` and `BLYNK_TEMPLATE_ID`
values into the variables below.
"""
from __future__ import annotations
import BlynkLib as bl
import BlynkTimer as bt
from datetime import datetime

###
# Paste the tokens here!
###
BLYNK_AUTH_TOKEN = "<some auth token>"
BLYNK_TEMPLATE_ID = "<some template ID>"


# Initialize Blynk.
blynk = bl.Blynk(
    auth=BLYNK_AUTH_TOKEN,
    tmpl_id=BLYNK_TEMPLATE_ID,
)

# Create BlynkTimer Instance
timer = bt.BlynkTimer()


# This function will be called when Blynk connects to the server.
@blynk.on('connected')
def blynk_connected(ping: float):
    """Connection callback."""
    print(f"Blynk connected (ping: {ping} ms)")


# This function will be called when Blynk disconnects to the server.
@blynk.on('disconnected')
def blynk_disconnected():
    """Disconnection callback."""
    print(f"Blynk disconnected")


# Example function to print something.
def print_me():
    print(f"print me {datetime.now()}")

###
# Here is an example of a function which send a value to the Blynk server on pin 0.
# You need to call this function manually.
# An example of when to use this is when you want to send something from your Python script to the Blynk server.
###
def send_value_to_blynk_pin_0():
    pin = 0
    value = 3.14
    blynk.virtual_write(pin, value)

###
# Here is an example of a function which is called automatically when a change happens on the Blynk server for pin 1.
# You do not call this function manually. Instead, Blynk calls it for you automatically.
# An example of when to use this is when you want the Blynk server to send something to the Python script.
###
@blynk.on('V1')
def read_value_from_blynk_pin_1(values):
    print(f"Current value for pin 1 is: {values[0]}")


# Add Timers.
timer.set_interval(1, print_me) # This timer will run the function every 1 second.


# Now run the main loop.
print('Press CTRL+C to terminate ...')
while True:
    blynk.run()
    timer.run()