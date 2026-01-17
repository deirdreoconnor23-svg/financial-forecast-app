# Financial Forecasting Tool

A privacy-first Streamlit web application for financial time series forecasting. All data processing happens locally on your machine - no data is ever sent to external services.

## Features

- **Upload Excel Files**: Import your financial data from .xlsx files
- **Flexible Column Selection**: Choose which columns to use for dates and values
- **Configurable Forecast Period**: Forecast 1-12 months ahead
- **Exponential Smoothing**: Advanced time series forecasting algorithm
- **Interactive Visualizations**: Plotly charts for exploring historical and forecast data
- **Key Metrics**: Historical average, forecast average, and projected growth rate
- **CSV Export**: Download your forecast results for further analysis

## Privacy

**All processing happens locally on your machine.** This application:
- Does NOT send data to any external servers
- Does NOT make any API calls
- Does NOT require an internet connection (after installation)
- Keeps your financial data completely private

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):
   ```bash
   cd financial_forecast_app
   python -m venv venv

   # On macOS/Linux:
   source venv/bin/activate

   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Streamlit server**:
   ```bash
   streamlit run forecast_app.py
   ```

2. **Open your browser** to the URL shown (typically http://localhost:8501)

3. **Upload your data** or use the included sample data to explore the features

## Using the Application

### Step 1: Load Your Data

Either:
- Click "Browse files" in the sidebar to upload your Excel file
- Check "Use sample data instead" to try the app with demo data

### Step 2: Select Columns

Choose which column contains your dates and which contains the values you want to forecast.

### Step 3: Configure Forecast

Use the slider to select how many months ahead you want to forecast (1-12 months).

### Step 4: Generate Forecast

Click the "Generate Forecast" button to run the analysis.

### Step 5: Review Results

- View key metrics (averages, growth rate)
- Explore the interactive chart
- Download results as CSV

## Data Requirements

Your Excel file should contain:

| Requirement | Description |
|-------------|-------------|
| Date Column | Dates in any standard format (YYYY-MM-DD, MM/DD/YYYY, etc.) |
| Value Column | Numeric financial values (revenue, sales, expenses, etc.) |
| Minimum Rows | At least 6 data points (12+ months recommended) |
| Frequency | Regular intervals (monthly data works best) |

### Example Data Format

| Date | Revenue |
|------|---------|
| 2023-01-01 | 100000 |
| 2023-02-01 | 105000 |
| 2023-03-01 | 110000 |
| ... | ... |

## Technical Details

### Forecasting Method

The application uses **Exponential Smoothing** (Holt-Winters method) from the statsmodels library:

- **Trend Component**: Captures upward or downward trends in your data
- **Seasonal Component**: Identifies recurring patterns (enabled with 12+ months of data)
- **Damped Trend**: Prevents unrealistic long-term extrapolation

### Dependencies

- `streamlit`: Web application framework
- `pandas`: Data manipulation
- `numpy`: Numerical computing
- `statsmodels`: Time series analysis and forecasting
- `plotly`: Interactive visualizations
- `openpyxl`: Excel file reading

## File Structure

```
financial_forecast_app/
├── forecast_app.py           # Main Streamlit application
├── requirements.txt          # Python dependencies
├── sample_financial_data.xlsx # Demo data file
├── generate_sample_data.py   # Script to regenerate sample data
└── README.md                 # This file
```

## Troubleshooting

### "Module not found" errors
Make sure you've activated your virtual environment and installed all dependencies:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### "Sample data file not found"
Ensure `sample_financial_data.xlsx` is in the same directory as `forecast_app.py`. You can regenerate it:
```bash
python generate_sample_data.py
```

### Forecast errors
- Ensure your data has at least 6 rows
- Check that your value column contains only numeric data
- Verify dates are in a consistent format

### Port already in use
If port 8501 is busy, Streamlit will suggest an alternative. Or specify a port:
```bash
streamlit run forecast_app.py --server.port 8502
```

## License

MIT License - Feel free to use, modify, and distribute.

## Support

For issues or questions, please check:
1. The troubleshooting section above
2. Streamlit documentation: https://docs.streamlit.io
3. statsmodels documentation: https://www.statsmodels.org
