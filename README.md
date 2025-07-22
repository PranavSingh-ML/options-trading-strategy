# Options Trading Strategy Backtest

A comprehensive Python implementation of an intraday options trading strategy featuring market movement analysis, hedged positions, and advanced trailing stop management.

## Strategy Overview

This strategy implements a market-neutral options spread with sophisticated risk management:

### Entry Logic
- **Market Analysis**: Analyze spot movement from 9:15 AM to 3:25 PM
- **Trade Direction**: 
  - Market UP → Sell ATM PE (Put)
  - Market DOWN → Sell ATM CE (Call)
- **Hedge Position**: Buy OTM option 2% away from ATM strike
- **Entry Time**: 3:25 PM daily

### Advanced Exit Management
- **Independent Trailing Stops**: Main and hedge positions trail separately with 3% buffers
  - **Short Position**: Trails 3-minute lows, exits when price exceeds low + 3%
  - **Long Position**: Trails 3-minute highs, exits when price falls below high - 3%
- **Minimum Hold Period**: 3-minute buffer ensures meaningful trailing calculations
- **Time Exit**: Force exit at 9:45 AM next day if positions remain open
- **Realistic Slippage**: 0.5% applied to all transactions

## Project Structure

```
├── backtest.py             # Main backtesting execution engine
├── strategy.py             # Core trading logic and position management  
├── config.py              # Strategy configuration parameters
├── data_utils.py          # Database operations and data management
├── excel_output.py        # Report generation (Excel format)
├── chart_analysis.py      # Performance visualization and analysis
├── strategy_backtest_full.xlsx    # Complete backtest results
└── strategy_dashboard.png         # Performance visualization charts
├── Assignment/             # Data directory
│   ├── instructions.txt    # Original strategy specifications
│   ├── OPT.db             # Options price database
│   ├── OPT_sample.db      # Sample options data for testing
│   ├── SPOT.db            # Spot price database
│   └── SPOT_sample.db     # Sample spot data for testing
```

## Key Features

### 1. **Intelligent Expiry Selection**
- Automatically skips next-day expiries to ensure meaningful hedge effectiveness
- Proper datetime-based sorting for accurate contract selection
- Multi-expiry contract handling with optimal selection logic

### 2. **Advanced Position Management**
- Independent trailing stops for main and hedge positions
- Proper OTM hedge selection (PE: lower strikes, CE: higher strikes)
- 3% buffer system preventing noise-based premature exits

### 3. **Comprehensive Risk Management**
- Position-specific trailing logic (short vs long positions)
- Minimum 3-minute hold period for reliable trailing calculations
- Time-based forced exits to prevent overnight exposure
- Realistic transaction cost modeling

### 4. **Professional Reporting**
- Multi-sheet Excel reports with separate exit tracking
- 6-chart performance dashboard with detailed analytics
- Independent exit time and reason tracking for both positions

## Installation and Usage

### Prerequisites
```bash
pip install pandas numpy matplotlib seaborn openpyxl
```

### Running the Backtest
```python
# Execute complete backtest
python backtest.py

# Generate performance visualizations  
python chart_analysis.py
```

### Configuration
Modify `config.py` to adjust strategy parameters:
- Entry/exit times and market session windows
- Slippage percentages and transaction costs
- Hedge distance and trailing buffer percentages
- Database paths and lot sizing

## Results Summary

**Strategy Performance**:
- **Sophisticated Risk Management**: Independent position trailing with 3% buffers
- **Realistic Execution**: Proper expiry selection and transaction cost modeling  
- **Advanced Analytics**: Comprehensive performance tracking and visualization

**Key Features**:
- Independent exit management for optimal risk control
- Intelligent contract selection avoiding next-day expiries
- Professional-grade reporting and analysis tools

## Technical Implementation

### Core Components

1. **OptionsStrategy Class**: Complete trading workflow implementation
   - Intraday market movement analysis with directional bias detection
   - Intelligent strike selection with proper ATM and OTM hedge positioning  
   - Advanced trailing stop management with position-specific logic
   - Independent exit handling for main and hedge positions

2. **DataManager Class**: Sophisticated database operations
   - Intelligent expiry filtering with next-day expiry avoidance
   - Proper datetime-based sorting and chronological data handling
   - Multi-contract data retrieval with optimal selection algorithms

3. **Enhanced Trade Tracking**: Comprehensive trade record structure
   - Independent exit times and reasons for both positions
   - Detailed P&L attribution and percentage return calculations
   - Complete audit trail for strategy performance analysis

### Advanced Risk Management Features

- **Position-Specific Trailing**: Short positions trail lows, long positions trail highs
- **Buffer System**: 3% buffers prevent noise-based exits while preserving risk control
- **Minimum Hold Logic**: Ensures trailing calculations are based on meaningful data windows
- **Smart Contract Selection**: Avoids illiquid near-expiry contracts for reliable execution

## Generated Reports

- **strategy_backtest_full.xlsx**: Complete results with enhanced tracking
  - Input Parameters: Strategy configuration and settings
  - P&L Summary: Daily performance with cumulative analysis
  - All Trades: Detailed trade log with independent exit tracking

- **strategy_dashboard.png**: Professional 6-chart performance visualization
  - Cumulative P&L progression with drawdown analysis
  - Daily P&L distribution and volatility metrics
  - Position component performance breakdown
  - Win/loss statistics and strategy analytics

## Technical Notes

This implementation demonstrates advanced quantitative finance concepts:
- Sophisticated options strategy construction and execution
- Independent position management with proper risk controls
- Professional-grade backtesting methodology with realistic assumptions
- Comprehensive performance analysis and visualization

The strategy incorporates real-world trading considerations including proper contract selection, transaction costs, and position-specific risk management techniques used by professional options traders.

## License

This project is for educational and research purposes. Ensure compliance with relevant financial regulations before any live trading implementation.# Options Trading Strategy Backtest
