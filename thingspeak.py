import usocket as socket
import time
import config


class Thingspeak:
    def __init__(self):
        self.BASE_URL = config.BASE_URL
        self.WRITE_API_KEY = config.WRITE_API_KEY

    def create_url(self, field, value):
        url = (
            self.BASE_URL
            + "update?api_key="
            + self.WRITE_API_KEY
            + "&"
            + field
            + "="
            + str(value)
        )
        return url

    def write_channel_field(self, field, value):
        # if not wlan.isconnected():
        #     wifi_connect()
        print("Sending webhook for...", field, value)
        url = self.create_url(field, value)
        _, _, host, path = url.split("/", 3)
        full_url = "GET /{} HTTP/1.1\r\nHost: {}\r\n\r\n".format(path, host).encode()
        addr = socket.getaddrinfo(host, 80)[0][-1]
        print("Establishing socket connection...")
        s = socket.socket()
        s.connect(addr)
        print("Sending webhook...")
        s.write(full_url)
        data = s.recv(15)
        print(str(data, "utf8"), end="")
        print("\n")
        time.sleep(10)
        s.close()
        print("socket closed")
        return full_url
