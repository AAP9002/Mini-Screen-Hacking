import os
import time as system_time

import adafruit_connection_manager
import wifi
import adafruit_requests

import board
import terminalio
import displayio
from adafruit_display_text import label
from adafruit_display_shapes.roundrect import RoundRect
import adafruit_cst8xx


class TouchButton:
    def __init__(self, x, y, image_path, display_group, callback=None, padding=10):
        self.image = displayio.OnDiskBitmap(image_path)
        self.x = x
        self.y = y
        self.callback = callback
        self.padding = padding

        # Safe width/height fallback (in case BMP metadata failed)
        self.width = getattr(self.image, "width", 200)
        self.height = getattr(self.image, "height", 200)

        self.tilegrid = displayio.TileGrid(
            self.image,
            pixel_shader=self.image.pixel_shader,
            x=self.x,
            y=self.y
        )

        display_group.append(self.tilegrid)

    def isPressed(self, touch):
        raw_x, raw_y = touch["x"], touch["y"]

        # Swap axes before flipping
        tx = raw_y
        ty = display.height - raw_x

        left   = self.x - self.padding
        right  = self.x + self.width + self.padding
        top    = self.y - self.padding
        bottom = self.y + self.height + self.padding

        return left <= tx <= right and top <= ty <= bottom

    def runCallback(self):
        if self.callback:
            self.callback()
            
display = board.DISPLAY
ctp = adafruit_cst8xx.Adafruit_CST8XX(board.I2C())

ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")

brewing_webhook_url = "https://hooks.slack.com/triggers/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"
done_webhook_url = "https://hooks.slack.com/triggers/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"

pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)

print(f"\nConnecting to {ssid}...")
try:
    wifi.radio.connect(ssid, password)
    print("WiFi Connected!")
except Exception as e:
    print(f"WiFi Error: {e}")


isSending = False
displaySendingAnnouncementSeconds = 0


def send_coffee_brewing_message():
    global displaySendingAnnouncementSeconds
    global isSending

    if isSending or displaySendingAnnouncementSeconds > 0:
        return
    
    isSending = True
    
    with requests.get(brewing_webhook_url) as response:
        print(response.json())
        displaySendingAnnouncementSeconds = 2000
        isSending = False
        

def send_coffee_made_message():
    global displaySendingAnnouncementSeconds
    global isSending

    if isSending or displaySendingAnnouncementSeconds > 0:
        return
    
    isSending = True
    
    with requests.get(done_webhook_url) as response:
        print(response.json())
        displaySendingAnnouncementSeconds = 2000
        isSending = False
        


# ------------------- Build UI Once -------------------
screen = displayio.Group()
display.root_group = screen

header = RoundRect(10, 10, 300, 40, 10, fill=0x000000, outline=0xFF00FF, stroke=3)
screen.append(header)

title = label.Label(terminalio.FONT, text="Coffee Broadcast  c|_|", color=0xFFFFFF)
title.x = 25
title.y = 35
title.scale = 2
screen.append(title)

status_label = label.Label(terminalio.FONT, text="", color=0x00FF00)
status_label.x = 5
status_label.y = 225
status_label.scale = 2
screen.append(status_label)

error_status_label = label.Label(terminalio.FONT, text="", color=0xFF0000)
error_status_label.x = 5
error_status_label.y = 225
error_status_label.scale = 2
screen.append(error_status_label)

button_label = label.Label(terminalio.FONT, text="Brewing", scale=2, color=0xFFFFFF)
button_label.x = 30
button_label.y = 65
screen.append(button_label)

buttonDone = TouchButton(180, 80, "/menu.bmp", screen, send_coffee_made_message)
buttonBrewing = TouchButton(10, 85, "/loading.bmp", screen, send_coffee_brewing_message)

button_label_done = label.Label(terminalio.FONT, text="Ready!", scale=2, color=0xFFFFFF)
button_label_done.x = 210
button_label_done.y = 64
screen.append(button_label_done)


# ------------------- Main Loop -------------------
while True:
    touches = ctp.touches
    
    is_sent_notification_showing = displaySendingAnnouncementSeconds > 0

    if touches and len(touches) > 0:
        touch = touches[0]
#         status_label.text = f"{touch}"
        if buttonDone.isPressed(touch) and not is_sent_notification_showing:
            status_label.text = "Sending..."
            buttonDone.runCallback()
            
        elif buttonBrewing.isPressed(touch) and not is_sent_notification_showing:
            status_label.text = "Sending..."
            buttonBrewing.runCallback()

    if is_sent_notification_showing:
        displaySendingAnnouncementSeconds -= 1
        status_label.text = "SENT :) Great Success!"
    else:
        status_label.text = ""

    system_time.sleep(0.0001)

