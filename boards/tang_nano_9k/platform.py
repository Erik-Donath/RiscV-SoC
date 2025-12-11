"""Tang Nano 9K Platform Definition"""

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.gowin.platform import GowinPlatform
from litex.build.gowin.programmer import GowinProgrammer
from litex.build.openfpgaloader import OpenFPGALoader

# IO Definitions

_io = [
    # Clock / Reset
    ("clk27", 0, Pins("52"), IOStandard("LVCMOS33")),

    # LEDs (1.8V bank)
    ("user_led", 0, Pins("10"), IOStandard("LVCMOS18")),
    ("user_led", 1, Pins("11"), IOStandard("LVCMOS18")),
    ("user_led", 2, Pins("13"), IOStandard("LVCMOS18")),
    ("user_led", 3, Pins("14"), IOStandard("LVCMOS18")),
    ("user_led", 4, Pins("15"), IOStandard("LVCMOS18")),
    ("user_led", 5, Pins("16"), IOStandard("LVCMOS18")),

    # Buttons (1.8V bank)
    ("user_btn", 0, Pins("3"), IOStandard("LVCMOS18")),
    ("user_btn", 1, Pins("4"), IOStandard("LVCMOS18")),

    # USB-UART (FT2232D, on-board)
    ("serial", 0,
        Subsignal("rx", Pins("18")),
        Subsignal("tx", Pins("17")),
        IOStandard("LVCMOS33")
    ),

    # Secondary UART on expansion header
    ("uart0", 0,
        Subsignal("rx", Pins("41")),
        Subsignal("tx", Pins("42")),
        IOStandard("LVCMOS33")
    ),

    # I2C on expansion header
    ("i2c0", 0,
        Subsignal("sda", Pins("40")),
        Subsignal("scl", Pins("35")),
        IOStandard("LVCMOS33"),
    ),

    # SPI Flash (on-board)
    ("spiflash", 0,
        Subsignal("cs_n", Pins("60"), IOStandard("LVCMOS33")),
        Subsignal("clk",  Pins("59"), IOStandard("LVCMOS33")),
        Subsignal("miso", Pins("62"), IOStandard("LVCMOS33")),
        Subsignal("mosi", Pins("61"), IOStandard("LVCMOS33")),
    ),

    # SPI for SD-Card (J6)
    ("spisdcard", 0,
        Subsignal("clk",  Pins("36")),
        Subsignal("mosi", Pins("37")),
        Subsignal("cs_n", Pins("38")),
        Subsignal("miso", Pins("39")),
        IOStandard("LVCMOS33"),
    ),

    # PSRAM / HyperRAM (2 chips share bus)
    ("O_psram_ck",      0, Pins(2)),
    ("O_psram_ck_n",    0, Pins(2)),
    ("O_psram_cs_n",    0, Pins(2)),
    ("O_psram_reset_n", 0, Pins(2)),
    ("IO_psram_dq",     0, Pins(16)),
    ("IO_psram_rwds",   0, Pins(2)),

    # HDMI (TMDSTx pairs)
    ("hdmi", 0,
        Subsignal("clk_p",   Pins("69")),
        Subsignal("clk_n",   Pins("68")),
        Subsignal("data0_p", Pins("71")),
        Subsignal("data0_n", Pins("70")),
        Subsignal("data1_p", Pins("73")),
        Subsignal("data1_n", Pins("72")),
        Subsignal("data2_p", Pins("75")),
        Subsignal("data2_n", Pins("74")),
        Misc("PULL_MODE=NONE"),
    ),

    # SPI RGB LCD
    ("spilcd", 0,
        Subsignal("reset", Pins("47")),
        Subsignal("cs",    Pins("48")),
        Subsignal("clk",   Pins("79")),
        Subsignal("mosi",  Pins("77")),
        Subsignal("rs",    Pins("47")),
        IOStandard("LVCMOS33"),
    ),

    # GPIO expansion (J6 / J7)
    ("gpio", 0, Pins("25 26 27 28 29 30 33 34"), IOStandard("LVCMOS33")),

    # PWM (J6)
    ("pwm0", 0, Pins("51"), IOStandard("LVCMOS33")),
    ("pwm1", 0, Pins("53"), IOStandard("LVCMOS33")),
]

# Connectors ---------------------------------------------------------------------------------------

_connectors = [
    # J6 (SD + GPIO + PSRAM/others)
    ("J6", "38 37 36 39 25 26 27 28 29 30 33 34 40 35 41 42 51 53 54 55 56 57 68 69"),
    # J7 (HDMI/LCD/generic)
    ("J7", "63 86 85 84 83 82 81 80 79 77 76 75 74 73 72 71 70 - 48 49 31 32 - -"),
]

# Platform -----------------------------------------------------------------------------------------

class TangNano9KPlatform(GowinPlatform):
    """Sipeed Tang Nano 9K FPGA Platform."""

    default_clk_name   = "clk27"
    default_clk_period = 1e9 / 27e6

    def __init__(self, toolchain="gowin"):
        GowinPlatform.__init__(
            self,
            "GW1NR-LV9QN88PC6/I5",
            _io,
            _connectors,
            toolchain=toolchain,
            devicename="GW1NR-9C"
        )
        # Enable MSPI pins as GPIO (needed for Tang Nano 9K board)
        self.toolchain.options["use_mspi_as_gpio"] = 1

    def create_programmer(self, kit="openfpgaloader"):
        """Return a programmer for this board."""
        if kit == "gowin":
            return GowinProgrammer(self.devicename)
        else:
            # Default: openFPGALoader with FT2232 cable
            return OpenFPGALoader(cable="ft2232")

    def do_finalize(self, fragment):
        """Add timing constraints."""
        GowinPlatform.do_finalize(self, fragment)
        self.add_period_constraint(
            self.lookup_request("clk27", loose=True),
            1e9 / 27e6
        )
