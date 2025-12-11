"""
HyperRAM Memory Controller

Portable implementation for HyperBus protocol.
"""

from migen import Module, Signal, If, Case, Cat, TSTriple
from migen.genlib.misc import timeline

from litex.soc.interconnect import wishbone

from .timing import HyperBusTiming


class HyperRAMController(Module):
    """
    HyperRAM Memory Controller.

    Features:
      - FPGA vendor agnostic.
      - Supports 8-bit and 16-bit data widths.
      - Configurable latency.
      - Wishbone interface.
    """

    def __init__(self, pads, latency=6):
        """
        Initialize HyperRAM controller.

        Args:
            pads: Physical pads (clk, cs_n, dq, rwds, optional rst_n).
            latency: Number of HyperRAM latency cycles.
        """
        self.pads = pads
        self.bus = wishbone.Interface()

        # Determine data width and add tristates if needed.
        dq   = self._ensure_tristate(pads, "dq")
        rwds = self._ensure_tristate(pads, "rwds")

        dw = len(dq.o)
        assert dw in [8, 16], f"Unsupported data width: {dw}"

        # Internal signals.
        clk       = Signal()
        clk_phase = Signal(2)
        cs        = Signal()
        ca        = Signal(48)
        ca_active = Signal()
        sr        = Signal(48)

        # Optional reset control: keep high by default.
        if hasattr(pads, "rst_n"):
            self.comb += pads.rst_n.eq(1)

        # Chip select and clock pins.
        self.comb += pads.cs_n.eq(~cs)
        if hasattr(pads, "clk"):
            self.comb += pads.clk.eq(clk)

        # Simple internal clocking derived from sys_clk phases.
        self.sync += clk_phase.eq(clk_phase + 1)
        self.sync += Case(clk_phase, {
            1: clk.eq(cs),
            3: clk.eq(0),
        })

        # Data path: shift register and IO mapping.
        dqi = Signal(dw)
        self.sync += dqi.eq(dq.i)

        self.sync += [
            If((clk_phase == 0) | (clk_phase == 2),
               If(ca_active,
                  # During CA phase: HyperRAM uses 8-bit shifts.
                  sr.eq(Cat(dqi[:8], sr[:-8]))
               ).Else(
                  # During data phase: shift full data width.
                  sr.eq(Cat(dqi, sr[:-dw]))
               )
            )
        ]

        # Read data mapping: expose shift register as Wishbone data.
        self.comb += self.bus.dat_r.eq(sr[:len(self.bus.dat_r)])

        # Output data mapping: drive DQ from tail of shift register.
        self.comb += [
            If(ca_active,
               dq.o.eq(sr[-8:])
            ).Else(
               dq.o.eq(sr[-dw:])
            )
        ]

        # Command-Address generation.
        # CA[47]    : R/W# (1 = read, 0 = write) – here ~we.
        # CA[45]    : Linear burst.
        # Address mapping depends on data width.
        self.comb += [
            ca[47].eq(~self.bus.we),
            ca[45].eq(1),
        ]

        if dw == 8:
            self.comb += [
                ca[16:45].eq(self.bus.adr[2:]),
                ca[1:3].eq(self.bus.adr[0:2]),
                ca[0].eq(0),
            ]
        else:
            self.comb += [
                ca[16:45].eq(self.bus.adr[3:]),
                ca[1:3].eq(self.bus.adr[1:3]),
                ca[0].eq(self.bus.adr[0]),
            ]

        # Timing sequence
        timing  = HyperBusTiming(latency=latency, data_width=dw)
        dt_seq  = timing.build_sequence(cs, ca, ca_active, dq, rwds, sr, self.bus)

        # RWDS output is driven in the timing sequence; ensure o is connected.
        # The timing helper sets rwds.o in its actions.

        # Convert delta-time sequence to absolute-time sequence for timeline.
        t_seq = []
        t = 0
        for dt, actions in dt_seq:
            t_seq.append((t, actions))
            t += dt

        # Launch timeline when a new Wishbone cycle starts at phase 1.
        self.sync += timeline(self.bus.cyc & self.bus.stb & (clk_phase == 1), t_seq)

    # --------------------------------------------------------------------- #
    # Helpers
    # --------------------------------------------------------------------- #

    def _add_tristate(self, pad):
        """Create TSTriple for given pad and return it."""
        t = TSTriple(len(pad))
        self.specials += t.get_tristate(pad)
        return t

    def _ensure_tristate(self, pads, name):
        """
        Ensure pads.<name> is a TSTriple-like object (has .i/.o/.oe)
        and return it.
        """
        pad = getattr(pads, name)
        if hasattr(pad, "oe"):
            # Already a tristate/record with oe/o/i.
            return pad
        t = TSTriple(len(pad))
        self.specials += t.get_tristate(pad)
        return t
