"""Clock and Reset Generation"""

from migen import Signal, ClockDomain
from litex.gen import LiteXModule
from litex.soc.cores.clock.gowin_gw1n import GW1NPLL


class ClockDomainGenerator(LiteXModule):
    """
    Clock and Reset Generator
    
    Generates system clock from board's input clock using PLL.
    Supports different FPGA vendors through abstraction.
    """
    
    def __init__(self, platform, sys_clk_freq, input_clk_name="clk27", input_clk_freq=27e6):
        """
        Initialize Clock Domain Generator
        
        Args:
            platform: FPGA platform
            sys_clk_freq: Target system clock frequency in Hz
            input_clk_name: Name of input clock resource
            input_clk_freq: Input clock frequency in Hz
        """
        self.rst = Signal()
        self.cd_sys = ClockDomain()
        
        # Get platform resources
        clk_in = platform.request(input_clk_name)
        reset_btn = platform.request("user_btn", 0)
        
        # Detect platform type and create appropriate PLL
        if hasattr(platform, "devicename"):  # Gowin
            self._create_gowin_pll(platform, clk_in, reset_btn, input_clk_freq, sys_clk_freq)
        else:
            raise NotImplementedError(f"Platform {type(platform)} not supported")
    
    def _create_gowin_pll(self, platform, clk_in, reset_btn, input_freq, output_freq):
        """Create Gowin-specific PLL"""
        self.pll = GW1NPLL(
            devicename=platform.devicename,
            device=platform.device
        )
        
        # Reset is active-low on button
        self.comb += self.pll.reset.eq(~reset_btn)
        
        # Register input clock
        self.pll.register_clkin(clk_in, input_freq)
        
        # Create output clock
        self.pll.create_clkout(self.cd_sys, output_freq)
