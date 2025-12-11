"""Tang Nano 9K Board Support"""

from migen import Signal

from boards import Board, register_board

from .platform import TangNano9KPlatform
from .peripherals import add_peripherals


@register_board("tang_nano_9k")
class TangNano9K(Board):
    """
    Sipeed Tang Nano 9K Board.

    Specifications:
        - FPGA:     Gowin GW1NR-9C
        - LUTs:     ~8640
        - BlockRAM: ~468 Kbits
        - PSRAM:    2x 32Mbit (HyperRAM)
        - USB-UART: FT2232D
    """

    name = "Tang Nano 9K"

    # Platform ----------------------------------------------------------------

    def create_platform(self):
        """Create platform instance."""
        return TangNano9KPlatform()

    # HyperRAM helper ---------------------------------------------------------

    def get_hyperram_pads(self, platform):
        """
        Get HyperRAM pads for the first chip.

        Note:
            Clock connections must be done by the caller (SoC),
            since the platform does not have a comb attribute.
        """
        dq      = platform.request("IO_psram_dq")
        rwds    = platform.request("IO_psram_rwds")
        reset_n = platform.request("O_psram_reset_n")
        cs_n    = platform.request("O_psram_cs_n")
        ck      = platform.request("O_psram_ck")
        ck_n    = platform.request("O_psram_ck_n")

        class HyperRAMPads:
            def __init__(self):
                # Clock comes from SoC; this is just a sink.
                self.clk  = Signal()
                self.rst_n = reset_n[0]
                self.dq    = dq[0:8]
                self.cs_n  = cs_n[0]
                self.rwds  = rwds[0]
                # Keep physical clock pins for external connection by caller.
                self._ck   = ck[0]
                self._ck_n = ck_n[0]

        return HyperRAMPads()

    # Board-specific peripherals ---------------------------------------------

    def add_peripherals(self, soc, platform, config):
        """Add Tang Nano 9K specific peripherals to the SoC."""
        add_peripherals(soc, platform, config)
