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


def mock_write_channel_field(self, field, value):
    url = (
        "https://api.thingspeak.com/update?api_key={{write api key}}&"
        + field
        + "="
        + str(value)
    )
    _, _, host, path = url.split("/", 3)
    full_url = "GET /{} HTTP/1.1\r\nHost: {}\r\n\r\n".format(path, host).encode()
    print(full_url)
    return full_url


def test_create_url():
    field = "field1"
    value = 256
    assert (
        thingspeak.create_url(field, value)
        == "https://api.thingspeak.com/update?api_key={{write api key}}&field1=256"
    )


@patch.object(Thingspeak, "write_channel_field", mock_write_channel_field)
def test_write_channel_field():
    field = "field2"
    value = 512
    assert (
        thingspeak.write_channel_field(field, value)
        == b"GET /update?api_key={{write api key}}&field2=512 HTTP/1.1\r\nHost: api.thingspeak.com\r\n\r\n"
    )
