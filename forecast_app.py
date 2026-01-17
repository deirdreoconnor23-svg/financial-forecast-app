"""
Privacy-First Financial Forecasting App

A Streamlit web application for financial time series forecasting.
All data processing happens locally - no data is sent to external services.

Features:
- Upload Excel files for analysis
- Select date and value columns
- Configure forecast period (1-12 months)
- Generate forecasts using Exponential Smoothing
- Interactive Plotly visualizations
- Download forecast results as CSV

Author: Financial Forecast App
License: MIT
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import plotly.graph_objects as go
import io
from fpdf import FPDF
import tempfile
import os


# =============================================================================
# Page Configuration
# =============================================================================
st.set_page_config(
    page_title="Forecast – Financial Forecasting Tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# Custom Styling - Patch Design System
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    .stApp {
        background: #FAFAFA;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    .block-container {
        max-width: 1200px;
        padding-top: 32px;
        padding-bottom: 48px;
        padding-left: 48px;
        padding-right: 48px;
    }

    /* Wider sidebar for dashboard layout */
    [data-testid="stSidebar"] {
        min-width: 360px !important;
        max-width: 360px !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0 !important;
    }

    /* Sidebar section headers */
    .sidebar-section {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: rgba(255, 255, 255, 0.45) !important;
        margin: 24px 0 14px 0;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Custom sophisticated icons */
    .sidebar-icon {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .sidebar-icon.upload {
        background: linear-gradient(135deg, rgba(255, 149, 0, 0.15) 0%, rgba(255, 149, 0, 0.05) 100%);
        border-color: rgba(255, 149, 0, 0.3);
    }

    .sidebar-icon.data {
        background: linear-gradient(135deg, rgba(99, 179, 237, 0.15) 0%, rgba(99, 179, 237, 0.05) 100%);
        border-color: rgba(99, 179, 237, 0.3);
    }

    .sidebar-icon.settings {
        background: linear-gradient(135deg, rgba(160, 174, 192, 0.15) 0%, rgba(160, 174, 192, 0.05) 100%);
        border-color: rgba(160, 174, 192, 0.3);
    }

    .sidebar-icon.action {
        background: linear-gradient(135deg, rgba(72, 187, 120, 0.15) 0%, rgba(72, 187, 120, 0.05) 100%);
        border-color: rgba(72, 187, 120, 0.3);
    }

    .sidebar-icon.info {
        background: linear-gradient(135deg, rgba(159, 122, 234, 0.15) 0%, rgba(159, 122, 234, 0.05) 100%);
        border-color: rgba(159, 122, 234, 0.3);
    }

    /* Nav item style like inspiration */
    .nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 14px;
        border-radius: 10px;
        margin: 4px 0;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .nav-item:hover {
        background: rgba(255, 255, 255, 0.08);
    }

    .nav-item.active {
        background: rgba(255, 149, 0, 0.15);
    }

    .nav-item-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.08);
        font-size: 16px;
    }

    .nav-item.active .nav-item-icon {
        background: #FF9500;
    }

    .nav-item-text {
        font-size: 14px;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.85);
    }

    /* Generate button styling */
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #FF9500 0%, #E68600 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        padding: 16px 24px !important;
        font-size: 15px !important;
        margin-top: 8px;
        width: 100%;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #E68600 0%, #CC7700 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(255, 149, 0, 0.4);
    }

    /* Data indicator in sidebar */
    .data-indicator {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }

    .data-indicator-label {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.6);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .data-indicator-value {
        font-size: 14px;
        font-weight: 600;
        color: #FFFFFF;
        margin-top: 4px;
    }

    /* Header */
    .app-header {
        display: flex;
        align-items: center;
        gap: 18px;
        margin-bottom: 32px;
        justify-content: center;
    }

    .app-logo {
        width: 72px;
        height: 72px;
        background: linear-gradient(135deg, #FF9500 0%, #E68600 100%);
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 16px rgba(230, 134, 0, 0.3);
        font-size: 36px;
    }

    .app-title {
        font-size: 48px !important;
        font-weight: 600;
        color: #1A1A1A;
        margin: 0 !important;
        padding: 0 !important;
        letter-spacing: -0.5px;
        line-height: 0.9 !important;
    }

    .app-subtitle {
        font-size: 20px !important;
        color: #666;
        margin: 0 !important;
        padding: 0 !important;
        margin-top: 4px !important;
        font-weight: 400;
    }

    /* Cards */
    .content-card {
        background: #FFFFFF;
        border-radius: 20px;
        box-shadow: 0 2px 40px rgba(0,0,0,0.06);
        padding: 32px;
        margin-bottom: 24px;
    }

    .section-title {
        font-size: 14px;
        font-weight: 600;
        color: #1A1A1A;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 16px;
    }

    /* Privacy badge styling */
    .privacy-badge {
        background: #FFFFFF;
        border-radius: 20px;
        box-shadow: 0 2px 40px rgba(0,0,0,0.06);
        padding: 24px;
        margin-bottom: 24px;
        border-left: 4px solid #FF9500;
    }

    .privacy-badge h4 {
        color: #1A1A1A;
        margin: 0 0 8px 0;
        font-size: 16px;
        font-weight: 600;
    }

    .privacy-badge p {
        color: #666;
        margin: 0;
        font-size: 14px;
        line-height: 1.6;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #FFFFFF;
        border-radius: 16px;
        box-shadow: 0 2px 40px rgba(0,0,0,0.06);
        padding: 20px;
    }

    [data-testid="stMetricLabel"] {
        font-size: 13px !important;
        color: #666 !important;
        font-weight: 500 !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 24px !important;
        color: #1A1A1A !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricDelta"] {
        color: #FF9500 !important;
    }

    /* Info box */
    .info-box {
        background: #FFF9F0;
        border-left: 4px solid #FF9500;
        padding: 16px 20px;
        margin: 16px 0;
        border-radius: 0 12px 12px 0;
        font-size: 14px;
        color: #1A1A1A;
    }

    /* Buttons */
    .stButton > button {
        background: #1A1A1A !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
    }

    .stButton > button:hover {
        background: #333 !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF9500 0%, #E68600 100%) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #E68600 0%, #CC7700 100%) !important;
    }

    /* Download button */
    .stDownloadButton > button {
        background: #1A1A1A !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }

    .stDownloadButton > button:hover {
        background: #333 !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 16px;
    }

    [data-testid="stFileUploader"] > div > div {
        border: 2px dashed #EBEBEB !important;
        border-radius: 12px !important;
    }

    /* Select boxes */
    .stSelectbox > div > div {
        background: #FFFFFF !important;
        border: 2px solid #EBEBEB !important;
        border-radius: 12px !important;
    }

    /* Slider */
    .stSlider > div > div > div {
        background: #FF9500 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #FFFFFF !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        color: #1A1A1A !important;
    }

    /* Dataframe */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Sidebar styling - Charcoal grey professional look */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2D3436 0%, #222526 100%);
        border-right: none;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 24px;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdown"] {
        color: #FFFFFF;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdown"] p {
        color: rgba(255, 255, 255, 0.85);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdown"] strong {
        color: #FFFFFF;
    }

    [data-testid="stSidebar"] .section-title {
        color: rgba(255, 255, 255, 0.6) !important;
        font-size: 11px !important;
        letter-spacing: 1px;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.15);
    }

    /* Sidebar - Make ALL text white */
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
    [data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"] {
        color: rgba(255, 255, 255, 0.8) !important;
    }

    /* Sidebar file uploader */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 12px;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] section {
        background: rgba(255, 255, 255, 0.12) !important;
        border: 1px dashed rgba(255, 255, 255, 0.4) !important;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] section:hover {
        background: rgba(255, 255, 255, 0.18) !important;
        border-color: rgba(255, 255, 255, 0.6) !important;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] small {
        color: rgba(255, 255, 255, 0.8) !important;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] button {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }

    /* Light grey select boxes in sidebar */
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.12) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
    }

    [data-testid="stSidebar"] .stSelectbox > div > div:hover {
        background: rgba(255, 255, 255, 0.18) !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
    }

    /* Lighter slider track */
    [data-testid="stSidebar"] .stSlider > div > div > div > div {
        background: rgba(255, 255, 255, 0.15) !important;
    }

    /* Sidebar checkbox */
    [data-testid="stSidebar"] .stCheckbox {
        background: rgba(255, 255, 255, 0.05);
        padding: 8px 12px;
        border-radius: 8px;
        margin: 4px 0;
    }

    /* Sidebar expander - Step styling */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.06) !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.15) !important;
    }

    [data-testid="stSidebar"] .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 0 0 10px 10px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-top: none;
        padding: 16px !important;
        margin-top: -4px;
    }

    /* Step number/checkmark styling */
    [data-testid="stSidebar"] .streamlit-expanderHeader p {
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }

    /* Step row - icon and expander inline */
    .step-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 12px;
    }

    .step-row + div [data-testid="stExpander"] {
        flex: 1;
    }

    .step-icon {
        width: 34px;
        height: 34px;
        min-width: 34px;
        border-radius: 9px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        z-index: 1;
    }

    .step-icon.upload {
        background: linear-gradient(135deg, rgba(255, 149, 0, 0.2) 0%, rgba(255, 149, 0, 0.1) 100%);
        border: 1px solid rgba(255, 149, 0, 0.3);
        box-shadow: 0 2px 8px rgba(255, 149, 0, 0.15);
    }

    .step-icon.data {
        background: linear-gradient(135deg, rgba(99, 179, 237, 0.2) 0%, rgba(99, 179, 237, 0.1) 100%);
        border: 1px solid rgba(99, 179, 237, 0.3);
        box-shadow: 0 2px 8px rgba(99, 179, 237, 0.15);
    }

    .step-icon.settings {
        background: linear-gradient(135deg, rgba(160, 174, 192, 0.2) 0%, rgba(160, 174, 192, 0.1) 100%);
        border: 1px solid rgba(160, 174, 192, 0.3);
        box-shadow: 0 2px 8px rgba(160, 174, 192, 0.15);
    }

    .step-icon.action {
        background: linear-gradient(135deg, rgba(72, 187, 120, 0.2) 0%, rgba(72, 187, 120, 0.1) 100%);
        border: 1px solid rgba(72, 187, 120, 0.3);
        box-shadow: 0 2px 8px rgba(72, 187, 120, 0.15);
    }

    .step-icon.info {
        background: linear-gradient(135deg, rgba(159, 122, 234, 0.2) 0%, rgba(159, 122, 234, 0.1) 100%);
        border: 1px solid rgba(159, 122, 234, 0.3);
        box-shadow: 0 2px 8px rgba(159, 122, 234, 0.15);
    }

    /* Inline step container */
    .step-container {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin-top: 14px;
    }

    .step-container .step-icon {
        margin-top: 8px;
    }

    [data-testid="stSidebar"] details summary span {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebar"] ul,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #FFFFFF !important;
    }

    /* Sidebar logo area */
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 20px 8px 28px 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 8px;
    }

    .sidebar-logo-icon {
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #FF9500 0%, #E68600 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 16px rgba(255, 149, 0, 0.35);
        color: white;
    }

    .sidebar-logo-icon svg {
        stroke: white;
    }

    .sidebar-logo-text {
        font-size: 24px;
        font-weight: 600;
        color: #FFFFFF;
        letter-spacing: -0.5px;
    }

    /* Success/Error messages */
    .stSuccess {
        background: #F0FFF4 !important;
        border: 1px solid #68D391 !important;
        border-radius: 12px !important;
        color: #1A1A1A !important;
    }

    .stError {
        background: #FFF5F5 !important;
        border: 1px solid #FC8181 !important;
        border-radius: 12px !important;
    }

    /* Footer */
    .app-footer {
        text-align: center;
        font-size: 13px;
        color: #999;
        margin: 32px 0 16px 0;
        padding-top: 24px;
        border-top: 1px solid #EBEBEB;
    }

    /* Checkbox */
    .stCheckbox label {
        color: #1A1A1A !important;
        font-weight: 400 !important;
    }

    /* Hide anchor links */
    .css-zt5igj {
        display: none;
    }

    a[href^="#"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# Helper Functions
# =============================================================================

def load_excel_file(uploaded_file):
    """
    Load an Excel file into a pandas DataFrame.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        tuple: (DataFrame or None, error message or None)
    """
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        if df.empty:
            return None, "The uploaded file is empty."
        return df, None
    except Exception as e:
        return None, f"Error reading file: {str(e)}"


def infer_date_format(series):
    """
    Infer the date format from a series of date strings.

    Args:
        series: pandas Series containing date values

    Returns:
        str or None: Inferred date format string, or None if couldn't infer
    """
    # Common date formats to try
    common_formats = [
        '%Y-%m-%d',      # 2024-01-15
        '%d/%m/%Y',      # 15/01/2024
        '%m/%d/%Y',      # 01/15/2024
        '%d-%m-%Y',      # 15-01-2024
        '%Y/%m/%d',      # 2024/01/15
        '%d.%m.%Y',      # 15.01.2024
        '%Y-%m-%d %H:%M:%S',  # 2024-01-15 10:30:00
        '%d/%m/%Y %H:%M:%S',  # 15/01/2024 10:30:00
        '%Y-%m',         # 2024-01
        '%m/%Y',         # 01/2024
        '%b %Y',         # Jan 2024
        '%B %Y',         # January 2024
        '%d %b %Y',      # 15 Jan 2024
        '%d %B %Y',      # 15 January 2024
    ]

    # Get sample of non-null values
    sample = series.dropna().head(5)
    if len(sample) == 0:
        return None

    # Try each format
    for fmt in common_formats:
        try:
            # Try to parse all sample values with this format
            for val in sample:
                pd.to_datetime(str(val), format=fmt)
            # If we get here, the format works
            return fmt
        except (ValueError, TypeError):
            continue

    return None


def detect_date_column(df):
    """
    Auto-detect which column contains dates, prioritizing columns with date-related keywords.

    Args:
        df: pandas DataFrame

    Returns:
        str or None: Name of the detected date column, or None if not found
    """
    # Keywords that suggest a date column (case-insensitive)
    date_keywords = ['date', 'month', 'period', 'time', 'quarter', 'year', 'day', 'week']

    date_columns = []
    keyword_matches = []

    for col in df.columns:
        col_lower = col.lower()
        is_keyword_match = any(keyword in col_lower for keyword in date_keywords)

        # Check if already datetime
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            if is_keyword_match:
                keyword_matches.append(col)
            else:
                date_columns.append(col)
            continue

        # Try to parse as dates
        try:
            # Skip if mostly numeric (could be years, IDs, etc.)
            if pd.api.types.is_numeric_dtype(df[col]):
                # Check if it looks like years (e.g., 2023, 2024)
                sample = df[col].dropna().head(10)
                if sample.between(1900, 2100).all():
                    continue
                continue

            # Try to infer date format first
            date_format = infer_date_format(df[col])
            if date_format:
                parsed = pd.to_datetime(df[col], format=date_format, errors='coerce')
            else:
                # Fallback to auto-parsing with warning suppressed
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    parsed = pd.to_datetime(df[col], errors='coerce')

            valid_ratio = parsed.notna().sum() / len(df)

            # If more than 80% parsed successfully, it's likely a date column
            if valid_ratio > 0.8:
                if is_keyword_match:
                    keyword_matches.append(col)
                else:
                    date_columns.append(col)
        except Exception:
            continue

    # Prioritize keyword matches, then other date columns
    all_date_cols = keyword_matches + date_columns
    return all_date_cols[0] if all_date_cols else None


def detect_numeric_columns(df, exclude_col=None):
    """
    Detect numeric columns suitable for forecasting.

    Args:
        df: pandas DataFrame
        exclude_col: Column to exclude (e.g., the date column)

    Returns:
        list: Names of numeric columns
    """
    numeric_cols = []

    for col in df.columns:
        if col == exclude_col:
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
        else:
            # Try to convert
            try:
                pd.to_numeric(df[col], errors='raise')
                numeric_cols.append(col)
            except Exception:
                continue

    return numeric_cols


def suggest_value_column(df, numeric_columns):
    """
    Suggest the best value column based on keywords and data characteristics.

    Args:
        df: pandas DataFrame
        numeric_columns: List of numeric column names

    Returns:
        str or None: Suggested value column name
    """
    if not numeric_columns:
        return None

    # Keywords that suggest a value/financial column (case-insensitive)
    value_keywords = ['revenue', 'sales', 'amount', 'value', 'total', 'price',
                      'income', 'profit', 'cost', 'expense', 'payment', 'balance',
                      'sum', 'money', 'fee', 'charge', 'earning']

    keyword_matches = []
    other_cols = []

    for col in numeric_columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in value_keywords):
            keyword_matches.append(col)
        else:
            other_cols.append(col)

    # Prioritize keyword matches
    if keyword_matches:
        return keyword_matches[0]
    elif other_cols:
        return other_cols[0]
    return None


def validate_columns(df, date_col, value_col):
    """
    Validate that selected columns are appropriate for forecasting.

    Args:
        df: pandas DataFrame
        date_col: Name of the date column
        value_col: Name of the value column

    Returns:
        tuple: (success boolean, error message or None)
    """
    # Check if columns exist
    if date_col not in df.columns or value_col not in df.columns:
        return False, "Selected columns not found in the data."

    # Try to convert date column
    try:
        pd.to_datetime(df[date_col])
    except Exception:
        return False, f"'{date_col}' cannot be converted to dates. Please select a valid date column."

    # Check if value column is numeric
    if not pd.api.types.is_numeric_dtype(df[value_col]):
        # Try to convert
        try:
            pd.to_numeric(df[value_col], errors='raise')
        except Exception:
            return False, f"'{value_col}' is not numeric. Please select a column with numerical values."

    # Check for sufficient data
    if len(df) < 6:
        return False, "At least 6 data points are required for forecasting."

    return True, None


def prepare_time_series(df, date_col, value_col):
    """
    Prepare data for time series forecasting.

    Args:
        df: pandas DataFrame
        date_col: Name of the date column
        value_col: Name of the value column

    Returns:
        pandas Series with datetime index
    """
    # Create a copy to avoid modifying original
    ts_df = df[[date_col, value_col]].copy()

    # Try to infer date format to avoid warnings
    date_format = infer_date_format(ts_df[date_col])
    if date_format:
        ts_df[date_col] = pd.to_datetime(ts_df[date_col], format=date_format)
    else:
        # Fallback with warnings suppressed
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ts_df[date_col] = pd.to_datetime(ts_df[date_col])

    ts_df[value_col] = pd.to_numeric(ts_df[value_col], errors='coerce')

    # Remove any rows with missing values
    ts_df = ts_df.dropna()

    # Sort by date
    ts_df = ts_df.sort_values(date_col)

    # Set date as index
    ts_df = ts_df.set_index(date_col)

    # Return as Series
    return ts_df[value_col]


def generate_forecast(time_series, forecast_periods):
    """
    Generate forecast using Exponential Smoothing.

    Args:
        time_series: pandas Series with datetime index
        forecast_periods: Number of periods to forecast

    Returns:
        tuple: (forecast Series, fitted model, error message or None)
    """
    try:
        # Determine seasonal periods (assume monthly data with yearly seasonality)
        # If we have at least 2 years of data, use seasonal model
        n_obs = len(time_series)

        if n_obs >= 24:
            # Full seasonal model with trend (needs 2+ full cycles for seasonality)
            model = ExponentialSmoothing(
                time_series,
                trend='add',
                seasonal='add',
                seasonal_periods=12,
                damped_trend=True
            )
        elif n_obs >= 12:
            # Trend model with damping (not enough data for seasonal)
            model = ExponentialSmoothing(
                time_series,
                trend='add',
                seasonal=None,
                damped_trend=True
            )
        else:
            # Simple trend model
            model = ExponentialSmoothing(
                time_series,
                trend='add',
                seasonal=None,
                damped_trend=False
            )

        # Fit the model
        fitted_model = model.fit(optimized=True)

        # Generate forecast
        forecast = fitted_model.forecast(forecast_periods)

        # Create forecast index (continue from last date)
        last_date = time_series.index[-1]
        forecast_index = pd.date_range(
            start=last_date + pd.DateOffset(months=1),
            periods=forecast_periods,
            freq='MS'  # Month Start
        )
        forecast.index = forecast_index

        return forecast, fitted_model, None

    except Exception as e:
        return None, None, f"Forecasting error: {str(e)}"


def create_forecast_chart(historical_data, forecast_data, value_col_name):
    """
    Create an interactive Plotly chart showing historical and forecast data.

    Args:
        historical_data: pandas Series with historical values
        forecast_data: pandas Series with forecast values
        value_col_name: Name of the value column for labeling

    Returns:
        plotly Figure object
    """
    fig = go.Figure()

    # Historical data trace - Patch orange theme
    fig.add_trace(go.Scatter(
        x=historical_data.index,
        y=historical_data.values,
        mode='lines+markers',
        name='Historical Data',
        line=dict(color='#FF9500', width=2),
        marker=dict(size=6, color='#FF9500'),
        hovertemplate='<b>Date:</b> %{x|%d/%m/%Y}<br>' +
                      '<b>Value:</b> €%{y:,.2f}<extra></extra>'
    ))

    # Forecast data trace - include last historical point to connect the lines
    forecast_x = [historical_data.index[-1]] + list(forecast_data.index)
    forecast_y = [historical_data.values[-1]] + list(forecast_data.values)

    fig.add_trace(go.Scatter(
        x=forecast_x,
        y=forecast_y,
        mode='lines+markers',
        name='Forecast',
        line=dict(color='#1A1A1A', width=2, dash='dash'),
        marker=dict(size=6, color='#1A1A1A', symbol='diamond'),
        hovertemplate='<b>Date:</b> %{x|%d/%m/%Y}<br>' +
                      '<b>Forecast:</b> €%{y:,.2f}<extra></extra>'
    ))

    # Add vertical line at forecast start
    forecast_start_date = historical_data.index[-1].to_pydatetime()
    fig.add_shape(
        type="line",
        x0=forecast_start_date,
        x1=forecast_start_date,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(width=1, dash="dot", color="gray")
    )
    fig.add_annotation(
        x=forecast_start_date,
        y=1,
        yref="paper",
        text="Forecast Start",
        showarrow=False,
        yshift=10
    )

    # Update layout - Patch style
    fig.update_layout(
        title=dict(
            text=f'{value_col_name} — Historical vs Forecast',
            font=dict(size=18, color='#1A1A1A', family='Inter, sans-serif'),
            x=0.5,
            xanchor='center'
        ),
        xaxis_title='Date',
        yaxis_title=f'{value_col_name} (€)',
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(family='Inter, sans-serif', color='#666')
        ),
        plot_bgcolor='#FAFAFA',
        paper_bgcolor='#FFFFFF',
        font=dict(family='Inter, sans-serif', color='#1A1A1A'),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#EBEBEB',
            showline=True,
            linewidth=1,
            linecolor='#EBEBEB',
            tickfont=dict(color='#666')
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#EBEBEB',
            showline=True,
            linewidth=1,
            linecolor='#EBEBEB',
            tickformat='€,.0f',
            tickfont=dict(color='#666')
        ),
        margin=dict(l=60, r=40, t=80, b=60)
    )

    return fig


def calculate_metrics(historical_data, forecast_data):
    """
    Calculate key metrics for display.

    Args:
        historical_data: pandas Series with historical values
        forecast_data: pandas Series with forecast values

    Returns:
        dict with calculated metrics
    """
    historical_avg = historical_data.mean()
    forecast_avg = forecast_data.mean()

    # Growth rate: compare last historical value to last forecast value
    last_historical = historical_data.iloc[-1]
    last_forecast = forecast_data.iloc[-1]
    growth_rate = ((last_forecast - last_historical) / last_historical) * 100

    # Projected total
    projected_total = forecast_data.sum()

    return {
        'historical_avg': historical_avg,
        'forecast_avg': forecast_avg,
        'growth_rate': growth_rate,
        'projected_total': projected_total,
        'historical_total': historical_data.sum(),
        'forecast_periods': len(forecast_data)
    }


def create_download_csv(historical_data, forecast_data, value_col_name):
    """
    Create a CSV file for download containing historical and forecast data.

    Args:
        historical_data: pandas Series with historical values
        forecast_data: pandas Series with forecast values
        value_col_name: Name of the value column

    Returns:
        CSV string
    """
    # Combine historical and forecast data
    combined_df = pd.DataFrame({
        'Date': list(historical_data.index) + list(forecast_data.index),
        value_col_name: list(historical_data.values) + list(forecast_data.values),
        'Type': ['Historical'] * len(historical_data) + ['Forecast'] * len(forecast_data)
    })

    # Format dates
    combined_df['Date'] = pd.to_datetime(combined_df['Date']).dt.strftime('%d/%m/%Y')

    return combined_df.to_csv(index=False)


class ForecastPDF(FPDF):
    """Custom PDF class for Forecast reports with Patch-style branding."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        # Orange accent bar at top
        self.set_fill_color(255, 149, 0)  # #FF9500
        self.rect(0, 0, 210, 8, 'F')

        # Logo/Title area
        self.set_y(15)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(26, 26, 26)  # #1A1A1A
        self.cell(0, 10, 'Forecast', ln=True, align='C')

        self.set_font('Helvetica', '', 12)
        self.set_text_color(102, 102, 102)  # #666
        self.cell(0, 6, 'Financial Forecasting Report', ln=True, align='C')

        self.ln(10)

    def footer(self):
        self.set_y(-20)
        self.set_font('Helvetica', '', 9)
        self.set_text_color(153, 153, 153)  # #999
        self.cell(0, 10, f'Generated {datetime.now().strftime("%d/%m/%Y %H:%M")} | Powered by local AI - Your data stays private', align='C')

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(26, 26, 26)
        self.cell(0, 10, title.upper(), ln=True)
        self.ln(2)

    def add_metric_box(self, label, value, x, y, width=45):
        # Draw box background
        self.set_fill_color(250, 250, 250)  # #FAFAFA
        self.rect(x, y, width, 22, 'F')

        # Draw border
        self.set_draw_color(235, 235, 235)  # #EBEBEB
        self.rect(x, y, width, 22, 'D')

        # Label
        self.set_xy(x + 2, y + 3)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(102, 102, 102)
        self.cell(width - 4, 5, label, align='C')

        # Value
        self.set_xy(x + 2, y + 10)
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(26, 26, 26)
        self.cell(width - 4, 8, value, align='C')

    def add_data_table(self, headers, data, col_widths=None):
        if col_widths is None:
            col_widths = [95, 95]

        # Header row
        self.set_fill_color(26, 26, 26)  # #1A1A1A
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 10)

        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, border=1, fill=True, align='C')
        self.ln()

        # Data rows
        self.set_text_color(26, 26, 26)
        self.set_font('Helvetica', '', 10)

        for row_idx, row in enumerate(data):
            # Alternate row colors
            if row_idx % 2 == 0:
                self.set_fill_color(255, 255, 255)
            else:
                self.set_fill_color(250, 250, 250)

            for i, cell in enumerate(row):
                self.cell(col_widths[i], 7, str(cell), border=1, fill=True, align='C')
            self.ln()


