from enum import Enum, auto


class FramingType(Enum):
    FULL = 0
    SUM = auto()
    RAW = auto()
    HISTOGRAM = auto()
    TEST = auto()
    SUM_SQ = auto()


class BsdaSettings:

    def __init__(self):
        self.framing = FramingType.SUM
        # s.bsda_settings[1].frame_duration_us = (f != FRAMING_T::HISTOGRAM ? 1000: 10000);
        self.frame_duration_us = 0
        self.temperature_period_ms = 0
        self.voltage_period_ms = 5000
        self.adc_shadow = [0x03ff, 0x03ff]
        self.raw_adc = 0
        self.raw_channel = 0
        self.log_uart = False
        self.log_level = 0
        self.disabled = False
        self.light_enabled = False
        self.temperature_enabled = False
        self.voltage_enabled = False

    def to_json(self):
        if self.temperature_period_ms > (2**16)-1:
            raise ValueError("Temperature period is greater than 2**16 - 1")

        d = {}
        d["framing"] = self.framing.value
        d["frame_duration_us"] = self.frame_duration_us
        d["temperature_period"] = self.temperature_period_ms
        d["voltage_period"] = self.voltage_period_ms
        d["adc_shadow"] = self.adc_shadow
        d["raw_adc"] = self.raw_adc
        d["raw_channel"] = self.raw_channel
        d["log_uart"] = self.log_uart
        d["log_level"] = self.log_level
        d["disabled"] = self.disabled
        d["light_enabled"] = self.light_enabled
        d["temperature_enabled"] = self.temperature_enabled
        d["voltage_enabled"] = self.voltage_enabled
        return d

    def from_json(self, j):
        self.framing = FramingType(j["framing"])
        self.frame_duration_us = j["frame_duration_us"]
        self.temperature_period_ms = j["temperature_period"]
        self.voltage_period_ms = j["voltage_period"]
        self.adc_shadow = j["adc_shadow"]
        self.raw_adc = j["raw_adc"]
        self.raw_channel = j["raw_channel"]
        self.log_uart = j["log_uart"]
        self.log_level = j["log_level"]
        self.disabled = j["disabled"]
        self.light_enabled = j["light_enabled"]
        self.temperature_enabled = j["temperature_enabled"]
        self.voltage_enabled = j["voltage_enabled"]

        return self

class EbiSettings:

    def __init__(self):
        #s.framereader_period = (f != FRAMING_T::HISTOGRAM ? 10: 100);
        self.voltage_reader_period_ms = 5000
        self.temperature_reader_period_ms = 0
        self.frame_reader_period_ms = 0
        self.frame_reader_framing_type = FramingType.SUM
        self.raw_board = 0
        self.bsda_settings = [BsdaSettings(), BsdaSettings(),BsdaSettings()]
        self.ntp_period_m = 0
        self.log_uart = False
        self.log_level = 0

    def to_json(self):
        d = {}
        d["voltage_reader_period"] = self.voltage_reader_period_ms
        d["temperature_reader_period"] = self.temperature_reader_period_ms
        d["period"] = self.frame_reader_period_ms
        d["type"] = self.frame_reader_framing_type.value
        d["bsda_settings"] = [s.to_json() for s in self.bsda_settings]
        d["raw_board"] = self.raw_board
        d["ntp_period_m"] = self.ntp_period_m
        d["log_level"] = self.log_level
        d["log_uart"] = self.log_uart
        return d

    def from_json(self, j):
        self.voltage_reader_period_ms = j["voltage_reader_period"]
        self.temperature_reader_period_ms = j["temperature_reader_period"]
        self.frame_reader_period_ms = j["period"]
        self.frame_reader_framing_type = FramingType(j["type"])
        self.bsda_settings = [BsdaSettings().from_json(e) for e in j["bsda_settings"]]
        self.raw_board = j["raw_board"]
        self.ntp_period_m = j["ntp_period_m"]
        self.log_level = j["log_level"]
        self.log_uart = j["log_uart"]

        return self