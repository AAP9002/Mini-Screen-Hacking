import adafruit_requests
import adafruit_connection_manager
import wifi
import adafruit_requests

pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)

class SendRequest:
    @staticmethod
    def post(webhook_url, payload = {}):        
        with requests.post(webhook_url, json=payload) as response:
            print(response.json())