from adafruit_display_text import label
from adafruit_display_shapes.roundrect import RoundRect
import displayio
import time as system_time
from components.TouchButton import TouchButton
import terminalio
import os

class MenuScreen:
    def __init__(self, app_state):
        self.app_state = app_state
        self.screen_group = displayio.Group()
        self.ReactButton = None
        self.BroadcastButton = None
        self.status_label = None
        self.build()
        self.setDefaultStatus()

    def openBroadcastScreen(self):
        self.app_state["current_screen"] = "broadcast_screen"

    def openReactScreen(self):
        self.app_state["current_screen"] = "react_screen"

    def build(self):
        header = RoundRect(10, 10, 300, 40, 10, fill=0x000000, outline=0xFF00FF, stroke=3)
        self.screen_group.append(header)

        title = label.Label(terminalio.FONT, text="Manchester-Brews   c|_|", color=0xFFFFFF)
        title.x = 25
        title.y = 35
        title.scale = 2
        self.screen_group.append(title)

        self.status_label = label.Label(terminalio.FONT, text="", color=0x00FF00)
        self.status_label.x = 5
        self.status_label.y = 225
        self.status_label.scale = 2
        self.screen_group.append(self.status_label)

        button_label = label.Label(terminalio.FONT, text="Broadcast", scale=2, color=0xFFFFFF)
        button_label.x = 30
        button_label.y = 65
        self.screen_group.append(button_label)

        self.BroadcastButton = TouchButton(25, 85, "/images/broadcast.bmp", self.screen_group, self.openBroadcastScreen)
        self.ReactButton = TouchButton(180, 85, "/images/react.bmp", self.screen_group, self.openReactScreen)

        button_label_done = label.Label(terminalio.FONT, text="React", scale=2, color=0xFFFFFF)
        button_label_done.x = 210
        button_label_done.y = 64
        self.screen_group.append(button_label_done)

    def setDefaultStatus(self):
        if self.app_state["last_brew_time"]:
            elapsed = int(system_time.monotonic() - self.app_state["last_brew_time"])
            hour = elapsed // 3600
            minutes = elapsed // 60
            seconds = elapsed % 60
            if hour > 0:
                self.status_label.text = f"Last Brewed: {hour}h {minutes%60}m ago"
            else:
                self.status_label.text = f"Last Brewed: {minutes}m {seconds}s ago"
        else:
            self.status_label.text = "Last Brewed: Not yet..."

    def updateStatus(self):
        self.setDefaultStatus()

    def get_screen(self):
        return self.screen_group
    
    def is_button_pressed(self, touch):
        if self.ReactButton.isPressed(touch):
            return True
        elif self.BroadcastButton.isPressed(touch):
            return True
        return False

    def fire_button_callback(self, touch):
        if self.ReactButton.isPressed(touch):
            self.ReactButton.runCallback()
        elif self.BroadcastButton.isPressed(touch):
            self.BroadcastButton.runCallback()
        self.setDefaultStatus()
