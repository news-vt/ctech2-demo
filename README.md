# ctech2-demo
Demo materials for C-Tech^2 summer camp.

## Blynk.io Setup

1. First create an account with [Blynk.io](https://blynk.cloud/). 
2. Create **templates** and **devices** for the `water temperature sensor`, and the `power strip`. 
3. Copy/paste the configuration code for each device into a YAML file with the same name as the Python file you are trying to run. For example, for the power strip you will create a file `power_strip.yml` that looks sort of like this:
    ```yaml
    BLYNK_TEMPLATE_ID: "<some id>"
    BLYNK_DEVICE_NAME: "<some name>"
    BLYNK_AUTH_TOKEN: "<some auth token"
    ```
4. Modify the Blynk **virtual pin** and **physical GPIO pin** assignments to match those of your Raspberry Pi and Blynk device online.

## Quickstart Guide

### Pi Camera Demo
```bash
$ python3 picam_demo.py
```

### Object Detection Demo
```bash
# Run object detection script using 180-degree camera rotation.
$ python3 object_detection.py -m ssd_mobilenet_v1_1_metadata_1.tflite -l labelmap.txt -r 180
```


## Raspberry Pi Installation Guide

1. If running on macOS ensure that you have [XQuartz](https://www.xquartz.org/) installed.
2. On RPi run the installer script:
    ```bash
    $ sudo install_rpi.sh
    ```
3. Enable X forwarding in `/etc/ssh/sshd_config` via setting:
     ```bash
     X11Forwarding yes
     ```
4. Must set `DISPLAY` env variable on RPi. Add the following to `~/.bashrc` or `~/.zshrc`:
    ```bash
    # For X11 forwarding
    export DISPLAY=localhost:10.0
    ```
5. Download the example TensorFlow Lite model which has been pre-trained on the COCO dataset:
    ```bash
    $ curl -L https://tfhub.dev/tensorflow/lite-model/ssd_mobilenet_v1/1/metadata/1?lite-format=tflite --output ssd_mobilenet_v1_1_metadata_1.tflite
    ```
6. Unzip the model file to reveal a new labels file called `labelmap.txt`:
    ```bash
    # Will unpack a new file called `labelmap.txt`
    $ unzip ssd_mobilenet_v1_1_metadata_1.tflite
    ```
