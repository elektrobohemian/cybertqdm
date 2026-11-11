# SPDX-License-Identifier: MIT
# main.py – progress bar display on Waveshare e-ink display (Pico 2/ Pico?)
# used protocol (one row per update):  desc|n|total|rate\n
# expected answers: READY at start; OK/ERR after each row

import sys
import epd as drv

# autodetect driver and partial update method
classes = [n for n in dir(drv) if n.startswith("EPD_")]
landscape = [n for n in classes if "Landscape" in n]
cls_name = (landscape or classes)[0]
epd = getattr(drv, cls_name)()
partial = getattr(epd, "display_Partial", None) or getattr(epd, "displayPartial", None)

W = getattr(epd, "width", 250)
H = getattr(epd, "height", 122)
if W < H:
    W, H = H, W

try:
    epd.Clear(0xFF)
except TypeError:
    epd.Clear()


def draw(desc, n, total, rate):
    epd.fill(0xFF)
    epd.text(desc[:30], 4, 6, 0x00)
    frac = n / total if total else 0
    epd.rect(4, 36, W - 8, 24, 0x00)
    epd.fill_rect(4, 36, int((W - 8) * frac), 24, 0x00)
    epd.text("{}/{}  {:.0f}%".format(n, total, frac * 100), 4, 72, 0x00)
    epd.text("{:.2f} it/s".format(rate), 4, 90, 0x00)


print("READY", cls_name)
count = 0
while True:
    line = sys.stdin.readline().strip()
    if not line:
        continue
    try:
        desc, n, total, rate = line.split("|")
        n, total = int(n), int(total)
        draw(desc, n, total, float(rate))
        if (
            count % 10 == 0 or not partial
        ):  # refresh e-ink display completely every 10 updates
            epd.init()
            epd.display(epd.buffer)
        else:
            partial(epd.buffer)
        count += 1
        print("OK", n, total)
    except Exception as e:
        print("ERR", repr(e))
