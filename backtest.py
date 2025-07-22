#!/usr/bin/env python3
"""
Main backtesting engine for options strategy
"""
from typing import List
import os
from config import StrategyConfig
from data_utils import DataManager
from strategy import OptionsStrategy, Trade
from excel_output import ExcelGenerator

class Backtester:
    """Main backtesting engine that orchestrates strategy execution across historical data"""
    
    def __init__(self, config: StrategyConfig):
        """Initialize backtester with configuration and required components"""
        self.config = config
        self.data_manager = DataManager(config.opt_db_path, config.spot_db_path, config.use_sample_data)
        self.strategy = OptionsStrategy(config, self.data_manager)
        self.excel_generator = ExcelGenerator(config)
        
    def run_backtest(self) -> List[Trade]:
        """Execute strategy across all available trading dates and collect results"""
        print("Starting backtest...")
        
        # Load all available trading dates from database
        available_dates = self.data_manager.get_available_dates()
        print(f"📅 Found {len(available_dates)} trading dates")
        
        trades = []
        successful_trades = 0
        
        # Process each trading date sequentially
        for i, date in enumerate(available_dates):
            print(f"📊 Processing {date} ({i+1}/{len(available_dates)})")
            
            try:
                # Execute strategy for current date
                trade = self.strategy.execute_trade(date)
                if trade:
                    trades.append(trade)
                    successful_trades += 1
                    print(f"  ✅ {trade.instrument_type} trade: P&L ₹{trade.total_pnl:.2f}")
                else:
                    print(f"  ❌ No valid trade setup found")
                    
            except Exception as e:
                print(f"  ⚠️ Error processing {date}: {e}")
        
        print(f"\n✅ Backtest completed!")
        print(f"📈 Successful trades: {successful_trades}/{len(available_dates)} ({successful_trades/len(available_dates)*100:.1f}%)")
        
        # Display summary statistics
        if trades:
            total_pnl = sum(trade.total_pnl for trade in trades)
            win_rate = sum(1 for trade in trades if trade.total_pnl > 0) / len(trades) * 100
            print(f"💰 Total P&L: ₹{total_pnl:.2f}")
            print(f"📊 Average P&L per trade: ₹{total_pnl/len(trades):.2f}")
            print(f"🎯 Win rate: {win_rate:.1f}%")
        
        return trades
    
    def generate_report(self, trades: List[Trade], filename: str = None) -> None:
        """Generate comprehensive Excel reports with strategy results and analysis"""
        if filename is None:
            filename = f"strategy_backtest_{'sample' if self.config.use_sample_data else 'full'}.xlsx"
        
        self.excel_generator.generate_excel_report(trades, filename)
        print(f"📋 Report saved as: {filename}")

def main():
    """Main execution function for running complete backtesting workflow"""
    print("📈 Options Trading Strategy Backtest")
    print("=" * 50)
    
    # Initialize strategy configuration
    config = StrategyConfig()
    
    print(f"⚙️ Configuration:")
    print(f"  Entry time: {config.entry_time}")
    print(f"  Exit time: {config.exit_time}")
    print(f"  Slippage: {config.entry_slippage*100}%")
    print(f"  Hedge distance: {config.hedge_distance_pct*100}%")
    print(f"  Using sample data: {config.use_sample_data}")
    print()
    
    # Execute full strategy backtest
    backtester = Backtester(config)
    trades = backtester.run_backtest()
    
    # Generate comprehensive reports
    if trades:
        backtester.generate_report(trades)
        print(f"\n🎉 Backtesting workflow completed successfully!")
    else:
        print("\n⚠️ No trades generated, skipping report generation")

if __name__ == "__main__":
    main()
