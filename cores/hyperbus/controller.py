"""
HyperRAM Memory Controller
Portable implementation for HyperBus protocol
"""

from migen import Module, Signal, If, Case, Cat, TSTriple
from migen.genlib.misc import timeline
from litex.build.io import DifferentialOutput
from litex.soc.interconnect import wishbone


class HyperRAMController(Module):
    """
    HyperRAM Memory Controller
    
    Features:
    - FPGA vendor agnostic
    - Supports 8-bit and 16-bit data widths
    - Configurable latency
    - Wishbone interface
    """
    
    def __init__(self, pads, latency=6):
        """
        Initialize HyperRAM controller
        
        Args:
            pads: Physical pads (clk, cs_n, dq, rwds, rst_n)
            latency: Number of latency cycles
        """
        self.pads = pads
        self.bus = wishbone.Interface()
        
        # Determine data width
        dq = self._add_tristate(pads.dq) if not hasattr(pads.dq, "oe") else pads.dq
        rwds = self._add_tristate(pads.rwds) if not hasattr(pads.rwds, "oe") else pads.rwds
        dw = len(pads.dq) if not hasattr(pads.dq, "oe") else len(pads.dq.o)
        
        assert dw in [8, 16], f"Unsupported data width: {dw}"
        
        # Internal signals
        clk = Signal()
        clk_phase = Signal(2)
        cs = Signal()
        ca = Signal(48)
        ca_active = Signal()
        sr = Signal(48)
        
        # Setup control
        if hasattr(pads, "rst_n"):
            self.comb += pads.rst_n.eq(1)
        self.comb += pads.cs_n.eq(~cs)
        if hasattr(pads, "clk"):
            self.comb += pads.clk.eq(clk)
        
        # Clock generation
        self.sync += clk_phase.eq(clk_phase + 1)
        self.sync += Case(clk_phase, {
            1: clk.eq(cs),
            3: clk.eq(0),
        })
        
        # Data path
        dqi = Signal(dw)
        self.sync += dqi.eq(dq.i)
        self.sync += [
            If((clk_phase == 0) | (clk_phase == 2),
                If(ca_active,
                    sr.eq(Cat(dqi[:8], sr[:-8]))
                ).Else(
                    sr.eq(Cat(dqi, sr[:-dw]))
                )
            )
        ]
        
        self.comb += [
            self.bus.dat_r.eq(sr),
            If(ca_active,
                dq.o.eq(sr[-8:])
            ).Else(
                dq.o.eq(sr[-dw:])
            )
        ]
        
        # Command-Address
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
        lat = (latency * 8) - 4
        rwdso = Signal(2)
        self.comb += rwds.o.eq(rwdso)
        
        dt_seq = [
            (3, []),
            (12, [cs.eq(1), dq.oe.eq(1), sr.eq(ca), ca_active.eq(1)]),
            (lat, [dq.oe.eq(0), ca_active.eq(0)]),
        ]
        
        if dw == 8:
            dt_seq += [
                (2, [dq.oe.eq(self.bus.we), sr[:16].eq(0), sr[16:].eq(self.bus.dat_w),
                     rwds.oe.eq(self.bus.we), rwdso[0].eq(~self.bus.sel[3])]),
                (2, [rwdso[0].eq(~self.bus.sel[2])]),
                (2, [rwdso[0].eq(~self.bus.sel[1])]),
                (2, [rwdso[0].eq(~self.bus.sel[0])]),
            ]
        else:
            dt_seq += [
                (2, [dq.oe.eq(self.bus.we), sr[:16].eq(0), sr[16:].eq(self.bus.dat_w),
                     rwds.oe.eq(self.bus.we), rwdso[1].eq(~self.bus.sel[3]), rwdso[0].eq(~self.bus.sel[2])]),
                (2, [rwdso[1].eq(~self.bus.sel[1]), rwdso[0].eq(~self.bus.sel[0])]),
            ]
        
        dt_seq += [
            (2, [cs.eq(0), rwds.oe.eq(0), dq.oe.eq(0)]),
            (1, [self.bus.ack.eq(1)]),
            (1, [self.bus.ack.eq(0)]),
            (0, [])
        ]
        
        t_seq = []
        t = 0
        for dt, a in dt_seq:
            t_seq.append((t, a))
            t += dt
        
        self.sync += timeline(self.bus.cyc & self.bus.stb & (clk_phase == 1), t_seq)
    
    def _add_tristate(self, pad):
        """Create tristate for pad"""
        t = TSTriple(len(pad))
        self.specials += t.get_tristate(pad)
        return t
