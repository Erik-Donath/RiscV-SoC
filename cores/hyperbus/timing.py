"""HyperBus Timing Sequence Generator"""

from migen import Signal


class HyperBusTiming:
    """
    HyperBus Timing Sequence Generator
    
    Generates the delta-time sequence for HyperRAM access:
    1. Command-Address phase (6 clocks)
    2. Latency phase (configurable)
    3. Data phase (read/write)
    4. End and acknowledge
    """
    
    def __init__(self, latency, data_width):
        """
        Initialize timing generator
        
        Args:
            latency: Number of latency cycles
            data_width: Data width (8 or 16)
        """
        self.latency = latency
        self.data_width = data_width
        
        # Calculate latency in sys_clk cycles
        # Latency starts from middle of CA phase (-4)
        # Fixed latency mode: 2 * latency cycles
        # 4 sys_clks per RAM clock
        self.latency_cycles = (latency * 8) - 4
    
    def build_sequence(self, cs, ca, ca_active, dq, rwds, sr, bus):
        """
        Build complete access sequence
        
        Returns:
            List of (delta_time, actions) tuples
        """
        rwds_out = Signal(2)
        # Fix: rwds is a module, not a signal - need to use comb from parent
        # This will be handled by the parent module
        
        sequence = [
            # Initial delay
            (3, []),
            
            # Command-Address phase
            (12, [
                cs.eq(1),
                dq.oe.eq(1),
                sr.eq(ca),
                ca_active.eq(1)
            ]),
            
            # Latency
            (self.latency_cycles, [
                dq.oe.eq(0),
                ca_active.eq(0)
            ]),
        ]
        
        # Data phase
        if self.data_width == 8:
            sequence.extend(self._data_phase_8bit(dq, rwds, rwds_out, sr, bus))
        else:
            sequence.extend(self._data_phase_16bit(dq, rwds, rwds_out, sr, bus))
        
        # End sequence
        sequence.extend([
            (2, [cs.eq(0), rwds.oe.eq(0), dq.oe.eq(0)]),
            (1, [bus.ack.eq(1)]),
            (1, [bus.ack.eq(0)]),
            (0, [])
        ])
        
        return sequence
    
    def _data_phase_8bit(self, dq, rwds, rwds_out, sr, bus):
        """Data phase for 8-bit mode"""
        return [
            (2, [
                dq.oe.eq(bus.we),
                sr[:16].eq(0),
                sr[16:].eq(bus.dat_w),
                rwds.oe.eq(bus.we),
                rwds.o.eq(rwds_out),
                rwds_out.eq((~bus.sel[3]).replicate(2))
            ]),
            (2, [rwds_out.eq((~bus.sel[2]).replicate(2))]),
            (2, [rwds_out.eq((~bus.sel[1]).replicate(2))]),
            (2, [rwds_out.eq((~bus.sel[0]).replicate(2))]),
        ]
    
    def _data_phase_16bit(self, dq, rwds, rwds_out, sr, bus):
        """Data phase for 16-bit mode"""
        return [
            (2, [
                dq.oe.eq(bus.we),
                sr[:16].eq(0),
                sr[16:].eq(bus.dat_w),
                rwds.oe.eq(bus.we),
                rwds.o.eq(rwds_out),
                rwds_out[1].eq(~bus.sel[3]),
                rwds_out[0].eq(~bus.sel[2])
            ]),
            (2, [
                rwds_out[1].eq(~bus.sel[1]),
                rwds_out[0].eq(~bus.sel[0])
            ]),
        ]
