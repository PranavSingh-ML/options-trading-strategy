import sqlite3
import pandas as pd
from datetime import datetime, time
from typing import List, Tuple, Optional
import os

class DataManager:
    """Manages access to options and spot price databases for backtesting"""
    def __init__(self, opt_db_path: str, spot_db_path: str, use_sample: bool = True):
        """Initialize database connections with option to use sample data for testing"""
        self.opt_db_path = opt_db_path.replace('.db', '_sample.db') if use_sample else opt_db_path
        self.spot_db_path = spot_db_path.replace('.db', '_sample.db') if use_sample else spot_db_path
        
    def get_table_names(self, db_path: str) -> List[str]:
        """Get all table names from database"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        conn.close()
        return tables
    
    def get_spot_data(self, date_table: str, start_time: str = "09:15:00", end_time: str = "15:30:00") -> pd.DataFrame:
        """Retrieve spot price data for specified date and time window"""
        conn = sqlite3.connect(self.spot_db_path)
        query = f"""
        SELECT * FROM `{date_table}` 
        WHERE time BETWEEN '{start_time}' AND '{end_time}'
        ORDER BY time
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_option_data(self, date_table: str, strike: int = None, instrument_type: str = None) -> pd.DataFrame:
        """Retrieve option price data with filtering by strike and instrument type (PE/CE)"""
        conn = sqlite3.connect(self.opt_db_path)
        
        # Build dynamic WHERE clause based on provided filters
        where_clauses = []
        if strike:
            where_clauses.append(f"strike = {strike}")
        if instrument_type:
            where_clauses.append(f"instrument_type = '{instrument_type}'")
            
        where_sql = " AND " + " AND ".join(where_clauses) if where_clauses else ""
        
        query = f"""
        SELECT * FROM `{date_table}` 
        WHERE time BETWEEN '09:15:00' AND '15:30:00' {where_sql}
        ORDER BY time, strike
        """
        df = pd.read_sql_query(query, conn)
        
        # Use nearest expiry to avoid multiple contracts for same strike
        if len(df) > 0 and strike and instrument_type:
            nearest_expiry = df['expiry'].min()
            df = df[df['expiry'] == nearest_expiry]
        
        conn.close()
        return df
    
    def get_available_dates(self) -> List[str]:
        """Get all available trading dates sorted chronologically"""
        dates = self.get_table_names(self.opt_db_path)
        # Sort by actual date order rather than alphabetical string order
        return sorted(dates, key=lambda x: pd.to_datetime(x, format='%d%m%Y'))
    
    def get_next_trading_day(self, current_date: str) -> Optional[str]:
        """Find the next available trading day for overnight position management"""
        all_dates = self.get_available_dates()
        try:
            current_idx = all_dates.index(current_date)
            if current_idx < len(all_dates) - 1:
                return all_dates[current_idx + 1]
        except ValueError:
            pass
        return None
    
    def get_atm_strike(self, spot_price: float, available_strikes: List[int]) -> int:
        """Find at-the-money strike closest to current spot price"""
        return min(available_strikes, key=lambda x: abs(x - spot_price))
    
    def get_strikes_by_expiry(self, date_table: str, expiry: str) -> List[int]:
        """Get all available strike prices for a specific expiry date"""
        conn = sqlite3.connect(self.opt_db_path)
        query = f"""
        SELECT DISTINCT strike FROM `{date_table}` 
        WHERE expiry = '{expiry}'
        ORDER BY strike
        """
        strikes = [row[0] for row in conn.execute(query).fetchall()]
        conn.close()
        return strikes