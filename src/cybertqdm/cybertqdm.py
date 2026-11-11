import glob
import time
import warnings

import serial
from serial.tools import list_ports
from tqdm import tqdm

__all__ = ["CyberTqdm", "cybertqdm"]

PICO_VID = (
    0x2E8A  # Raspberry Pi vendor ID; used to detect the device in macOS and Linux
)


def find_pico_ports():
    """Check serial ports of connected Pico devices, should work on any OS."""
    return sorted(p.device for p in list_ports.comports() if p.vid == PICO_VID)


class CyberTqdm(tqdm):
    """A tqdm wrapper that also prints a progres bar onto a e-ink display.

    To prevent wearing down the e-ink display too fast, console and e-ink update interval differs.

    - console: normal tqdm update interval
    - e-ink display: updates at start, then every `epaper_interval` seconds with a final update when the observed task ends.
    - If no Pico 2 is detected or the connection is lost, a warning is output. Console operation remains unaffected.
    """

    _ser = None  # common connection for progress bars
    _unavailable = False  # in case of errors do not try to reconnect again and again...

    def __init__(self, *args, port=None, epaper_interval=30, **kwargs):
        self._epaper_interval = epaper_interval
        self._last_send = 0.0
        self._epaper_done = False
        self._open_port(port)
        super().__init__(*args, **kwargs)

    # --- connection ---------------------------------------------------------
    @staticmethod
    def _open_port(port):
        cls = CyberTqdm
        if (cls._ser is not None and cls._ser.is_open) or cls._unavailable:
            return
        if port is None:
            # ports = sorted(glob.glob("/dev/cu.usbmodem*")) # works only on macOS
            ports = find_pico_ports()
            if not ports:
                cls._unavailable = True
                warnings.warn(
                    "E-ink display unavailable – falling back to console output."
                )
                return
            port = ports[0]
        try:
            cls._ser = serial.Serial(port, 115200, timeout=0, write_timeout=2)
        except (serial.SerialException, OSError) as e:
            cls._unavailable = True
            warnings.warn(
                f"E-ink display unavailable ({e}) – falling back to console output."
            )

    @staticmethod
    def _drop_port(err):
        cls = CyberTqdm
        warnings.warn(
            f"Lost connection to e-ink display ({err}) – falling back to console output."
        )
        try:
            cls._ser.close()
        except Exception:
            pass
        cls._ser = None
        cls._unavailable = True

    # --- send data -------------------------------------------------------------
    def _send(self):
        ser = CyberTqdm._ser
        if ser is None or self.disable:
            return
        try:
            if ser.in_waiting:  # drop OK/busy messages from the Pico 2
                ser.read(ser.in_waiting)
            d = self.format_dict
            desc = (
                (self.desc or "").replace("|", "/").replace("\n", " ").strip(": ")[:30]
            )
            n = int(d["n"])
            total = int(d["total"] or 0)
            rate = d["rate"] or 0.0
            ser.write(f"{desc}|{n}|{total}|{rate:.2f}\n".encode())
            ser.flush()
        except (serial.SerialException, OSError) as e:
            self._drop_port(e)
        self._last_send = time.time()

    # --- tqdm hooks ---------------------------------------------------------
    def display(self, msg=None, pos=None):
        if time.time() - self._last_send >= self._epaper_interval:
            self._send()
        return super().display(msg, pos)

    def close(self):
        if not getattr(self, "_epaper_done", True):
            self._epaper_done = True
            self._send()  # always display final state of the progress bar
        super().close()


def cybertqdm(*args, **kwargs):
    """Shortcut for CyberTqdm(range(*args), **kwargs)."""
    return CyberTqdm(range(*args), **kwargs)


if __name__ == "__main__":
    # quick test: 60 steps, each sleeping for 0.5 seconds, e-ink display update every 10 seconds
    for _ in cybertqdm(60, desc="Loosing faith in humanity...", epaper_interval=10):
        time.sleep(0.5)
