#!/usr/bin/env python3
"""
Graphical analysis module for options trading strategy results
Creates essential performance charts with proper scaling and business insights
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime

class StrategyAnalyzer:
    """Generates business-level performance charts and statistical analysis from strategy results"""
    
    def __init__(self, excel_file='strategy_backtest_full.xlsx'):
        """Initialize analyzer with Excel backtest results file"""
        self.excel_file = excel_file
        self.load_data()
        
    def load_data(self):
        """Load and prepare trading data for visualization and analysis"""
        try:
            # Load P&L and trade data from Excel workbook
            self.pnl_df = pd.read_excel(self.excel_file, sheet_name='PnL Summary')
            self.trades_df = pd.read_excel(self.excel_file, sheet_name='All Trades')
            
            # Clean and standardize P&L data
            self.pnl_df['PnL'] = pd.to_numeric(self.pnl_df['PnL'], errors='coerce')
            self.pnl_df['Date'] = pd.to_datetime(self.pnl_df['Date'], format='%d%m%Y', errors='coerce')
            self.pnl_df = self.pnl_df.dropna()
            
            # Sort chronologically for proper time series analysis
            self.pnl_df = self.pnl_df.sort_values('Date')
            
            # Calculate cumulative performance metrics
            self.pnl_df['Cumulative_PnL'] = self.pnl_df['PnL'].cumsum()
            
            # Clean and validate trade data
            numeric_cols = ['Total P&L', 'Main P&L', 'Hedge P&L']
            for col in numeric_cols:
                if col in self.trades_df.columns:
                    self.trades_df[col] = pd.to_numeric(self.trades_df[col], errors='coerce')
            
            self.trades_df = self.trades_df.dropna(subset=['Total P&L'])
            
            print(f"✅ Data loaded: {len(self.trades_df)} trades, {len(self.pnl_df)} P&L records")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            
    def create_strategy_dashboard(self):
        """Generate comprehensive 6-chart dashboard showing key performance metrics and risk analysis"""
        
        # Set up the figure with proper spacing
        fig = plt.figure(figsize=(16, 12))
        fig.suptitle('Options Trading Strategy Dashboard', fontsize=16, fontweight='bold', y=0.98)
        
        # Create 6 subplots in 3x2 grid
        gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)
        
        # Chart 1: Cumulative P&L Over Time
        ax1 = fig.add_subplot(gs[0, 0])
        if len(self.pnl_df) > 0:
            dates = self.pnl_df['Date']
            cumulative = self.pnl_df['Cumulative_PnL']
            
            ax1.plot(dates, cumulative, linewidth=2.5, color='#2E86AB', alpha=0.8)
            ax1.fill_between(dates, cumulative, alpha=0.2, color='#A23B72')
            
            # Format dates on x-axis
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
            ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Add horizontal line at zero
            ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)
            
            ax1.set_title('Cumulative P&L Performance', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Cumulative P&L (₹)')
            ax1.grid(True, alpha=0.3)
            
            # Format y-axis
            y_min, y_max = cumulative.min(), cumulative.max()
            margin = abs(y_max - y_min) * 0.1
            ax1.set_ylim(y_min - margin, y_max + margin)
        
        # Chart 2: Daily P&L Distribution
        ax2 = fig.add_subplot(gs[0, 1])
        if len(self.pnl_df) > 0:
            daily_pnl = self.pnl_df['PnL']
            
            # Create histogram with proper bins
            n_bins = min(15, max(5, len(daily_pnl) // 2))
            colors = ['red' if x < 0 else 'green' for x in daily_pnl]
            
            ax2.hist(daily_pnl, bins=n_bins, alpha=0.7, color='skyblue', 
                    edgecolor='black', linewidth=0.5)
            
            # Add mean line
            mean_pnl = daily_pnl.mean()
            ax2.axvline(mean_pnl, color='red', linestyle='--', linewidth=2, 
                       label=f'Mean: ₹{mean_pnl:.1f}')
            ax2.axvline(0, color='black', linestyle='-', alpha=0.5)
            
            ax2.set_title('Daily P&L Distribution', fontsize=12, fontweight='bold')
            ax2.set_xlabel('Daily P&L (₹)')
            ax2.set_ylabel('Frequency')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        # Chart 3: Drawdown Analysis
        ax3 = fig.add_subplot(gs[1, 0])
        if len(self.pnl_df) > 0:
            cumulative = self.pnl_df['Cumulative_PnL']
            running_max = cumulative.expanding().max()
            drawdown = cumulative - running_max  # This gives negative values (correct)
            
            dates = self.pnl_df['Date']
            ax3.fill_between(dates, drawdown, 0, alpha=0.3, color='red')
            ax3.plot(dates, drawdown, color='darkred', linewidth=2)
            
            # Format dates
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
            ax3.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            ax3.set_title('Drawdown Analysis', fontsize=12, fontweight='bold')
            ax3.set_ylabel('Drawdown (₹)')
            ax3.grid(True, alpha=0.3)
            
            # Set proper y-axis limits (drawdown is always <= 0)
            min_dd = drawdown.min()
            ax3.set_ylim(min_dd * 1.1, 50)  # Small positive margin at top
        
        # Chart 4: PE vs CE Performance Comparison
        ax4 = fig.add_subplot(gs[1, 1])
        if len(self.trades_df) > 0 and 'Type' in self.trades_df.columns:
            pe_trades = self.trades_df[self.trades_df['Type'] == 'PE']['Total P&L']
            ce_trades = self.trades_df[self.trades_df['Type'] == 'CE']['Total P&L']
            
            box_data = []
            labels = []
            
            if len(pe_trades) > 0:
                box_data.append(pe_trades)
                labels.append(f'PE ({len(pe_trades)})')
            
            if len(ce_trades) > 0:
                box_data.append(ce_trades)
                labels.append(f'CE ({len(ce_trades)})')
            
            if box_data:
                bp = ax4.boxplot(box_data, labels=labels, patch_artist=True)
                
                # Color the boxes
                colors = ['lightcoral', 'lightblue']
                for patch, color in zip(bp['boxes'], colors[:len(bp['boxes'])]):
                    patch.set_facecolor(color)
                    patch.set_alpha(0.7)
                
                ax4.axhline(y=0, color='black', linestyle='--', alpha=0.5)
                ax4.set_title('PE vs CE Performance', fontsize=12, fontweight='bold')
                ax4.set_ylabel('P&L (₹)')
                ax4.grid(True, alpha=0.3)
        
        # Chart 5: Main vs Hedge P&L Breakdown
        ax5 = fig.add_subplot(gs[2, 0])
        if len(self.trades_df) > 0 and all(col in self.trades_df.columns for col in ['Main P&L', 'Hedge P&L']):
            main_total = self.trades_df['Main P&L'].sum()
            hedge_total = self.trades_df['Hedge P&L'].sum()
            
            categories = ['Main Position', 'Hedge Position']
            values = [main_total, hedge_total]
            colors = ['green' if v > 0 else 'red' for v in values]
            
            bars = ax5.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax5.text(bar.get_x() + bar.get_width()/2., height + (abs(height)*0.01),
                        f'₹{value:.0f}', ha='center', va='bottom' if height > 0 else 'top',
                        fontweight='bold')
            
            ax5.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            ax5.set_title('Main vs Hedge P&L Contribution', fontsize=12, fontweight='bold')
            ax5.set_ylabel('Total P&L (₹)')
            ax5.grid(True, alpha=0.3, axis='y')
        
        # Chart 6: Win Rate and Trade Statistics
        ax6 = fig.add_subplot(gs[2, 1])
        if len(self.trades_df) > 0:
            total_trades = len(self.trades_df)
            winning_trades = len(self.trades_df[self.trades_df['Total P&L'] > 0])
            losing_trades = total_trades - winning_trades
            win_rate = (winning_trades / total_trades) * 100
            
            # Create pie chart
            sizes = [winning_trades, losing_trades]
            labels = [f'Winners\\n({winning_trades})', f'Losers\\n({losing_trades})']
            colors = ['lightgreen', 'lightcoral']
            
            wedges, texts, autotexts = ax6.pie(sizes, labels=labels, colors=colors, 
                                              autopct='%1.1f%%', startangle=90)
            
            ax6.set_title(f'Trade Outcomes\\nWin Rate: {win_rate:.1f}%', 
                         fontsize=12, fontweight='bold')
            
            # Make percentage text bold
            for autotext in autotexts:
                autotext.set_fontweight('bold')
        
        # Save the dashboard
        plt.savefig('strategy_dashboard.png', dpi=300, bbox_inches='tight', 
                    facecolor='white', edgecolor='none')
        print("📊 Strategy dashboard saved: strategy_dashboard.png")
        
        # Display summary statistics
        self.print_summary_stats()
        
    def print_summary_stats(self):
        """Display comprehensive strategy performance metrics and risk statistics"""
        print("\n" + "="*50)
        print("📊 STRATEGY PERFORMANCE SUMMARY")
        print("="*50)
        
        if len(self.trades_df) > 0:
            total_trades = len(self.trades_df)
            total_pnl = self.trades_df['Total P&L'].sum()
            win_rate = (self.trades_df['Total P&L'] > 0).mean() * 100
            avg_pnl = self.trades_df['Total P&L'].mean()
            best_trade = self.trades_df['Total P&L'].max()
            worst_trade = self.trades_df['Total P&L'].min()
            
            print(f"Total Trades: {total_trades}")
            print(f"Total P&L: ₹{total_pnl:.2f}")
            print(f"Win Rate: {win_rate:.1f}%")
            print(f"Average P&L per Trade: ₹{avg_pnl:.2f}")
            print(f"Best Trade: ₹{best_trade:.2f}")
            print(f"Worst Trade: ₹{worst_trade:.2f}")
            
            # Risk metrics
            returns = self.trades_df['Total P&L']
            volatility = returns.std()
            if volatility > 0:
                sharpe = returns.mean() / volatility
                print(f"Sharpe-like Ratio: {sharpe:.3f}")
            
            # Drawdown
            cumulative = returns.cumsum()
            max_drawdown = (cumulative - cumulative.cummax()).min()
            print(f"Maximum Drawdown: ₹{max_drawdown:.2f}")
            
            # Strategy breakdown
            if 'Type' in self.trades_df.columns:
                pe_count = (self.trades_df['Type'] == 'PE').sum()
                ce_count = (self.trades_df['Type'] == 'CE').sum()
                pe_pnl = self.trades_df[self.trades_df['Type'] == 'PE']['Total P&L'].sum()
                ce_pnl = self.trades_df[self.trades_df['Type'] == 'CE']['Total P&L'].sum()
                
                print(f"\nBreakdown:")
                print(f"PE Trades: {pe_count} (₹{pe_pnl:.2f})")
                print(f"CE Trades: {ce_count} (₹{ce_pnl:.2f})")
            
            if all(col in self.trades_df.columns for col in ['Main P&L', 'Hedge P&L']):
                main_pnl = self.trades_df['Main P&L'].sum()
                hedge_pnl = self.trades_df['Hedge P&L'].sum()
                print(f"Main Position P&L: ₹{main_pnl:.2f}")
                print(f"Hedge Position P&L: ₹{hedge_pnl:.2f}")
        
        print("="*50)

def main():
    """Main execution function for generating strategy performance dashboard"""
    print("🚀 Generating strategy performance dashboard...")
    analyzer = StrategyAnalyzer()
    analyzer.create_strategy_dashboard()
    print("✅ Dashboard generation complete!")

if __name__ == "__main__":
    main()