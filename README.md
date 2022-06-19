# ctech2-demo
Demo materials for C-Tech^2 summer camp.

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