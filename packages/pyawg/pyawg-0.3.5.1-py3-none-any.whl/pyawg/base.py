from __future__ import annotations

import json
import logging

import vxi11

from .enums import WaveformType, AmplitudeUnit, FrequencyUnit


class AWG:
    """
    A class to represent an Arbitrary Waveform Generator (AWG) device.

    Attributes:
        ip_addr : str
            The IP address of the AWG device.
        device : vxi11.Instrument | None
            The VXI-11 instrument instance representing the AWG device.
        manufacturer : str
            The manufacturer of the AWG device.
        model : str
            The model of the AWG device.
        serial_number : str
            The serial number of the AWG device.
        fw_version : str
            The firmware version of the AWG device.

    Methods:
        __init__(self, ip_addr: str):
            Initializes the AWG device with the given IP address.
        __str__(self):
            Returns a JSON string representation of the AWG device details.
        close(self):
            Closes the connection to the AWG device.
        get_id(self) -> str:
            Queries the AWG device for its identification string.
        query(self, command):
            Sends a query command to the AWG device and returns the response.
        write(self, command):
            Sends a command to the AWG device.

    """
    ip_addr: str
    device: vxi11.Instrument | None
    manufacturer: str
    model: str
    serial_number: str
    fw_version: str

    def __init__(self: AWG, ip_addr: str):
        """
        Initialize the Arbitrary Waveform Generator (AWG) with the given IP address.

        Args:
            ip_addr (str): The IP address of the AWG device.

        Attributes:
            ip_addr (str): The IP address of the AWG device.
            device (vxi11.Instrument or None): The instrument object representing the AWG device.
            manufacturer (str): The manufacturer of the AWG device.
            model (str): The model of the AWG device.
            serial_number (str): The serial number of the AWG device.
            fw_version (str): The firmware version of the AWG device.

        Raises:
            Exception: If the connection to the AWG device fails.

        """
        self.ip_addr = ip_addr
        self.device = None
        try:
            self.device = vxi11.Instrument(ip_addr)
            self.device.clear()
            logging.debug(f"Connected to AWG at {ip_addr}")
            
            self.manufacturer, self.model, self.serial_number, self.fw_version = self.get_id().strip().split(',')
        except Exception as e:
            logging.error(f"Failed to connect to AWG at {ip_addr}: {e}")
            raise
    
    def __str__(self: AWG) -> str:
        """
        Returns a JSON string representation of the object with the following attributes:
        
        - manufacturer: The manufacturer of the device.
        - model: The model of the device.
        - serial_number: The serial number of the device.
        - fw_version: The firmware version of the device.
        
        The JSON string is formatted with an indentation of 2 spaces.
        
        Returns:
            str: A JSON string representation of the object.
        """
        return json.dumps(
            dict(
                manufacturer=self.manufacturer,
                model=self.model,
                serial_number=self.serial_number,
                fw_version=self.fw_version
            ),
            indent=2
        )
        
    def close(self: AWG) -> None:
        """
        Closes the connection to the AWG device.

        This method attempts to close the connection to the Arbitrary Waveform Generator (AWG) device.
        If the connection is successfully closed, a debug message is logged. If an error occurs during
        the process, an error message is logged with the exception details.

        Raises:
            Exception: If there is an issue closing the connection to the AWG device.
        """
        try:
            self.device.close()
            logging.debug("Disconnected from AWG")
        except Exception as e:
            logging.error(f"Failed to disconnect from AWG: {e}")

    def get_id(self: AWG) -> str:
        """
        Retrieves the identification string of the device.

        Returns:
            str: The identification string of the device.
        """
        return self.query("*IDN?")

    def query(self: AWG, command: str) -> str:
        """
        Sends a query command to the device and returns the response.

        Args:
            command (str): The command to be sent to the device.

        Returns:
            str: The response received from the device.

        Raises:
            Exception: If there is an error in sending the query or receiving the response.
        """
        try:
            response = self.device.ask(command)
            logging.debug(f"Sent query: {command}, Received: {response}")
            return response
        except Exception as e:
            logging.error(f"Failed to query command: {e}")
            raise

    def reset(self: AWG) -> None:
        """
        Sends a query command to the device and returns the response.

        Raises:
            Exception: If there is an error in sending the query or receiving the response.
        """
        try:
            response = self.device.write('*RST')
        except Exception as e:
            logging.error(f"Failed to query command: {e}")
            raise

    def write(self: AWG, command: str) -> None:
        """
        Sends a command to the device.

        Args:
            command (str): The command string to be sent to the device.

        Raises:
            Exception: If there is an error while writing the command to the device.
        """
        try:
            self.device.write(command)
            logging.debug(f"Sent command: {command}")
        except Exception as e:
            logging.error(f"Failed to write command: {e}")
            raise
