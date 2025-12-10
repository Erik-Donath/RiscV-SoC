"""HyperRAM/HyperBus Controller"""

from .controller import HyperRAMController


def create_hyperram_controller(pads, latency=6):
    """
    Factory function to create HyperRAM controller
    
    Args:
        pads: HyperRAM physical pads
        latency: Latency cycles (default: 6)
    
    Returns:
        HyperRAMController instance
    """
    return HyperRAMController(pads, latency)


__all__ = ["HyperRAMController", "create_hyperram_controller"]
