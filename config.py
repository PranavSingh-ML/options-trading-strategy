from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class StrategyConfig:
    """Configuration parameters for the options trading strategy"""
    
    # Trading session timings
    entry_time: str = "15:25:00"       # Position entry time (3:25 PM)
    market_open: str = "09:15:00"      # Market open time for direction analysis
    
    # Exit management timing
    exit_time: str = "09:45:00"        # Maximum position hold time next day
    
    # Transaction cost modeling
    entry_slippage: float = 0.005      # Entry slippage (0.5%)
    exit_slippage: float = 0.005       # Exit slippage (0.5%)
    
    # Hedge position parameters
    hedge_distance_pct: float = 0.02   # Hedge strike distance from ATM (2%)
    
    # Trailing stop parameters
    trail_timeframe_minutes: int = 3   # Rolling window for 3-minute highs
    
    # Position sizing
    lot_size: int = 1                  # Number of lots per trade
    
    # Data source configuration
    opt_db_path: str = "Assignment/OPT.db"   # Options price database
    spot_db_path: str = "Assignment/SPOT.db" # Spot price database
    use_sample_data: bool = False            # Use sample data for testing
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration parameters to dictionary format for reporting"""
        return {
            'Entry Time': self.entry_time,
            'Market Open': self.market_open,
            'Exit Time': self.exit_time,
            'Entry Slippage': f"{self.entry_slippage*100}%",
            'Exit Slippage': f"{self.exit_slippage*100}%",
            'Hedge Distance': f"{self.hedge_distance_pct*100}%",
            'Trail Timeframe': f"{self.trail_timeframe_minutes} minutes",
            'Lot Size': self.lot_size
        }