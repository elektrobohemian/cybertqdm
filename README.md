# cybertqdm

`cybertqdm` is a wrapper around [`tqdm`](https://pypi.org/project/tqdm/) that will also display on an external e-ink display connected via USB.

It is called `cybertqdm` because it turns `tqdm` into a _cyber-physical system_ (Yes, that's an existing term, see the [Wikipedia](https://en.wikipedia.org/wiki/Cyber-physical_system)). It will show a process bar as illustrated below.

![cybertqdm running on the e-ink display](https://8bit-inferno.de/_persistent/img/cybertqdm.gif))

## Using `cybertqdm`

As `cybertqdm` wraps [`tqdm`](https://pypi.org/project/tqdm/) it works exactly the same. As a result, normal `tqdm` output will be printed to the console accompanied by a progess bar on an external e-ink display.

```python
from cybertqdm import cybertqdm
import time

for _ in cybertqdm(60, desc="Loosing faith in humanity...", epaper_interval=10):
        time.sleep(0.5)
```

Please note that the e-ink display will not update as fast as the `tqdm` console output. The refresh interval is controlled by `epaper_interval` (in seconds).

If no e-ink display is available while using `cybertqdm`, a warning is displayed and normal `tqdm` operation is unaffected.

## Installation

In contrast to most other PyPi packages, `cybertqdm` is a _cyber-physical system_. Thus, you will have to satisfy certain hardware requirements and software requirements on your embedded device. 

### Operating System Requirements

`cybertqdm` has been tested with the following operating systems (OS):

| OS  | Supported |
|-------|-----|
| Linux (Ubuntu) | ✔ |
| macOS (27.2.x)    | ✔ |
| Windows (11)    | ✔ |

The package might work on other OS as well because it is implemented in pure Python.

When using Linux, access to `/dev/ttyACM*` is often prohibited. Therefore, you must grant the appropriate permissions to the user running `cybertqm`:

```
sudo usermod -aG dialout $USER   # Debian/Ubuntu/Fedora
```

After a logout, `cybertqdm` should work as expected.

### Hardware Requirements

The current version of `cybertqdm` requires the following components:

1. One [Raspberry Pi Pico 2](https://www.raspberrypi.com/products/raspberry-pi-pico-2/) with a (pre-)soldered header. A Pi Pico might also work but `cybertqdm` is only tested on a Pi Pico 2.
2. One [Waveshare e-paper 2.13 inch display module](https://www.waveshare.com/wiki/Pico-ePaper-2.13) (250×122 pixels, black and white)
3. One USB-Micro to whatever-you-need-USB __data__ cable

### Hardware Setup

You only have to follow these steps once if you don't change your Pico 2 setup afterwards. If you reconnect your Pico 2 it will work directly – on every computer that has `cybertqdm` installed.

1. Install MicroPython on your Raspberry Pico 2 following the [official instructions](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html).
2. Copy the necessary files to your Raspberry Pico 2:
   - All necessary files come bundled with the PyPi package. In order to retrieve them, run the following Python script:
    
    ```python
        import cybertqdm as ctqdm
        from cybertqdm.diagnostics import show_device_files
        from importlib.resources import files

        print("cybertqdm version: "+ ctqdm.__version__)
        show_device_files()
    ```
   - The result should look similar to this sample output (assuming you are using [uv](https://github.com/astral-sh/uv) as a package manager):
    ```python
        cybertqdm version: 0.1.x
        The following files need to be copied to the device:
            .../.cache/uv/archive-v0/xQJrc_fVJrWXacY9/lib/python3.15/site-packages/cybertqdm/device/epd.py 
            .../.cache/uv/archive-v0/xQJrc_fVJrWXacY9/lib/python3.15/site-packages/cybertqdm/device/main.py
    ```
    - Now copy the files to your Pico 2 using `mpremote` using the paths shown above:
    ```
        mpremote cp <your_path>main.py :main.py
        mpremote cp <your_path>epd.py :epd.py
    ```
    - Then test the installation: `mpremote exec "import main"` which should print `init` etc. if everything worked correctly. You can close the running script by pressing Ctrl-C.
    - Reset your Pico 2 using `mpremote reset` which also starts `main.py` automatically.
    - To check wheter the communication with the Pico 2 works, run the following diagnosis which provides help to fix common issues:
    ```python
        from cybertqdm.diagnostics import run_checks

        run_checks()
    ```
    - If everthing works as expected, the result will look like as shown below. Please note that the actual `/dev/` path depends on your operating system. Otherwise, diagnostics and tips to fix your problem will be output.
    ```
        Pico 2 detected at port: /dev/cu.usbmodem11101
        Port opened.

        Sending: 0/10 ... OK
        Sending: 5/10 ... OK
        Sending: 10/10 ... OK

        Pico 2 works as expected.
    ```
