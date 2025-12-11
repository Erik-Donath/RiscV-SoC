"""Tang Nano 9K Peripheral Configuration"""

from litex.soc.cores.timer import Timer
from litex.soc.cores.gpio import GPIOOut, GPIOIn
from litex.soc.cores.bitbang import I2CMaster


def add_peripherals(soc, platform, config):
    """
    Add peripherals to SoC based on configuration.

    Args:
        soc:      SoC instance.
        platform: Platform instance.
        config:   SoC configuration object with feature flags, e.g.:
                  - with_timer
                  - with_i2c
                  - with_uart
                  - with_spi
                  - sys_clk_freq
    """

    # LEDs (always add)
    soc.leds = GPIOOut(
        pads=platform.request_all("user_led")
    )

    # Button with interrupt (always add)
    # Use button 1 (index 1) to avoid clash with reset buttons if any.
    soc.gpio_btn = GPIOIn(
        pads=platform.request("user_btn", 1),
        with_irq=True
    )
    soc.irq.add("gpio_btn", use_loc_if_exists=True)

    # Timers (optional: 3 independent timers)
    if getattr(config, "with_timer", False):
        soc.timer0 = Timer()
        soc.timer1 = Timer()
        soc.timer2 = Timer()
        soc.irq.add("timer0", use_loc_if_exists=True)
        soc.irq.add("timer1", use_loc_if_exists=True)
        soc.irq.add("timer2", use_loc_if_exists=True)

    # I2C Master on expansion header
    if getattr(config, "with_i2c", False):
        pads = platform.request("i2c0")
        soc.i2c0 = I2CMaster(pads=pads)

    # Secondary UART on expansion header
    # Exposed as "uart1" and internally wired to platform "uart0".
    if getattr(config, "with_uart", False):
        soc.add_uart(name="uart1", uart_name="uart0")

    # SPI master for SD-Card on J6
    if getattr(config, "with_spi", False):
        from litex.soc.cores.spi import SPIMaster
        soc.spi_sdcard = SPIMaster(
            pads=platform.request("spisdcard"),
            data_width=8,
            sys_clk_freq=config.sys_clk_freq,
            spi_clk_freq=10e6,
        )