def create_pdf_report(historical_data, forecast_data, value_col_name, metrics, chart_fig):
    """
    Create a PDF report with forecast results.

    Args:
        historical_data: pandas Series with historical values
        forecast_data: pandas Series with forecast values
        value_col_name: Name of the value column
        metrics: Dictionary with calculated metrics
        chart_fig: Plotly figure object

    Returns:
        bytes: PDF file content
    """
    pdf = ForecastPDF()
    pdf.add_page()

    # Executive Summary section
    pdf.section_title('Executive Summary')

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(66, 66, 66)

    growth_direction = "increase" if metrics['growth_rate'] > 0 else "decrease"
    summary_text = (
        f"This report presents a {metrics['forecast_periods']}-month financial forecast for {value_col_name}. "
        f"Based on historical data analysis using Exponential Smoothing, the model projects a "
        f"{abs(metrics['growth_rate']):.1f}% {growth_direction} from the last recorded value to the end of the forecast period. "
        f"The total projected value over the forecast period is EUR {metrics['projected_total']:,.0f}."
    )
    pdf.multi_cell(0, 6, summary_text)
    pdf.ln(8)

    # Key Metrics section
    pdf.section_title('Key Metrics')

    start_y = pdf.get_y()
    pdf.add_metric_box('Historical Avg', f"EUR {metrics['historical_avg']:,.0f}", 10, start_y, width=46)
    pdf.add_metric_box('Forecast Avg', f"EUR {metrics['forecast_avg']:,.0f}", 58, start_y, width=46)
    pdf.add_metric_box('Projected Growth', f"{metrics['growth_rate']:+.1f}%", 106, start_y, width=46)
    pdf.add_metric_box(f"{metrics['forecast_periods']}-Mo Total", f"EUR {metrics['projected_total']:,.0f}", 154, start_y, width=46)

    pdf.set_y(start_y + 30)

    # Chart section
    pdf.section_title('Forecast Visualization')

    # Export chart to image
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        chart_fig.write_image(tmp_file.name, width=800, height=400, scale=2)
        pdf.image(tmp_file.name, x=10, w=190)
        os.unlink(tmp_file.name)

    pdf.ln(5)

    # Add new page for data tables
    pdf.add_page()

    # Historical Data table
    pdf.section_title('Historical Data (Last 6 Periods)')

    hist_data = []
    for date, value in zip(historical_data.index[-6:], historical_data.values[-6:]):
        hist_data.append([date.strftime('%d/%m/%Y'), f"EUR {value:,.2f}"])

    pdf.add_data_table(['Date', value_col_name], hist_data)
    pdf.ln(10)

    # Forecast Data table
    pdf.section_title('Forecast Data')

    forecast_table_data = []
    for date, value in zip(forecast_data.index, forecast_data.values):
        forecast_table_data.append([date.strftime('%d/%m/%Y'), f"EUR {value:,.2f}"])

    pdf.add_data_table(['Date', f'{value_col_name} (Forecast)'], forecast_table_data)
    pdf.ln(10)

    # Methodology note
    pdf.section_title('Methodology')
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(102, 102, 102)
    methodology_text = (
        "This forecast was generated using Exponential Smoothing (Holt-Winters method), "
        "which accounts for trends and seasonal patterns in the data. The model automatically "
        "adapts its parameters based on the amount of historical data available. "
        "All data processing occurs locally - no data is transmitted to external servers."
    )
    pdf.multi_cell(0, 5, methodology_text)

    # Return PDF as bytes
    return bytes(pdf.output())


