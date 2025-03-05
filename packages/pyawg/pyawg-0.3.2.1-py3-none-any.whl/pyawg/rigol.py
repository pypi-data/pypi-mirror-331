from __future__ import annotations

import logging

from .base import AWG
from .enums import AmplitudeUnit, BurstModeRigol, BurstTriggerSource, FrequencyUnit, OutputLoad, WaveformType
from .exceptions import *


class RigolDG1000Z(AWG):
    def __init__(self: RigolDG1000Z, ip_address):
        super().__init__(ip_address)
        logging.debug("RigolDG1000Z instance created.")

    def set_amplitude(self: RigolDG1000Z, channel: int, amplitude: float | int, unit: AmplitudeUnit = AmplitudeUnit.VPP) -> None:
        """Sets the amplitude for the specified channel."""

        if not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(amplitude) is not float and type(amplitude) is not int:
            raise TypeError(f"'amplitude' must be float or int; received {type(amplitude)}")
        elif not (-10 <= amplitude <= 10):
            raise ValueError(f"'amplitude' must be between -/+ 10")
        elif not isinstance(unit, AmplitudeUnit):
            raise TypeError(f"'unit' must be enum of type AmplitudeUnit. Hint: have you forgotten to import 'AmplitudeType' from 'pyawg'?")

        try:
            self.write(f"SOUR{channel}:VOLT {amplitude}{unit.value}")
            logging.debug(f"Channel {channel} amplitude set to {amplitude}{unit.value}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} amplitude to {amplitude}{unit.value}: {e}")
            raise

    def set_burst_delay(self: RigolDG1000Z, channel: int, delay: float | int) -> None:
        """Sets burst delay for the specified channel."""

        if not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(delay) is not float and type(delay) is not int:
            raise TypeError(f"'delay' must be float or int; received {type(delay)}")
        elif delay < 0:
            raise ValueError(f"'delay' cannot be negative")

        try:
            self.write(f"SOUR{channel}:BURS:TDEL {delay}")
            logging.debug(f"Channel {channel} burst delay has been set to {delay}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} burst delay to {delay}: {e}")

    def set_burst_mode(self: RigolDG1000Z, channel: int, burst_mode: BurstModeRigol) -> None:
        """Sets the mode of the burst for the specified channel"""

        if not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif not isinstance(burst_mode, BurstModeRigol):
            raise TypeError(f"'burst_mode' must be enum of type BurstModeRigol. Hint: have you forgotten to import 'BurstModeRigol' from 'pyawg'?")

        try:
            self.write(f"SOUR{channel}:BURS:MODE {burst_mode.value}")
            logging.debug(f"Channel {channel} burst mode has been set to {burst_mode.value}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} burst mode to {burst_mode.value}: {e}")

    def set_burst_period(self: RigolDG1000Z, channel: int, period: float | int) -> None:
        """Sets the period of the burst for the specified channel."""

        if not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(period) is not float and type(period) is not int:
            raise TypeError(f"'period' must be float or int; received {type(period)}")
        elif period < 0:
            raise ValueError(f"'period' cannot be negative")

        try:
            self.write(f"SOUR{channel}:BURS:INT:PER {period}")
            logging.debug(f"Channel {channel} burst period has been set to {period}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} burst period to {period}: {e}")

    def set_burst_state(self: RigolDG1000Z, channel: int, state: bool) -> None:
        """Sets the state of the burst for the specified channel."""

        if not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(state) is not bool:
            raise TypeError(f"'state' must be bool; received {type(state)}")

        state_str = "ON" if state else "OFF"
        try:
            self.write(f"SOUR{channel}:BURS {state_str}")
            logging.debug(f"Channel {channel} burst state has been set to {state_str}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} burst state to {state_str}: {e}")

    def set_burst_trigger_source(self: RigolDG1000Z, channel: int, trigger_source: BurstTriggerSource) -> None:
        """Sets the trigger source of the burst for the specified channel."""

        if not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif not isinstance(trigger_source, BurstTriggerSource):
            raise TypeError(f"'trigger_source' must be enum of type BurstTriggerSource. Hint: have you forgotten to import 'BurstTriggerSource' from 'pyawg'?")

        try:
            self.write(f"SOUR{channel}:BURS:TRIG:SOUR {trigger_source.value}")
            logging.debug(f"Channel {channel} burst trigger source has been set to {trigger_source.value}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} burst trigger source to {trigger_source.value}: {e}")

    def set_frequency(self: RigolDG1000Z, channel: int, frequency: float | int, unit: FrequencyUnit = FrequencyUnit.HZ) -> None:
        """Sets the frequency for the specified channel."""

        if not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(frequency) is not float and type(frequency) is not int:
            raise TypeError(f"'frequency' must be float or int; received {type(frequency)}")
        elif frequency < 0:
            raise ValueError(f"'frequency' cannot be negative")
        elif not isinstance(unit, FrequencyUnit):
            raise TypeError(f"'unit' must be enum of type FrequencyUnit. Hint: did you forget to import 'FrequencyUnit' from 'pyawg'?")

        try:
            self.write(f"SOUR{channel}:FREQ {frequency}{unit.value}")
            logging.debug(f"Channel {channel} frequency set to {frequency}{unit.value}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} frequency to {frequency}{unit.value}: {e}")
            raise

    def set_offset(self: RigolDG1000Z, channel: int, offset_voltage: float | int) -> None:
        """Sets the offset voltage for the specified channel."""

        if not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(offset_voltage) is not float and type(offset_voltage) is not int:
            raise TypeError(f"'offset_voltage' must be float or int; received {type(offset_voltage)}")

        try:
            self.write(f"SOUR{channel}:VOLT:OFFS {offset_voltage}")
            logging.debug(f"Channel {channel} offset voltage set to {offset_voltage} Vdc")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} offset voltage to {offset_voltage} Vdc: {e}")
            raise

    def set_output(self: RigolDG1000Z, channel: int, state: bool) -> None:
        """Sets the output on the specified channel ON or OFF"""

        if not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(state) is not bool:
            raise TypeError(f"'state' must be bool; received {type(state)}")


        state_str = "ON" if state else "OFF"
        try:
            self.write(f"OUTP{channel} {state_str}")
            logging.debug(f"Channel {channel} output has been set to {state_str}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} output to {state_str}: {e}")

    def set_output_load(self: RigolDG1000Z, channel: int, load: OutputLoad | int | float) -> None:
        """Sets the output load for the specified channel."""

        if not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(load) is not float and type(load) is not int and not isinstance(load, OutputLoad):
            raise TypeError(f"'load' must be float or int or enum of type OutputLoad; received {type(state)}. Hint: did you forget to import 'OutputLoad' from 'pyawg'?")

        if load == OutputLoad.HZ or load == OutputLoad.INF:
            load = 'INF'
        try:
            self.write(f"OUTP{channel}:LOAD {load}")
            logging.debug(f"Channel {channel} output load has been set to {load}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} output load to {load}: {e}")

    def set_phase(self: RigolDG1000Z, channel: int, phase: float | int) -> None:
        """Sets the phase for the specified channel."""

        if not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif type(phase) is not float and type(phase) is not int:
            raise TypeError(f"'phase' must be float or int; received {type(phase)}")
        elif not (0 <= abs(phase) <= 360):
            raise ValueError(f"'phase' must be between 0 and 360")

        try:
            self.write(f"SOUR{channel}:PHAS {phase}")
            logging.debug(f"Channel {channel} phase set to {phase}°")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} phase to {phase}°: {e}")
            raise

    def set_waveform(self: RigolDG1000Z, channel: int, waveform_type: WaveformType) -> None:
        """Sets the waveform type for the specified channel."""

        if not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)
        elif not isinstance(waveform_type, WaveformType):
            raise TypeError(f"'waveform_type' must be enum of type WaveformType. Hint: have you forgotten to import 'WaveformType' from 'pyawg'?")

        try:
            self.write(f"SOUR{channel}:FUNC {waveform_type.value}")
            logging.debug(f"Channel {channel} waveform set to {waveform_type.value}")
        except Exception as e:
            logging.error(f"Failed to set channel {channel} waveform to {waveform_type.value}: {e}")
            raise

    def sync_phase(self: RigolDG1000Z, channel: int = 1) -> None:
        """Sets the phase synchronization of the two channels."""

        if not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)

        try:
            self.write(f"SOUR{channel}:PHAS:SYNC")
            logging.debug(f"Phases of both the channels have been synchronized")
        except Exception as e:
            logging.error(f"Failed to synchronize phase: {e}")
            raise

    def trigger_burst(self: RigolDG1000Z, channel: int) -> None:
        """Triggers a burst from the specified channel."""

        if not (channel == 1 or channel == 2):
            raise InvalidChannelNumber(channel)

        try:
            self.write(f"SOUR{channel}:BURS:TRIG")
            logging.debug(f"Burst on channel {channel} has been successfully triggered")
        except Exception as e:
            logging.error(f"Failed to trigger the burst on channel {channel}: {e}")
