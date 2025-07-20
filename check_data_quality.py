#!/usr/bin/env python3
"""
Comprehensive data quality analysis for options and spot databases
Checks completeness, consistency, and identifies data gaps
"""

import pandas as pd
import sqlite3
from config import StrategyConfig
from data_utils import DataManager

class DataQualityChecker:
    """Analyzes data quality across all dates and strikes"""
    
    def __init__(self):
        self.config = StrategyConfig()
        # Use full database for quality check
        self.opt_db_path = self.config.opt_db_path.replace('_sample.db', '.db')
        self.spot_db_path = self.config.spot_db_path.replace('_sample.db', '.db')
        self.data_manager = DataManager(self.opt_db_path, self.spot_db_path, use_sample=False)
        
    def check_complete_data_quality(self):
        """Comprehensive data quality check"""
        print("🔍 COMPREHENSIVE DATA QUALITY ANALYSIS")
        print("=" * 60)
        
        # Get all available dates
        available_dates = self.data_manager.get_available_dates()
        print(f"📅 Total dates in database: {len(available_dates)}")
        print(f"Date range: {available_dates[0]} to {available_dates[-1]}")
        
        # Check each date systematically
        self.check_spot_data_quality(available_dates)
        self.check_option_data_quality(available_dates)
        self.check_time_coverage(available_dates)
        self.check_strike_coverage(available_dates)
        
    def check_spot_data_quality(self, dates):
        """Check spot data completeness"""
        print(f"\n📊 SPOT DATA QUALITY CHECK")
        print("-" * 40)
        
        spot_issues = []
        for date in dates[:10]:  # Check first 10 dates to avoid overload
            try:
                spot_df = self.data_manager.get_spot_data(date)
                if len(spot_df) == 0:
                    spot_issues.append(f"{date}: No spot data")
                elif len(spot_df) < 300:  # Expect ~375 records for full day
                    spot_issues.append(f"{date}: Only {len(spot_df)} records")
                else:
                    time_range = f"{spot_df['time'].min()} to {spot_df['time'].max()}"
                    print(f"✅ {date}: {len(spot_df)} records ({time_range})")
            except Exception as e:
                spot_issues.append(f"{date}: Error - {e}")
        
        if spot_issues:
            print(f"\n⚠️ SPOT DATA ISSUES:")
            for issue in spot_issues:
                print(f"  - {issue}")
        else:
            print("✅ All spot data looks good")
    
    def check_option_data_quality(self, dates):
        """Check option data completeness by date"""
        print(f"\n📈 OPTION DATA QUALITY CHECK")
        print("-" * 40)
        
        option_issues = []
        for date in dates[:5]:  # Limit to avoid session crash
            try:
                # Get sample option data
                option_sample = self.data_manager.get_option_data(date)
                if len(option_sample) == 0:
                    option_issues.append(f"{date}: No option data")
                    continue
                
                # Check expiries
                expiries = option_sample['expiry'].unique()
                
                # Check strikes
                strikes = option_sample['strike'].unique()
                
                # Check instruments
                instruments = option_sample['instrument_type'].unique()
                
                # Check time coverage
                time_range = f"{option_sample['time'].min()} to {option_sample['time'].max()}"
                
                print(f"✅ {date}: {len(option_sample)} total records")
                print(f"   Expiries: {len(expiries)} ({expiries[0] if len(expiries) > 0 else 'None'})")
                print(f"   Strikes: {len(strikes)} (Range: {strikes.min():.0f} to {strikes.max():.0f})")
                print(f"   Instruments: {instruments}")
                print(f"   Time range: {time_range}")
                
            except Exception as e:
                option_issues.append(f"{date}: Error - {e}")
        
        if option_issues:
            print(f"\n⚠️ OPTION DATA ISSUES:")
            for issue in option_issues:
                print(f"  - {issue}")
    
    def check_time_coverage(self, dates):
        """Check time coverage for specific strikes"""
        print(f"\n⏰ TIME COVERAGE ANALYSIS")
        print("-" * 40)
        
        # Check a few problematic dates from your debug output
        problem_dates = [
            ('04092023', '05092023', 44600, 'PE'),  # Main option missing morning data
            ('07092023', '08092023', 44800, 'PE'),  # Main option missing morning data
            ('12092023', '13092023', 45500, 'CE'),  # Hedge option missing morning data
        ]
        
        for entry_date, exit_date, strike, instrument in problem_dates:
            print(f"\n🎯 Analyzing {entry_date} → {exit_date} ({instrument} {strike})")
            
            try:
                # Check exit day data for specific strike
                exit_data = self.data_manager.get_option_data(exit_date, strike, instrument)
                
                if len(exit_data) == 0:
                    print(f"❌ No data for {instrument} {strike} on {exit_date}")
                else:
                    time_range = f"{exit_data['time'].min()} to {exit_data['time'].max()}"
                    morning_data = exit_data[exit_data['time'] <= '09:45:00']
                    
                    print(f"   Total records: {len(exit_data)}")
                    print(f"   Time range: {time_range}")
                    print(f"   Morning records (<=09:45): {len(morning_data)}")
                    
                    if len(morning_data) == 0:
                        print(f"❌ MISSING: No morning data for {instrument} {strike}")
                        # Check what times are available
                        first_10_times = exit_data['time'].head(10).tolist()
                        print(f"   First 10 available times: {first_10_times}")
                    else:
                        morning_range = f"{morning_data['time'].min()} to {morning_data['time'].max()}"
                        print(f"✅ Morning data available: {morning_range}")
                        
            except Exception as e:
                print(f"❌ Error checking {exit_date}: {e}")
    
    def check_strike_coverage(self, dates):
        """Check strike availability patterns"""
        print(f"\n📊 STRIKE COVERAGE ANALYSIS")
        print("-" * 40)
        
        # Analyze strike patterns for a few dates
        sample_dates = dates[:3]
        
        for date in sample_dates:
            try:
                print(f"\n📅 Date: {date}")
                
                # Get all option data for this date
                all_options = self.data_manager.get_option_data(date)
                if len(all_options) == 0:
                    print("   No option data")
                    continue
                
                # Group by expiry and instrument
                for expiry in all_options['expiry'].unique()[:2]:  # Check first 2 expiries
                    print(f"   Expiry: {expiry}")
                    
                    expiry_data = all_options[all_options['expiry'] == expiry]
                    
                    for instrument in ['PE', 'CE']:
                        inst_data = expiry_data[expiry_data['instrument_type'] == instrument]
                        
                        if len(inst_data) == 0:
                            print(f"     {instrument}: No data")
                            continue
                        
                        strikes = inst_data['strike'].unique()
                        record_counts = inst_data.groupby('strike').size()
                        
                        print(f"     {instrument}: {len(strikes)} strikes")
                        print(f"       Strike range: {strikes.min():.0f} to {strikes.max():.0f}")
                        print(f"       Records per strike: {record_counts.min()} to {record_counts.max()}")
                        
                        # Check for strikes with very few records
                        low_count_strikes = record_counts[record_counts < 100]
                        if len(low_count_strikes) > 0:
                            print(f"       ⚠️ {len(low_count_strikes)} strikes with <100 records")
                            print(f"       Examples: {dict(low_count_strikes.head())}")
                        
            except Exception as e:
                print(f"   Error: {e}")
    
    def check_failed_trade_dates(self):
        """Specifically check the dates that failed in backtest"""
        print(f"\n🚨 FAILED TRADE ANALYSIS")
        print("-" * 40)
        
        # From your debug output - dates that failed
        failed_cases = [
            ('04092023', '05092023', 'PE', 44600, 43700),
            ('07092023', '08092023', 'PE', 44800, 43900),
            ('11092023', '12092023', 'PE', 45600, 44700),
            ('12092023', '13092023', 'CE', 45500, 46400),
            ('14092023', '15092023', 'CE', 46000, 46900),
        ]
        
        for entry_date, exit_date, instrument, main_strike, hedge_strike in failed_cases:
            print(f"\n🔍 Case: {entry_date} → {exit_date} ({instrument})")
            print(f"   Main strike: {main_strike}, Hedge strike: {hedge_strike}")
            
            # Check main strike data
            main_data = self.get_strike_analysis(exit_date, main_strike, instrument)
            print(f"   Main data: {main_data}")
            
            # Check hedge strike data  
            hedge_data = self.get_strike_analysis(exit_date, hedge_strike, instrument)
            print(f"   Hedge data: {hedge_data}")
    
    def get_strike_analysis(self, date, strike, instrument):
        """Get quick analysis for specific strike"""
        try:
            data = self.data_manager.get_option_data(date, strike, instrument)
            if len(data) == 0:
                return "No data"
            
            morning_count = len(data[data['time'] <= '09:45:00'])
            time_range = f"{data['time'].min()}-{data['time'].max()}"
            
            return f"{len(data)} records ({time_range}), {morning_count} morning"
        except:
            return "Error"

def main():
    """Run complete data quality analysis"""
    checker = DataQualityChecker()
    checker.check_complete_data_quality()
    checker.check_failed_trade_dates()
    
    print(f"\n{'='*60}")
    print("🎯 SUMMARY")
    print(f"{'='*60}")
    print("This analysis will reveal:")
    print("1. Which dates have incomplete data")
    print("2. Which strikes are missing morning sessions")
    print("3. Time coverage gaps")
    print("4. Specific reasons for trade failures")

if __name__ == "__main__":
    main()