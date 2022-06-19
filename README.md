# ctech2-demo
Demo materials for C-Tech^2 summer camp.


## Raspberry Pi Installation Guide

1. If running on macOS ensure that you have [XQuartz](https://www.xquartz.org/) installed.
2. On RPi run the installer script:
    ```bash
    sudo install_rpi.sh
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