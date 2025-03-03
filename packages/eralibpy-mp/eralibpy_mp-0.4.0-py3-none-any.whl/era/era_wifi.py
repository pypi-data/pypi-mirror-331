import network
import utime as time

def wifi_log(*args):
    print("[WiFi]", *args)

class WiFi(object):
    def __init__(self, ssid, password, log = wifi_log):
        self.ssid = ssid
        self.password = password
        self.log = log
        self.wifi = network.WLAN(network.STA_IF)

    def connect(self):
        try:
            self.log("Connecting to WiFi network '{}'".format(self.ssid))
            self.wifi.active(True)
            self.wifi.connect(self.ssid, self.password)
            while not self.wifi.isconnected():
                time.sleep(1)
                self.log("WiFi connect retry ...")
            self.log("WiFi IP:", self.localIP())
        except Exception as w_exc:
            self.log("Failed to connect to WiFi: ", w_exc)

    def connected(self):
        return self.wifi.isconnected()

    def localIP(self):
        return self.wifi.ifconfig()[0] if self.connected() else None

    def RSSI(self):
        return self.wifi.status("rssi")

    def run(self):
        try:
            if not self.connected():
                self.connect()
        except KeyboardInterrupt:
            raise
