# import glob # only needed in original macOS version
import sys
import time
from importlib.metadata import version
from importlib.resources import files

try:
    from cybertqdm import (
        find_pico_ports,
    )  # if diagnostics.py is run directly, we have to adjust the import
except ImportError:
    from .cybertqdm import (
        find_pico_ports,
    )  # this is the import used when being called as part of the package

try:
    import serial
except ImportError:
    sys.exit("pyserial not available, run:  'pip install pyserial'")


def read_lines(ser, timeout):
    """reads everthing sent by the Pico 2 within the defined timeout."""
    end = time.time() + timeout
    buf = ""
    while time.time() < end:
        chunk = ser.read(ser.in_waiting or 1).decode(errors="replace")
        buf += chunk
        if "OK" in buf or "ERR" in buf or "Traceback" in buf:
            time.sleep(0.2)
            buf += ser.read(ser.in_waiting).decode(errors="replace")
            break
    return buf.strip()


def diagnose(text):
    if ">>>" in text or "Traceback" in text or "SyntaxError" in text:
        print("-> Pico 2 is in REPL mode, 'main.py' is NOT running or has crashed.")
        print("   For more details, run:  'mpremote run main.py' to show errors ")
    elif not text:
        print(
            "-> No answer received. Most likely 'main.py' is not running on the Pico 2."
        )
        print(
            "   Check if 'main.py' exists on the Pico 2 by running 'mpremote ls' and reset afterwards with 'mpremote reset'"
        )


def run_checks():
    # 1) look for the port
    # ports = glob.glob("/dev/cu.usbmodem*") # first version only worked on macOS
    ports = find_pico_ports()
    if not ports:
        sys.exit(
            "Could not detect Pico 2 (/dev/cu.usbmodem*). Are you using a USB data cable? Is the firmware installed? Is 'mpremote' running or an IDE such as Thonny?"
        )
    port = ports[0]
    print(f"Pico 2 detected at port: {port}")

    # 2) open port
    try:
        ser = serial.Serial(port, 115200, timeout=0.2)
    except serial.SerialException as e:
        sys.exit(
            f"Cannot open port: {e}\n-> Is it used by 'mpremote' or an IDE such as Thonny?"
        )
    time.sleep(0.5)
    ser.reset_input_buffer()
    print("Port opened.\n")

    # 3) run a test sequence
    ok = True
    for n, total in [(0, 10), (5, 10), (10, 10)]:
        ser.write(f"Connection test|{n}|{total}|1.00\n".encode())
        ser.flush()
        print(f"Sending: {n}/{total} ... ", end="", flush=True)
        answer = read_lines(ser, timeout=20)  # e-ink display might take a moment
        if f"OK {n} {total}" in answer:
            print("OK")
        else:
            ok = False
            print("ERROR")
            print("   Pico 2 answered:", answer or "(n/a)")
            diagnose(answer)
            break

    ser.close()
    print("\nPico 2 works as expected." if ok else "\nTest failed.")
    return ok


def show_device_files():
    DEVICE = files("cybertqdm") / "device"

    print("cybertqdm version: " + version("cybertqdm"))
    print("The following files need to be copied to the device:")
    for entry in DEVICE.iterdir():
        print(
            "\t" + str(DEVICE) + "/" + entry.name,
            " [dir]" if entry.is_dir() else "",
        )


if __name__ == "__main__":
    ok = run_checks()
    print("")
    if ok:
        show_device_files()
    else:
        print("Aborted listing files on device. Communication test failed.")
