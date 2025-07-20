import pandas as pd
from datetime import datetime, time
from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass
from data_utils import DataManager
from config import StrategyConfig

@dataclass
class Trade:
    date: str
    exit_date: str
    entry_time: str
    exit_time: str
    strike: int
    hedge_strike: int
    instrument_type: str
    entry_price: float
    exit_price: float
    hedge_entry_price: float
    hedge_exit_price: float
    main_pnl: float
    hedge_pnl: float
    total_pnl: float
    main_pnl_pct: float
    hedge_pnl_pct: float
    total_pnl_pct: float
    entry_reason: str
    exit_reason: str

class OptionsStrategy:
    def __init__(self, config: StrategyConfig, data_manager: DataManager):
        self.config = config
        self.data_manager = data_manager
        
    def analyze_market_movement(self, spot_df: pd.DataFrame) -> Tuple[float, float, str]:
        """Analyze spot movement from market open to entry time to determine trade direction"""
        # Extract market open price (9:15 AM) and entry time price (3:25 PM)
        open_data = spot_df[spot_df['time'] >= self.config.market_open].iloc[0]
        entry_data = spot_df[spot_df['time'] <= self.config.entry_time].iloc[-1]
        
        open_price = open_data['close']
        entry_price = entry_data['close']
        
        # Calculate percentage movement and determine direction
        movement_pct = (entry_price - open_price) / open_price
        direction = "UP" if movement_pct > 0 else "DOWN"
        
        return open_price, entry_price, direction
    
    def get_atm_and_hedge_strikes(self, spot_price: float, available_strikes: List[int], direction: str) -> Tuple[int, int]:
        """Select ATM strike for main position and OTM strike for hedge position"""
        atm_strike = self.data_manager.get_atm_strike(spot_price, available_strikes)
        
        # Determine instrument type: UP market -> Sell PE, DOWN market -> Sell CE
        instrument_type = "PE" if direction == "UP" else "CE"
        
        # Calculate hedge strike 2% away from ATM strike
        if instrument_type == "PE":
            # For PE options: OTM hedge is at lower strike price
            target_hedge = int(atm_strike * (1 - self.config.hedge_distance_pct))
            hedge_candidates = [s for s in available_strikes if s < atm_strike]
        else:
            # For CE options: OTM hedge is at higher strike price
            target_hedge = int(atm_strike * (1 + self.config.hedge_distance_pct))
            hedge_candidates = [s for s in available_strikes if s > atm_strike]
        
        # Select closest available strike to target hedge, or use ATM if none available
        if not hedge_candidates:
            hedge_strike = atm_strike
        else:
            hedge_strike = min(hedge_candidates, key=lambda x: abs(x - target_hedge))
        
        return atm_strike, hedge_strike
    
    def get_option_price_with_slippage(self, price: float, is_entry: bool, is_sell: bool = True) -> float:
        """Apply realistic slippage costs to option prices for entry and exit transactions"""
        slippage = self.config.entry_slippage if is_entry else self.config.exit_slippage
        
        if is_sell:
            return price * (1 - slippage)  # Selling: receive lower price due to slippage
        else:
            return price * (1 + slippage)  # Buying: pay higher price due to slippage
    
    def calculate_trailing_exits(self, option_df: pd.DataFrame, entry_price: float, is_short_position: bool = True) -> Tuple[Optional[str], Optional[float], str]:
        """Calculate trailing stop exits using 3-minute rolling highs for both main and hedge positions"""
        if len(option_df) == 0:
            return None, None, "No Data"
        
        option_df = option_df.copy()
        
        # Calculate 3-minute rolling maximum of high prices as trailing stop
        option_df['3min_trail'] = option_df['high'].rolling(window=3, min_periods=1).max()
        
        # Check each minute for trailing stop hit
        for idx, row in option_df.iterrows():
            trailing_stop = row['3min_trail']
            if row['close'] >= trailing_stop:
                return row['time'], row['close'], "Trail Stop Hit"
        
        # Exit at 9:45 AM if no trailing stop was hit during the session
        last_row = option_df.iloc[-1]
        return last_row['time'], last_row['close'], "Time Exit"
    
    def calculate_simultaneous_exits(self, main_df: pd.DataFrame, hedge_df: pd.DataFrame, 
                                   main_entry_price: float, hedge_entry_price: float) -> Tuple[Optional[str], Optional[float], Optional[float], str]:
        """Manage spread position exits: when either leg hits trailing stop, close both legs simultaneously"""
        if len(main_df) == 0 or len(hedge_df) == 0:
            return None, None, None, "No Data"
        
        # Prepare trailing stop calculations for both legs
        main_df = main_df.copy()
        hedge_df = hedge_df.copy()
        
        main_df['3min_trail'] = main_df['high'].rolling(window=3, min_periods=1).max()
        hedge_df['3min_trail'] = hedge_df['high'].rolling(window=3, min_periods=1).max()
        
        # Process all available timestamps chronologically
        all_times = sorted(set(main_df['time'].tolist() + hedge_df['time'].tolist()))
        
        # Monitor both legs each minute for trailing stop hits
        for current_time in all_times:
            main_current = main_df[main_df['time'] == current_time]
            hedge_current = hedge_df[hedge_df['time'] == current_time]
            
            # Require data for both legs to proceed
            if len(main_current) == 0 or len(hedge_current) == 0:
                continue
                
            main_row = main_current.iloc[0]
            hedge_row = hedge_current.iloc[0]
            
            # Check trailing stop conditions for both legs
            main_stop_hit = main_row['close'] >= main_row['3min_trail']
            hedge_stop_hit = hedge_row['close'] >= hedge_row['3min_trail']
            
            # Exit entire spread position when either leg hits its stop
            if main_stop_hit or hedge_stop_hit:
                reason = "Main Trail Stop" if main_stop_hit else "Hedge Trail Stop"
                return current_time, main_row['close'], hedge_row['close'], reason
        
        # Force exit at 9:45 AM if no trailing stops were triggered
        main_last = main_df.iloc[-1]
        hedge_last = hedge_df.iloc[-1]
        final_time = max(main_last['time'], hedge_last['time'])
        
        return final_time, main_last['close'], hedge_last['close'], "Time Exit"
    
    def execute_trade(self, date: str) -> Optional[Trade]:
        """Execute complete options spread trade: analyze market, enter positions, and manage exits"""
        try:
            # Load spot market data for trade entry analysis
            spot_df = self.data_manager.get_spot_data(date)
            if len(spot_df) == 0:
                return None
            
            # Determine market direction based on intraday movement
            open_price, entry_spot, direction = self.analyze_market_movement(spot_df)
            
            # Load available option contracts and strikes for the trading day
            option_sample = self.data_manager.get_option_data(date)
            if len(option_sample) == 0:
                return None
                
            expiry = option_sample['expiry'].iloc[0]
            available_strikes = self.data_manager.get_strikes_by_expiry(date, expiry)
            
            # Select instrument type and strikes based on market direction
            instrument_type = "PE" if direction == "UP" else "CE"
            atm_strike, hedge_strike = self.get_atm_and_hedge_strikes(entry_spot, available_strikes, direction)
            
            # Load option price data for main and hedge positions
            main_option_df = self.data_manager.get_option_data(date, atm_strike, instrument_type)
            hedge_option_df = self.data_manager.get_option_data(date, hedge_strike, instrument_type)
            
            if len(main_option_df) == 0 or len(hedge_option_df) == 0:
                return None
            
            # Get entry prices at 3:25 PM
            entry_row = main_option_df[main_option_df['time'] <= self.config.entry_time]
            hedge_entry_row = hedge_option_df[hedge_option_df['time'] <= self.config.entry_time]
            
            if len(entry_row) == 0 or len(hedge_entry_row) == 0:
                return None
                
            entry_row = entry_row.iloc[-1:] 
            hedge_entry_row = hedge_entry_row.iloc[-1:]
            
            entry_time = entry_row['time'].iloc[0]
            # Apply slippage: sell main position (short), buy hedge position (long)
            entry_price = self.get_option_price_with_slippage(entry_row['close'].iloc[0], True, True)
            hedge_entry_price = self.get_option_price_with_slippage(hedge_entry_row['close'].iloc[0], True, False)
            
            # Move to next trading day for position management
            next_date = self.data_manager.get_next_trading_day(date)
            if next_date is None:
                return None
            
            # Load next day option data for exit management
            next_main_df = self.data_manager.get_option_data(next_date, atm_strike, instrument_type)
            next_hedge_df = self.data_manager.get_option_data(next_date, hedge_strike, instrument_type)
            
            if len(next_main_df) == 0 or len(next_hedge_df) == 0:
                return None
            
            # Limit data to trading window (9:15 AM to 9:45 AM)
            next_main_df = next_main_df[next_main_df['time'] <= self.config.exit_time]
            next_hedge_df = next_hedge_df[next_hedge_df['time'] <= self.config.exit_time]
            
            if len(next_main_df) == 0 or len(next_hedge_df) == 0:
                return None
            
            # Execute spread exit strategy with simultaneous leg management
            exit_time, main_exit_price_raw, hedge_exit_price_raw, exit_reason = self.calculate_simultaneous_exits(
                next_main_df, next_hedge_df, entry_price, hedge_entry_price
            )
            
            if main_exit_price_raw is None or hedge_exit_price_raw is None:
                return None
            
            # Apply exit slippage: buy back short position, sell long hedge position
            main_exit_price = self.get_option_price_with_slippage(main_exit_price_raw, False, False)
            hedge_exit_price = self.get_option_price_with_slippage(hedge_exit_price_raw, False, True)
            
            # Calculate profit/loss for each leg of the spread
            main_pnl = (entry_price - main_exit_price) * self.config.lot_size  # Short position P&L
            hedge_pnl = (hedge_exit_price - hedge_entry_price) * self.config.lot_size  # Long position P&L
            total_pnl = main_pnl + hedge_pnl
            
            # Calculate percentage returns relative to capital deployed
            main_pnl_pct = (main_pnl / entry_price) * 100 if entry_price > 0 else 0
            hedge_pnl_pct = (hedge_pnl / hedge_entry_price) * 100 if hedge_entry_price > 0 else 0
            
            # Total return as percentage of combined capital
            total_capital = entry_price + hedge_entry_price
            total_pnl_pct = (total_pnl / total_capital) * 100 if total_capital > 0 else 0
            
            return Trade(
                date=date,
                exit_date=next_date,
                entry_time=entry_time,
                exit_time=exit_time,
                strike=atm_strike,
                hedge_strike=hedge_strike,
                instrument_type=instrument_type,
                entry_price=entry_price,
                exit_price=main_exit_price,
                hedge_entry_price=hedge_entry_price,
                hedge_exit_price=hedge_exit_price,
                main_pnl=main_pnl,
                hedge_pnl=hedge_pnl,
                total_pnl=total_pnl,
                main_pnl_pct=main_pnl_pct,
                hedge_pnl_pct=hedge_pnl_pct,
                total_pnl_pct=total_pnl_pct,
                entry_reason=f"Market {direction}, Sell {instrument_type}",
                exit_reason=exit_reason
            )
            
        except Exception as e:
            print(f"Error processing {date}: {e}")
            return None