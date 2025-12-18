import os
import time as system_time
import wifi
import board
import adafruit_cst8xx
from screens.BroadcastScreen import BroadcastScreen
from screens.MenuScreen import MenuScreen
from screens.ReactScreen import ReactScreen

# Shared state for screen switching
app_state = {
    "current_screen": "menu_screen",
    "last_brew_time": None,
    "reset_react_options": False
    }
            
display = board.DISPLAY
ctp = adafruit_cst8xx.Adafruit_CST8XX(board.I2C())

ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")

thank_you_react_webhook = os.getenv("THANKS_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK")
coffee_parrot_react_webhook = os.getenv("COFFEE_PARROT_REACT_TO_LAST_MESSAGE_SLACK_WEBHOOK")

print(f"\nConnecting to {ssid}...")
try:
    wifi.radio.connect(ssid, password)
    print("WiFi Connected!")
except Exception as e:
    print(f"WiFi Error: {e}")

# ------------------- Build UI Once -------------------
menu_screen = MenuScreen(app_state)
broadcast_screen = BroadcastScreen(app_state)
react_screen = ReactScreen(app_state)
display.root_group = menu_screen.get_screen()

# ------------------- Main Loop -------------------
last_screen = app_state["current_screen"]

while True:
    touches = ctp.touches
    if touches and len(touches) > 0:
        touch = touches[0]
        if app_state["current_screen"] == "menu_screen" and menu_screen.is_button_pressed(touch):
            menu_screen.fire_button_callback(touch)
        elif app_state["current_screen"] == "broadcast_screen" and broadcast_screen.is_button_pressed(touch):
            broadcast_screen.fire_button_callback(touch)
        elif app_state["current_screen"] == "react_screen" and react_screen.is_button_pressed(touch):
            react_screen.fire_button_callback(touch)

        if app_state["reset_react_options"]:
            react_screen.rebuild()
            app_state["reset_react_options"] = False

    # Handle screen switching
    if app_state["current_screen"] != last_screen:
        last_screen = app_state["current_screen"]
        if app_state["current_screen"] == "menu_screen":
            display.root_group = menu_screen.get_screen()
        elif app_state["current_screen"] == "broadcast_screen":
            display.root_group = broadcast_screen.get_screen()
        elif app_state["current_screen"] == "react_screen":
            display.root_group = react_screen.get_screen()
        system_time.sleep(0.5)

    # Update status on menu screen
    if app_state["current_screen"] == "menu_screen":
        menu_screen.updateStatus()

    system_time.sleep(0.0001)