# =============================================================================
# Main Application
# =============================================================================

def main():
    """Main application entry point."""

    # Initialize session state
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'forecast_generated' not in st.session_state:
        st.session_state.forecast_generated = False
    if 'date_col' not in st.session_state:
        st.session_state.date_col = None
    if 'value_col' not in st.session_state:
        st.session_state.value_col = None
    if 'forecast_months' not in st.session_state:
        st.session_state.forecast_months = 6

    # ==========================================================================
    # SIDEBAR - Minimal: Only Data Source and How It Works
    # ==========================================================================
    with st.sidebar:
        # Logo
        st.markdown("""
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 3v18h18"/>
                    <path d="M18 9l-5 5-4-4-3 3"/>
                </svg>
            </div>
            <div>
                <div class="sidebar-logo-text">Forecast</div>
                <div style="color: rgba(255,255,255,0.5); font-size: 12px; margin-top: 2px;">Financial Forecasting Tool</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Variables to track data state
        df = None
        data_loaded = False

        # =====================================================================
        # DATA SOURCE - File Upload
        # =====================================================================
        col_icon1, col_exp1 = st.columns([0.12, 0.88])
        with col_icon1:
            st.markdown("""
            <div class="step-icon upload" style="margin-top: 6px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 3 7 8"/>
                    <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
            </div>
            """, unsafe_allow_html=True)
        with col_exp1:
            with st.expander("Data Source", expanded=True):
                uploaded_file = st.file_uploader(
                    "Upload Excel file",
                    type=['xlsx', 'xls'],
                    help="Excel file with date and numeric columns",
                    label_visibility="collapsed"
                )

                st.markdown("<div style='margin: 8px 0; text-align: center; color: rgba(255,255,255,0.3); font-size: 11px;'>— or —</div>", unsafe_allow_html=True)

                use_sample = st.checkbox(
                    "Use sample data",
                    help="Try the app with demo financial data"
                )

        # Load data based on selection
        data_status = None

        if use_sample:
            try:
                df = pd.read_excel('sample_financial_data_24months.xlsx', engine='openpyxl')
                data_loaded = True
                data_status = ("success", "Sample data loaded")
            except FileNotFoundError:
                data_status = ("error", "Sample file not found")
            except Exception as e:
                data_status = ("error", f"Error: {str(e)}")
        elif uploaded_file is not None:
            df, error = load_excel_file(uploaded_file)
            if error:
                data_status = ("error", error)
            else:
                data_loaded = True
                data_status = ("success", uploaded_file.name)

        # Show status
        if data_status:
            status_type, status_msg = data_status
            if status_type == "success":
                st.markdown(f"""
                <div class="data-indicator" style="margin: 4px 0 16px 0;">
                    <div class="data-indicator-value" style="color: #48BB78; font-size: 12px;">✓ {status_msg}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(status_msg)

        # =====================================================================
        # HOW IT WORKS
        # =====================================================================
        st.markdown("<hr style='margin: 16px 0; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

        col_icon_info, col_exp_info = st.columns([0.12, 0.88])
        with col_icon_info:
            st.markdown("""
            <div class="step-icon info" style="margin-top: 6px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M12 16v-4"/>
                    <path d="M12 8h.01"/>
                </svg>
            </div>
            """, unsafe_allow_html=True)
        with col_exp_info:
            with st.expander("How It Works"):
                st.markdown("""
                **Forecasting Method**

                Uses **Exponential Smoothing** (Holt-Winters):
                - Adapts to data trends
                - Captures seasonal patterns
                - Reliable short-term forecasts

                ---

                **Model Selection**

                - **24+ months:** Full seasonal + trend
                - **12-23 months:** Trend with damping
                - **6-11 months:** Simple trend
                - **< 6 months:** Not supported

                ---

                **Privacy**

                All processing is local. Your data never leaves your computer.
                """)

    # ==========================================================================
    # MAIN CONTENT AREA - Vertical Workflow
    # ==========================================================================

    # Show different content based on state
    if not data_loaded or df is None:
        # Welcome state - no data loaded
        st.markdown("""
        <div class="app-header">
            <div class="app-logo">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                    <path d="M3 3v18h18"/>
                    <path d="M18 9l-5 5-4-4-3 3"/>
                </svg>
            </div>
            <div>
                <h1 class="app-title">Forecast</h1>
                <p class="app-subtitle">Financial Forecasting Tool</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="privacy-badge">
            <h4>Welcome to Forecast</h4>
            <p>Upload your financial data using the sidebar to get started. Your data stays completely private —
            all processing happens locally on your machine.</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="content-card">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <div class="step-icon upload">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FF9500" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                            <polyline points="17 8 12 3 7 8"/>
                            <line x1="12" y1="3" x2="12" y2="15"/>
                        </svg>
                    </div>
                    <h4 style="margin: 0;">Upload Your Data</h4>
                </div>
                <p style="color: #666; font-size: 14px; margin: 0;">
                Use the sidebar to upload an Excel file with your financial data.
                The file should have a date column and numeric value column(s).
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="content-card">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <div class="step-icon data">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#63B3ED" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2"/>
                            <path d="M3 9h18"/>
                            <path d="M9 21V9"/>
                        </svg>
                    </div>
                    <h4 style="margin: 0;">Try Sample Data</h4>
                </div>
                <p style="color: #666; font-size: 14px; margin: 0;">
                Check "Use sample data" in the sidebar to explore the app
                with demo financial data before uploading your own.
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<p class="section-title">Data Requirements</p>', unsafe_allow_html=True)
        st.markdown("""
        - **Date Column**: Dates in any standard format
        - **Value Column**: Numeric values (revenue, sales, expenses, etc.)
        - **Minimum 6 months** of data (24+ months recommended)
        - **Regular intervals** (monthly data works best)
        """)

    else:
        # =====================================================================
        # DATA LOADED - Show Complete Vertical Workflow
        # =====================================================================

        # Auto-detect columns
        detected_date_col = detect_date_column(df)
        numeric_columns = detect_numeric_columns(df, detected_date_col)
        suggested_value_col = suggest_value_column(df, numeric_columns)

        # =====================================================================
        # STEP 1: CONFIGURE DATA
        # =====================================================================
        st.markdown('<p class="section-title">Step 1: Configure Data</p>', unsafe_allow_html=True)

        # Column Selection
        col1, col2 = st.columns(2)

        with col1:
            # Date column selection - put detected date column first in options
            if detected_date_col:
                # Reorder columns to put detected date first
                date_options = [detected_date_col] + [c for c in df.columns if c != detected_date_col]
                st.markdown("**Date Column** <span style='color: #48BB78; font-size: 12px;'>(auto-detected)</span>", unsafe_allow_html=True)
                date_col = st.selectbox(
                    "Date Column",
                    options=date_options,
                    index=0,
                    help="Auto-detected based on column name and data format. Change if incorrect.",
                    label_visibility="collapsed"
                )
            else:
                st.markdown("**Date Column** <span style='color: #E53E3E; font-size: 12px;'>(please select)</span>", unsafe_allow_html=True)
                date_col = st.selectbox(
                    "Date Column",
                    options=df.columns.tolist(),
                    help="Select the column containing dates",
                    label_visibility="collapsed"
                )

        with col2:
            # Value column selection - put suggested value column first in options
            if len(numeric_columns) >= 1:
                if suggested_value_col:
                    # Reorder columns to put suggested value first
                    value_options = [suggested_value_col] + [c for c in numeric_columns if c != suggested_value_col]
                    st.markdown("**Value Column** <span style='color: #48BB78; font-size: 12px;'>(auto-suggested)</span>", unsafe_allow_html=True)
                else:
                    value_options = numeric_columns
                    st.markdown("**Value Column**", unsafe_allow_html=True)

                value_col = st.selectbox(
                    "Value Column",
                    options=value_options,
                    index=0,
                    help="Auto-suggested based on column name (revenue, sales, etc.). Change if incorrect.",
                    label_visibility="collapsed"
                )
            else:
                st.markdown("**Value Column** <span style='color: #E53E3E; font-size: 12px;'>(no numeric columns found)</span>", unsafe_allow_html=True)
                available = [c for c in df.columns if c != date_col]
                value_col = st.selectbox(
                    "Value Column",
                    options=available,
                    help="Select the column to forecast",
                    label_visibility="collapsed"
                )

        # Store in session state
        st.session_state.date_col = date_col
        st.session_state.value_col = value_col

        # Validation
        validation_passed = True
        date_valid = False
        value_valid = False
        date_error = None
        value_error = None

        # Validate date column
        try:
            date_format = infer_date_format(df[date_col])
            if date_format:
                test_parsed = pd.to_datetime(df[date_col], format=date_format, errors='coerce')
            else:
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    test_parsed = pd.to_datetime(df[date_col], errors='coerce')

            valid_count = test_parsed.notna().sum()
            if valid_count == 0:
                date_error = f"Could not parse dates in '{date_col}'. Try a different column or check your date format."
                validation_passed = False
            elif valid_count < len(df) * 0.8:
                date_error = f"Only {valid_count}/{len(df)} rows have valid dates. Some rows may be skipped."
            else:
                date_valid = True
        except Exception as e:
            date_error = f"Error parsing dates: {str(e)}"
            validation_passed = False

        # Validate value column
        if not pd.api.types.is_numeric_dtype(df[value_col]):
            try:
                pd.to_numeric(df[value_col], errors='raise')
                value_valid = True
            except Exception:
                value_error = f"'{value_col}' is not numeric. Please select a column with numbers."
                validation_passed = False
        else:
            value_valid = True

        # Check for duplicate column selection
        if date_col == value_col:
            st.error("⚠️ Date and Value columns must be different. Please select different columns.")
            validation_passed = False

        # Show validation messages
        if date_error:
            st.error(f"📅 {date_error}")
        if value_error:
            st.error(f"💰 {value_error}")

        # Data Preview with selected columns (only if different columns selected)
        st.markdown("---")
        st.markdown("**Preview of Selected Data** — <span style='color: #666; font-size: 13px;'>Does this look correct?</span>", unsafe_allow_html=True)

        if date_col != value_col:
            # Sort and prepare preview data
            try:
                df_preview = df[[date_col, value_col]].copy()
                if date_format:
                    df_preview[date_col] = pd.to_datetime(df_preview[date_col], format=date_format)
                else:
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        df_preview[date_col] = pd.to_datetime(df_preview[date_col])
                df_preview = df_preview.sort_values(date_col)
                df_preview = df_preview.dropna()

                # Format for display
                df_display = df_preview.head(5).copy()
                df_display[date_col] = df_display[date_col].dt.strftime('%d %b %Y')
                df_display[value_col] = df_display[value_col].apply(lambda x: f"€{x:,.2f}" if pd.notna(x) else "")

                st.dataframe(df_display, use_container_width=True, hide_index=True)
            except Exception:
                st.dataframe(df[[date_col, value_col]].head(5), use_container_width=True)
        else:
            st.info("Select different columns for Date and Value to see the preview.")

        # Model indicator
        n_months = len(df)
        if n_months >= 24:
            st.success(f"✓ {n_months} months detected — using full seasonal model")
        elif n_months >= 12:
            st.info(f"✓ {n_months} months detected — using trend model (24+ months needed for seasonal)")
        elif n_months >= 6:
            st.warning(f"⚠️ {n_months} months detected — basic trend model. More data recommended.")
        else:
            st.error(f"❌ Only {n_months} months — Minimum 6 months required")

        st.divider()

        # =====================================================================
        # STEP 2: FORECAST SETTINGS
        # =====================================================================
        st.markdown('<p class="section-title">Step 2: Forecast Settings</p>', unsafe_allow_html=True)

        # Forecast period slider
        forecast_months = st.slider(
            "Forecast Period (months)",
            min_value=1,
            max_value=12,
            value=st.session_state.forecast_months,
            help="Number of months to forecast into the future"
        )
        st.session_state.forecast_months = forecast_months

        st.divider()

        # =====================================================================
        # STEP 3: GENERATE
        # =====================================================================
        st.markdown('<p class="section-title">Step 3: Generate Forecast</p>', unsafe_allow_html=True)

        # Generate button (disabled if validation failed)
        generate_clicked = st.button(
            "Generate Forecast",
            type="primary",
            use_container_width=True,
            disabled=not validation_passed
        )

        if not validation_passed:
            st.caption("Please fix the errors above before generating a forecast.")

        if generate_clicked and validation_passed:
            with st.spinner("Generating forecast..."):
                # Prepare time series
                time_series = prepare_time_series(df, date_col, value_col)

                # Generate forecast
                forecast, model, error = generate_forecast(time_series, forecast_months)

                if error:
                    st.error(f"❌ {error}")
                else:
                    # Store results
                    st.session_state.time_series = time_series
                    st.session_state.forecast = forecast
                    st.session_state.model = model
                    st.session_state.forecast_generated = True
                    st.rerun()

        # =====================================================================
        # STEP 4: RESULTS (appears after generation)
        # =====================================================================
        if st.session_state.forecast_generated and 'time_series' in st.session_state:
            st.divider()

            st.markdown('<p class="section-title">Step 4: Results</p>', unsafe_allow_html=True)

            time_series = st.session_state.time_series
            forecast = st.session_state.forecast
            value_col_display = st.session_state.value_col

            # Calculate metrics
            metrics = calculate_metrics(time_series, forecast)

            # Chart
            fig = create_forecast_chart(time_series, forecast, value_col_display)
            st.plotly_chart(fig, use_container_width=True)

            # Metrics Display
            st.markdown("**Key Metrics**")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Historical Avg", f"€{metrics['historical_avg']:,.0f}")
            with col2:
                st.metric("Forecast Avg", f"€{metrics['forecast_avg']:,.0f}")
            with col3:
                st.metric("Projected Growth", f"{metrics['growth_rate']:+.1f}%")

            # Downloads
            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                csv_data = create_download_csv(time_series, forecast, value_col_display)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"forecast_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with col2:
                try:
                    fig_pdf = create_forecast_chart(time_series, forecast, value_col_display)
                    pdf_data = create_pdf_report(time_series, forecast, value_col_display, metrics, fig_pdf)
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_data,
                        file_name=f"forecast_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.warning(f"PDF generation unavailable: {str(e)}")

    # Footer
    st.markdown("""
    <div class="app-footer">
        Powered by local AI · Your data stays private
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
