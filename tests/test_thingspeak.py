import pytest
from unittest.mock import patch
from unittest.mock import MagicMock
import struct as ustruct
import sys

# mock Socket
mock_usocket = MagicMock()
sys.modules["usocket"] = mock_usocket

from thingspeak import Thingspeak

thingspeak = Thingspeak()


def mock_write_channel_field(self, values):
    value_string = str()
    for value in values:
        field = value[0]
        value = str(value[1])
        value_string = value_string + "&" + field + "=" + value
        print(value_string)

    url = self.BASE_URL + "update?api_key=" + self.WRITE_API_KEY + value_string
    _, _, host, path = url.split("/", 3)
    full_url = "GET /{} HTTP/1.1\r\nHost: {}\r\n\r\n".format(path, host).encode()
    print(full_url)
    return full_url


def test_create_url():
    values = [("field1", 256)]
    assert (
        thingspeak.create_url(values)
        == "https://api.thingspeak.com/update?api_key={{write api key}}&field1=256"
    )


def test_create_url_two_values():
    values = [("field1", 256), ("field2", 512)]
    assert (
        thingspeak.create_url(values)
        == "https://api.thingspeak.com/update?api_key={{write api key}}&field1=256&field2=512"
    )


@patch.object(Thingspeak, "write_channel_field", mock_write_channel_field)
def test_write_channel_field():
    values = [("field2", 512)]
    assert (
        thingspeak.write_channel_field(values)
        == b"GET /update?api_key={{write api key}}&field2=512 HTTP/1.1\r\nHost: api.thingspeak.com\r\n\r\n"
    )


@patch.object(Thingspeak, "write_channel_field", mock_write_channel_field)
def test_write_channel_field_two_values():
    values = [("field1", 256), ("field2", 512)]
    assert (
        thingspeak.write_channel_field(values)
        == b"GET /update?api_key={{write api key}}&field1=256&field2=512 HTTP/1.1\r\nHost: api.thingspeak.com\r\n\r\n"
    )
