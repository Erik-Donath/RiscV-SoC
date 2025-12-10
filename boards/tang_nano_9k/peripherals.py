"""Tang Nano 9K Peripheral Configuration"""

from litex.soc.cores.timer import Timer
from litex.soc.cores.gpio import GPIOOut, GPIOIn
from litex.soc.cores.bitbang import I2CMaster


def add_peripherals(soc, platform, config):
    """
    Add peripherals to SoC based on configuration
    
    Args:
        soc: SoC instance
        platform: Platform instance
        config: SoC configuration
    """
    
    # LEDs (always add)
    soc.leds = GPIOOut(
        pads=platform.request_all("user_led")
    )
    
    # Button with interrupt (always add)
    soc.gpio_btn = GPIOIn(
        pads=platform.request("user_btn", 1),
        with_irq=True
    )
    soc.irq.add("gpio_btn", use_loc_if_exists=True)
    
    # Timers
    if config.with_timer:
        soc.timer0 = Timer()
        soc.timer1 = Timer()
        soc.timer2 = Timer()
        soc.irq.add("timer0", use_loc_if_exists=True)
        soc.irq.add("timer1", use_loc_if_exists=True)
        soc.irq.add("timer2", use_loc_if_exists=True)
    
    # I2C Master
    if config.with_i2c:
        soc.i2c0 = I2CMaster(pads=platform.request("i2c0"))
    
    # Secondary UART
    if config.with_uart:
        soc.add_uart(name="uart1", uart_name="uart0")
    
    # SPI (optional)
    if config.with_spi:
        from litex.soc.cores.spi import SPIMaster
        soc.spi_sdcard = SPIMaster(
            pads=platform.request("spisdcard"),
            data_width=8,
            sys_clk_freq=config.sys_clk_freq,
            spi_clk_freq=10e6
        )
