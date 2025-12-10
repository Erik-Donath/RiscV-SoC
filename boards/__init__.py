"""Board Support Package"""

from typing import Dict, Type


class Board:
    """Base board interface"""
    name: str = "Unknown Board"
    
    def create_platform(self):
        """Create and return platform instance"""
        raise NotImplementedError
    
    def get_hyperram_pads(self, platform):
        """Get HyperRAM pad configuration"""
        raise NotImplementedError
    
    def add_peripherals(self, soc, platform, config):
        """Add board-specific peripherals to SoC"""
        raise NotImplementedError


_boards: Dict[str, Type[Board]] = {}


def register_board(name: str):
    """Decorator to register a board"""
    def decorator(cls):
        _boards[name] = cls
        return cls
    return decorator


def get_board(name: str) -> Board:
    """Get board instance by name"""
    if name not in _boards:
        raise ValueError(f"Unknown board: {name}")
    return _boards[name]()


# Import all boards to trigger registration
from .tang_nano_9k import TangNano9K
