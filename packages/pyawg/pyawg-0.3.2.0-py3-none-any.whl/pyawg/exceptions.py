from __future__ import annotations

class PyAWGException(Exception):
    pass


class InvalidChannelNumber(PyAWGException):
    def __init__(self: InvalidChannelNumber, channel) -> None:
        super().__init__(f"Invalid Channel Number: {channel}; please check the datatype and/or its value")
