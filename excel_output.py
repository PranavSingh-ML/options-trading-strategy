import pandas as pd
from typing import List, Dict
from strategy import Trade
from config import StrategyConfig

class ExcelGenerator:
    """Generates comprehensive Excel reports from trading strategy results"""
    
    def __init__(self, config: StrategyConfig):
        """Initialize with strategy configuration for parameter reporting"""
        self.config = config
    
    def generate_excel_report(self, trades: List[Trade], filename: str = 'strategy_results.xlsx') -> None:
        """Create multi-sheet Excel workbook with strategy parameters, P&L summary, and trade details"""
        
        # Sheet 1: Input Parameters
        params_df = pd.DataFrame(list(self.config.to_dict().items()), columns=['Parameter', 'Value'])
        
        # Sheet 2: P&L Summary
        if trades:
            daily_data = []
            for trade in trades:
                daily_data.append({
                    'Date': f"{trade.date:0>8}",  # Ensure 8 digits with leading zeros
                    'PnL': trade.total_pnl
                })
            
            pnl_df = pd.DataFrame(daily_data)
            pnl_df['Cumulative_PnL'] = pnl_df['PnL'].cumsum()
            
            # Convert date for grouping
            pnl_df['Date_parsed'] = pd.to_datetime(pnl_df['Date'], format='%d%m%Y')
            pnl_df['Month'] = pnl_df['Date_parsed'].dt.strftime('%Y-%m')
            pnl_df['Year'] = pnl_df['Date_parsed'].dt.year
            
            monthly_pnl = pnl_df.groupby('Month')['PnL'].sum().reset_index()
            yearly_pnl = pnl_df.groupby('Year')['PnL'].sum().reset_index()
        else:
            pnl_df = pd.DataFrame(columns=['Date', 'PnL', 'Cumulative_PnL'])
            monthly_pnl = pd.DataFrame(columns=['Month', 'PnL'])
            yearly_pnl = pd.DataFrame(columns=['Year', 'PnL'])
        
        # Sheet 3: All Trades
        if trades:
            trades_data = []
            for trade in trades:
                trades_data.append({
                    'Entry Date': f"{trade.date:0>8}",  # Ensure 8 digits with leading zeros
                    'Exit Date': f"{trade.exit_date:0>8}",  # Ensure 8 digits with leading zeros
                    'Entry Time': trade.entry_time,
                    'Exit Time': trade.exit_time,
                    'Strike': trade.strike,
                    'Hedge Strike': trade.hedge_strike,
                    'Type': trade.instrument_type,
                    'Entry Price': trade.entry_price,
                    'Exit Price': trade.exit_price,
                    'Hedge Entry': trade.hedge_entry_price,
                    'Hedge Exit Price': trade.hedge_exit_price,
                    'Main P&L': trade.main_pnl,
                    'Hedge P&L': trade.hedge_pnl,
                    'Total P&L': trade.total_pnl,
                    'Main P&L %': trade.main_pnl_pct,
                    'Hedge P&L %': trade.hedge_pnl_pct,
                    'Total P&L %': trade.total_pnl_pct,
                    'Entry Reason': trade.entry_reason,
                    'Exit Reason': trade.exit_reason
                })
            trades_df = pd.DataFrame(trades_data)
        else:
            trades_df = pd.DataFrame()
        
        # Create multi-sheet Excel workbook for comprehensive analysis
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            params_df.to_excel(writer, sheet_name='Input Parameters', index=False)
            
            # P&L Summary sheet with daily, monthly, and yearly breakdowns
            pnl_df[['Date', 'PnL', 'Cumulative_PnL']].to_excel(writer, sheet_name='PnL Summary', index=False, startrow=0)
            monthly_pnl.to_excel(writer, sheet_name='PnL Summary', index=False, startrow=len(pnl_df)+3)
            yearly_pnl.to_excel(writer, sheet_name='PnL Summary', index=False, startrow=len(pnl_df)+len(monthly_pnl)+6)
            
            trades_df.to_excel(writer, sheet_name='All Trades', index=False)
        
        print(f"📊 Excel report generated: {filename}")
        print(f"   - Strategy Parameters: {len(params_df)} configuration items")
        print(f"   - P&L Summary: {len(pnl_df)} trading days")
        print(f"   - Trade Details: {len(trades_df)} executed trades")