# Options Trading Strategy Backtest

A comprehensive Python implementation of an options trading strategy based on intraday market movement analysis with hedged positions and trailing stop management.

## Strategy Overview

This strategy implements a market-neutral options spread with the following key components:

### Entry Logic
- **Market Analysis**: Analyze spot movement from 9:15 AM to 3:25 PM
- **Trade Direction**: 
  - Market UP → Sell ATM PE (Put)
  - Market DOWN → Sell ATM CE (Call)
- **Hedge Position**: Buy OTM option 2% away from ATM strike
- **Entry Time**: 3:25 PM daily

### Exit Management
- **Trailing Stops**: Both legs use 3-minute rolling highs
- **Simultaneous Exits**: When either leg hits stop, close both positions
- **Time Exit**: Force exit at 9:45 AM next day if positions still open
- **Slippage**: 0.5% applied to all entry/exit transactions

## Project Structure

```
├── config.py              # Strategy configuration parameters
├── data_utils.py           # Database operations and data management
├── strategy.py             # Core trading logic and position management
├── excel_output.py         # Report generation (Excel format)
├── chart_analysis.py       # Performance visualization and analysis
├── backtest.py             # Main backtesting execution engine
├── Assignment/             # Data directory
│   ├── instructions.txt    # Original strategy specifications
│   ├── OPT.db             # Options price database
│   ├── OPT_sample.db      # Sample options data for testing
│   ├── SPOT.db            # Spot price database
│   └── SPOT_sample.db     # Sample spot data for testing
├── strategy_backtest_full.xlsx  # Complete backtest results
├── strategy_dashboard.png       # Performance visualization charts
├── check_data_quality.py        # Data quality analysis script
└── DATA_QUALITY_ISSUES.md      # Comprehensive data quality report
```

## Key Features

### 1. **Robust Data Management**
- SQLite database integration for historical options and spot data
- Automatic date handling and chronological processing
- Sample data support for development and testing

### 2. **Advanced Position Management**
- Proper OTM hedge selection (PE: lower strikes, CE: higher strikes)
- Simultaneous exit management to prevent unhedged exposure
- Trailing stop implementation using 3-minute rolling highs

### 3. **Comprehensive Reporting**
- Multi-sheet Excel reports with parameters, P&L summary, and trade details
- Performance visualization with 6-chart dashboard
- Risk metrics and strategy analysis

### 4. **Business Logic Validation**
- P&L calculations validated against actual market movements
- Trade direction verification against intraday spot analysis
- Hedge effectiveness monitoring and analysis

## Installation and Usage

### Prerequisites
```bash
pip install pandas numpy matplotlib seaborn openpyxl
```

### Running the Backtest
```python
# Run complete backtest
python backtest.py

# Generate performance charts
python chart_analysis.py

# Validate P&L logic (optional)
python pnl_summary.py

# Check data quality issues
python check_data_quality.py

# Debug specific failed trades
python debug_failed_trades.py
```

### Configuration
Modify `config.py` to adjust strategy parameters:
- Entry/exit times
- Slippage percentages
- Hedge distance
- Data source paths

## Results Summary

**Strategy Performance** (Based on sample data):
- **Total P&L**: ₹350.48
- **Win Rate**: 46.4%
- **Average P&L per Trade**: ₹12.52
- **Total Trades**: 28 executed trades

**Key Insights**:
- Strategy shows consistent profitability with reasonable win rate
- Hedge positions provide downside protection as intended
- Time decay effects captured through overnight position management

## ⚠️ Data Quality Issues Discovered

**Critical Finding**: Significant data quality issues were identified that impact strategy execution:

- **Trade Failure Rate**: ~40% of potential trades fail due to missing morning session data
- **Missing Data Window**: 9:15-9:45 AM exit data frequently unavailable for specific option strikes
- **Strike-Specific Gaps**: Different option strikes have vastly different data completeness levels

**Impact on Results**:
- Current backtest results are based on trades with complete data only
- Many potential trading opportunities are excluded due to data gaps
- Strategy performance may be different with complete data coverage

**See [DATA_QUALITY_ISSUES.md](DATA_QUALITY_ISSUES.md) for comprehensive analysis**

## Technical Implementation

### Core Components

1. **OptionsStrategy Class**: Implements complete trading workflow
   - Market movement analysis
   - Strike selection (ATM + OTM hedge)
   - Position entry with slippage
   - Trailing stop management
   - Simultaneous exit logic

2. **DataManager Class**: Handles all database operations
   - Date filtering and chronological sorting
   - Options chain data retrieval
   - Spot price analysis
   - Multi-expiry contract handling

3. **Trade Dataclass**: Comprehensive trade record structure
   - Entry/exit timing and prices
   - P&L calculations (absolute and percentage)
   - Position details and exit reasons

### Risk Management Features

- **Hedge Protection**: OTM positions limit maximum loss exposure
- **Trailing Stops**: Dynamic exit based on 3-minute price highs
- **Time Limits**: Mandatory exit prevents extended exposure
- **Slippage Modeling**: Realistic transaction cost simulation

## Validation Results

The strategy has been thoroughly validated for business logic correctness:

✅ **P&L Arithmetic**: All calculations mathematically verified  
✅ **Trade Direction**: Entry logic matches market movement analysis  
✅ **Option Pricing**: Correct ATM vs OTM price relationships  
✅ **Hedge Behavior**: Appropriate risk-reward patterns observed  
✅ **Performance Metrics**: Results align with expected option strategy outcomes  

## Files Generated

- `strategy_backtest_full.xlsx`: Complete results with 3 sheets
  - Input Parameters: Strategy configuration
  - P&L Summary: Daily performance with cumulative tracking
  - All Trades: Detailed trade log with entry/exit analysis

- `strategy_dashboard.png`: 6-chart performance visualization
  - Cumulative P&L progression
  - Daily P&L distribution
  - Drawdown analysis
  - PE vs CE performance comparison
  - Position component analysis
  - Win/loss statistics

- `DATA_QUALITY_ISSUES.md`: Comprehensive data quality analysis
  - Missing morning session data patterns
  - Strike-specific coverage gaps
  - Failed trade case studies
  - Recommendations for data improvement

## License

This project is for educational and research purposes. Please ensure compliance with relevant financial regulations before any live trading implementation.

## Author

Implementation developed as part of quantitative finance coursework, demonstrating systematic options strategy development and backtesting methodology.
