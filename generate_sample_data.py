"""
Generate realistic sample financial data for the forecasting app.
This script creates a 24-month revenue dataset with:
- Upward trend
- Seasonal patterns (Q4 spike, summer dip)
- Realistic noise
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data():
    """Generate 24 months of realistic financial data."""
    np.random.seed(42)  # For reproducibility

    # Create date range (24 months)
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=30*i) for i in range(24)]

    # Base revenue with upward trend
    base_revenue = 100000  # Starting at $100k
    trend = np.linspace(0, 50000, 24)  # Linear growth of $50k over 2 years

    # Seasonal pattern (monthly multipliers)
    # Q4 spike (Oct-Dec), summer dip (Jun-Aug)
    seasonal_pattern = {
        1: 0.95,   # January - post-holiday dip
        2: 0.92,   # February - lowest
        3: 1.00,   # March - recovery
        4: 1.02,   # April
        5: 1.05,   # May
        6: 0.98,   # June - summer dip starts
        7: 0.95,   # July - summer
        8: 0.97,   # August - summer
        9: 1.05,   # September - back to business
        10: 1.10,  # October - Q4 ramp
        11: 1.15,  # November - holiday prep
        12: 1.25,  # December - holiday peak
    }

    # Generate revenue values
    revenues = []
    for i, date in enumerate(dates):
        month = date.month
        seasonal_factor = seasonal_pattern[month]

        # Base + trend + seasonality
        revenue = (base_revenue + trend[i]) * seasonal_factor

        # Add realistic noise (3-5% variation)
        noise = np.random.normal(0, revenue * 0.04)
        revenue += noise

        revenues.append(round(revenue, 2))

    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Revenue': revenues
    })

    # Format dates as first of each month
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

    return df

if __name__ == "__main__":
    df = generate_sample_data()
    df.to_excel('sample_financial_data.xlsx', index=False)
    print("Sample data generated successfully!")
    print(f"\nData preview:\n{df.head(10)}")
    print(f"\nData statistics:\n{df['Revenue'].describe()}")
