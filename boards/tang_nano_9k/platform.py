"""Tang Nano 9K Platform Definition"""

from litex.build.generic_platform import Pins, Subsignal, IOStandard
from litex.build.gowin.platform import GowinPlatform
from litex.build.openfpgaloader import OpenFPGALoader


# IO Definitions
_io = [
    # Clock
    ("clk27", 0, Pins("52"), IOStandard("LVCMOS33")),
    
    # LEDs
    ("user_led", 0, Pins("10"), IOStandard("LVCMOS18")),
    ("user_led", 1, Pins("11"), IOStandard("LVCMOS18")),
    ("user_led", 2, Pins("13"), IOStandard("LVCMOS18")),
    ("user_led", 3, Pins("14"), IOStandard("LVCMOS18")),
    ("user_led", 4, Pins("15"), IOStandard("LVCMOS18")),
    ("user_led", 5, Pins("16"), IOStandard("LVCMOS18")),
    
    # Buttons
    ("user_btn", 0, Pins("3"), IOStandard("LVCMOS18")),
    ("user_btn", 1, Pins("4"), IOStandard("LVCMOS18")),
    
    # UART (USB-Serial, connected to FT2232D)
    ("serial", 0,
        Subsignal("rx", Pins("18")),
        Subsignal("tx", Pins("17")),
        IOStandard("LVCMOS33")
    ),
    
    # Secondary UART (expansion header)
    ("uart0", 0,
        Subsignal("rx", Pins("41")),
        Subsignal("tx", Pins("42")),
        IOStandard("LVCMOS33")
    ),
    
    # I2C
    ("i2c0", 0,
        Subsignal("sda", Pins("40")),
        Subsignal("scl", Pins("35")),
        IOStandard("LVCMOS33"),
    ),
    
    # SPI for SD Card
    ("spisdcard", 0,
        Subsignal("clk", Pins("36")),
        Subsignal("mosi", Pins("37")),
        Subsignal("cs_n", Pins("38")),
        Subsignal("miso", Pins("39")),
        IOStandard("LVCMOS33"),
    ),
    
    # HyperRAM / PSRAM (2 chips)
    ("O_psram_ck", 0, Pins(2)),
    ("O_psram_ck_n", 0, Pins(2)),
    ("O_psram_cs_n", 0, Pins(2)),
    ("O_psram_reset_n", 0, Pins(2)),
    ("IO_psram_dq", 0, Pins(16)),
    ("IO_psram_rwds", 0, Pins(2)),
    
    # GPIO Expansion
    ("gpio", 0, Pins("25"), IOStandard("LVCMOS33")),
    ("gpio", 1, Pins("26"), IOStandard("LVCMOS33")),
    ("gpio", 2, Pins("27"), IOStandard("LVCMOS33")),
    ("gpio", 3, Pins("28"), IOStandard("LVCMOS33")),
    ("gpio", 4, Pins("29"), IOStandard("LVCMOS33")),
    ("gpio", 5, Pins("30"), IOStandard("LVCMOS33")),
    ("gpio", 6, Pins("33"), IOStandard("LVCMOS33")),
    ("gpio", 7, Pins("34"), IOStandard("LVCMOS33")),
    
    # PWM
    ("pwm0", 0, Pins("51"), IOStandard("LVCMOS33")),
    ("pwm1", 0, Pins("53"), IOStandard("LVCMOS33")),
]

_connectors = []


class TangNano9KPlatform(GowinPlatform):
    """Tang Nano 9K FPGA Platform"""
    
    default_clk_name = "clk27"
    default_clk_period = 1e9 / 27e6
    
    def __init__(self):
        GowinPlatform.__init__(
            self,
            "GW1NR-LV9QN88PC6/I5",
            _io,
            _connectors,
            toolchain="gowin",
            devicename="GW1NR-9C"
        )
        
        # Enable MSPI pins as GPIO
        self.toolchain.options["use_mspi_as_gpio"] = 1
    
    def create_programmer(self):
        """Create programmer using openFPGALoader"""
        return OpenFPGALoader(cable="ft2232")
    
    def do_finalize(self, fragment):
        """Add timing constraints"""
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(
            self.lookup_request("clk27", loose=True),
            1e9 / 27e6
        )
