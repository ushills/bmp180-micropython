import usocket as socket
import time
import config


class Thingspeak:
    def __init__(self):
        self.BASE_URL = config.BASE_URL
        self.WRITE_API_KEY = config.WRITE_API_KEY

    def create_url(self, values):
        value_string = str()
        for value in values:
            field = value[0]
            value = str(value[1])
            value_string = value_string + "&" + field + "=" + value

        url = self.BASE_URL + "update?api_key=" + self.WRITE_API_KEY + value_string
        return url

    # send values list in the form

    def write_channel_field(self, values):
        print("Sending webhook values\n", values)
        url = self.create_url(values)
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
        time.sleep(2)
        s.close()
        print("socket connection closed.\n" + "-"*20)
        return full_url
