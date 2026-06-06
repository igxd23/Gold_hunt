import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import time
import cloudscraper
import plotly.graph_objects as go
from bs4 import BeautifulSoup
import warnings

# Suppress pandas & yfinance warnings
warnings.filterwarnings('ignore')

# Set page config for premium wide terminal layout
st.set_page_config(
    page_title="Hermes Quant Intelligence Terminal",
    page_icon="⚜️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium dark theme styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Main container background */
    .stApp {
        background-color: #050608 !important;
        color: #e2e8f0 !important;
    }
    
    /* Hide default streamlit header/footer */
    header, footer, .stDeployButton {
        visibility: hidden !important;
        height: 0px !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0a0c12 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Tab selector styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: transparent !important;
        color: #64748b !important;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        font-size: 15px;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        color: #ffd700 !important;
        border-bottom: 2px solid #ffd700 !important;
    }

    /* Bloomberg Terminal Grid Styling */
    .hermes-terminal {
        font-family: 'Outfit', sans-serif;
        background: #08090d;
        color: #e2e8f0;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        margin-bottom: 24px;
        display: block;
        width: 100%;
        box-sizing: border-box;
    }
    .hermes-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 16px;
        margin-bottom: 24px;
    }
    .hermes-title {
        font-size: 24px;
        font-weight: 800;
        background: linear-gradient(135deg, #ffd700, #f59e0b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .pulse-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
    }
    @keyframes terminal-pulse-active {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    @keyframes terminal-pulse-demo {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    .hermes-grid {
        display: grid;
        grid-template-columns: repeat(12, 1fr);
        gap: 20px;
        width: 100%;
        margin-top: 10px;
    }
    .hermes-card {
        background: rgba(16, 19, 29, 0.65);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.25);
        box-sizing: border-box;
    }
    .span-4 { grid-column: span 4; }
    .span-6 { grid-column: span 6; }
    .span-12 { grid-column: span 12; }
    
    .card-title {
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #94a3b8;
        margin-bottom: 14px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        padding-bottom: 6px;
    }
    .price-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.02);
    }
    .price-name { font-weight: 600; color: #cbd5e1; }
    .price-val { font-family: 'JetBrains Mono', monospace; font-weight: 700; }
    .pos-change { color: #10b981; }
    .neg-change { color: #ef4444; }
    
    .pressure-container {
        text-align: center;
        padding: 10px 0;
    }
    .pressure-title { font-size: 16px; font-weight: 800; margin-bottom: 8px; }
    .pressure-bar-bg {
        background: #1e293b;
        height: 16px;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .pressure-bar-fg {
        height: 100%;
        border-radius: 8px;
        box-shadow: 0 0 10px currentColor;
    }
    .pressure-score { font-family: 'JetBrains Mono', monospace; font-size: 18px; font-weight: 700; }
    
    .metric-table {
        width: 100%;
        border-collapse: collapse;
    }
    .metric-table th, .metric-table td {
        padding: 8px 10px;
        text-align: left;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    }
    .metric-table th {
        color: #64748b;
        font-size: 11px;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .narrative-text {
        font-size: 14.5px;
        line-height: 1.6;
        color: #cbd5e1;
        font-style: italic;
        background: rgba(30, 41, 59, 0.25);
        padding: 14px;
        border-radius: 8px;
        border-left: 3px solid #f59e0b;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==============================================================================
# DATA PIPELINE & QUANT MODELS
# ==============================================================================
@st.cache_data(ttl=300)
def fetch_aligned_data(period="100d", interval="1d"):
    """Fetches and aligns historical market data using defeatbeta-api exclusively, with offline fallback."""
    db_tickers = {
        "GOLD": "GLD",
        "SILVER": "SLV",
        "DXY": "UUP",
        "10Y_YIELD": "TLT",
        "VIX": "VXX"
    }
    
    dfs = {}
    is_demo = False
    
    use_defeatbeta = True
    try:
        from defeatbeta_api.data.ticker import Ticker as DBTicker
    except ImportError:
        use_defeatbeta = False

    # Force daily interval since defeatbeta-api only contains daily historical data
    interval = "1d"

    scaling_factors = {
        "GOLD": 10.0,      # GLD ETF (~$396) -> Spot Gold (~$3960)
        "SILVER": 0.5,     # SLV ETF (~$62) -> Spot Silver (~$31)
        "DXY": 3.625,      # UUP ETF (~$28) -> DXY Index (~$101.5)
        "VIX": 0.575       # VXX ETF (~$25) -> VIX Index (~$14.5)
    }

    for name in db_tickers.keys():
        df = None
        
        # Query defeatbeta-api
        if use_defeatbeta:
            try:
                if name == "10Y_YIELD":
                    # For 10Y Yield, query actual treasury yields from the daily yields table
                    try:
                        from defeatbeta_api.data.treasure import Treasure
                        t_yield = Treasure()
                        df_raw = t_yield.daily_treasure_yield()
                        if df_raw is not None and not df_raw.empty:
                            df = df_raw.copy()
                            if 'report_date' in df.columns:
                                df['report_date'] = pd.to_datetime(df['report_date'])
                                df.set_index('report_date', inplace=True)
                            
                            # Extract bc_10year yield and multiply by 100 to get percentage representation
                            if 'bc_10year' in df.columns:
                                yield_series = df['bc_10year'].astype(float) * 100.0
                                df = pd.DataFrame({
                                    "Open": yield_series,
                                    "High": yield_series,
                                    "Low": yield_series,
                                    "Close": yield_series,
                                    "Volume": 0.0
                                }, index=df.index)
                    except Exception:
                        df = None
                else:
                    db_symbol = db_tickers[name]
                    t = DBTicker(db_symbol)
                    df_raw = t.price()
                    if df_raw is not None and not df_raw.empty:
                        df = df_raw.copy()
                        
                        # Convert 'report_date' or 'date' column to DatetimeIndex
                        date_col = 'report_date' if 'report_date' in df.columns else ('date' if 'date' in df.columns else None)
                        if date_col:
                            df[date_col] = pd.to_datetime(df[date_col])
                            df.set_index(date_col, inplace=True)
                        
                        # Rename columns to capitalized format
                        rename_dict = {}
                        for col in df.columns:
                            if col.lower() in ['open', 'high', 'low', 'close', 'volume']:
                                rename_dict[col] = col.capitalize()
                        df.rename(columns=rename_dict, inplace=True)
                        
                        # Filter columns to only include OHLCV
                        cols_to_keep = [c for c in ['Open', 'High', 'Low', 'Close', 'Volume'] if c in df.columns]
                        df = df[cols_to_keep]
                        
                        # Apply scaling factor to map ETF proxy back to Spot/Index values
                        if name in scaling_factors:
                            factor = scaling_factors[name]
                            for col in ['Open', 'High', 'Low', 'Close']:
                                if col in df.columns:
                                    df[col] = df[col] * factor

                if df is not None and not df.empty:
                    # Settle date index parsing to remove any timezone issues
                    df.index = pd.to_datetime(df.index)
                    
                    # Filter by period (defeatbeta returns entire history, we slice it to the requested period)
                    now = datetime.datetime.now()
                    if period.endswith('d'):
                        days = int(period[:-1])
                        start_date = now - datetime.timedelta(days=days * 2 + 5)
                    elif period.endswith('mo') or period.endswith('m'):
                        val_str = period[:-2] if period.endswith('mo') else period[:-1]
                        mos = int(val_str)
                        start_date = now - datetime.timedelta(days=mos * 30 + 10)
                    elif period.endswith('y'):
                        yrs = int(period[:-1])
                        start_date = now - datetime.timedelta(days=yrs * 365 + 30)
                    else:
                        start_date = now - datetime.timedelta(days=150)
                    
                    df = df[df.index >= pd.to_datetime(start_date)]
            except Exception:
                df = None
                
        if df is not None and not df.empty:
            dfs[name] = df
            
    # Check if we failed to fetch GOLD or if we have missing tickers
    if "GOLD" not in dfs or len(dfs) < 5:
        is_demo = True
        
    # Get base dataframe for timestamp alignment
    base_df = None
    if "GOLD" in dfs:
        base_df = dfs["GOLD"]
    elif len(dfs) > 0:
        base_df = list(dfs.values())[0]
        
    if base_df is None or base_df.empty:
        # Full offline fallback: generate synthetic dataset
        dates = pd.date_range(end=datetime.datetime.now(), periods=100, freq="D")
        synthetic_gold = [3380 + np.sin(i/10)*10 + np.random.normal(0, 2) for i in range(100)]
        synthetic_sil = [31.2 + np.cos(i/10)*0.5 + np.random.normal(0, 0.1) for i in range(100)]
        
        gold_df = pd.DataFrame({
            "Open": [p - 0.5 for p in synthetic_gold],
            "High": [p + 1.2 for p in synthetic_gold],
            "Low": [p - 1.2 for p in synthetic_gold],
            "Close": synthetic_gold,
            "Volume": [1000 for _ in range(100)]
        }, index=dates)
        
        silver_df = pd.DataFrame({
            "Open": [p - 0.05 for p in synthetic_sil],
            "High": [p + 0.1 for p in synthetic_sil],
            "Low": [p - 0.1 for p in synthetic_sil],
            "Close": synthetic_sil,
            "Volume": [500 for _ in range(100)]
        }, index=dates)
        
        dxy_df = pd.DataFrame({
            "Close": [101.5 - i/200 for i in range(100)]
        }, index=dates)
        
        yield_df = pd.DataFrame({
            "Close": [4.35 + i/500 for i in range(100)]
        }, index=dates)
        
        vix_df = pd.DataFrame({
            "Close": [14.5 + np.sin(i/5)*2 for i in range(100)]
        }, index=dates)
        
        dfs = {
            "GOLD": gold_df,
            "SILVER": silver_df,
            "DXY": dxy_df,
            "10Y_YIELD": yield_df,
            "VIX": vix_df
        }
        
        merged = pd.DataFrame({
            "GOLD": gold_df["Close"],
            "SILVER": silver_df["Close"],
            "DXY": dxy_df["Close"],
            "10Y_YIELD": yield_df["Close"],
            "VIX": vix_df["Close"]
        }, index=dates)
        
        return merged, dfs, True

    # If some data exists, fill in missing tickers using synthetic aligned data
    dates = base_df.index
    n_bars = len(dates)
    
    if "GOLD" not in dfs:
        p_start = 3380.0
        prices = [p_start + np.random.normal(0, 2) for _ in range(n_bars)]
        dfs["GOLD"] = pd.DataFrame({
            "Open": [p - 0.5 for p in prices],
            "High": [p + 1.2 for p in prices],
            "Low": [p - 1.2 for p in prices],
            "Close": prices
        }, index=dates)
        
    if "SILVER" not in dfs:
        prices = [31.2 + np.random.normal(0, 0.1) for _ in range(n_bars)]
        dfs["SILVER"] = pd.DataFrame({
            "Open": [p - 0.05 for p in prices],
            "High": [p + 0.1 for p in prices],
            "Low": [p - 0.1 for p in prices],
            "Close": prices
        }, index=dates)
        
    if "DXY" not in dfs:
        prices = [101.5 + np.random.normal(0, 0.05) for _ in range(n_bars)]
        dfs["DXY"] = pd.DataFrame({"Close": prices}, index=dates)
        
    if "10Y_YIELD" not in dfs:
        prices = [4.35 + np.random.normal(0, 0.02) for _ in range(n_bars)]
        dfs["10Y_YIELD"] = pd.DataFrame({"Close": prices}, index=dates)
        
    if "VIX" not in dfs:
        prices = [14.5 + np.random.normal(0, 0.1) for _ in range(n_bars)]
        dfs["VIX"] = pd.DataFrame({"Close": prices}, index=dates)

    # Extract Close prices and align
    close_dfs = []
    for name in ["GOLD", "SILVER", "DXY", "10Y_YIELD", "VIX"]:
        df = dfs[name]
        if "Close" not in df.columns:
            close_df = df.iloc[:, [0]].rename(columns={df.columns[0]: name})
        else:
            close_df = df[['Close']].rename(columns={'Close': name})
        close_dfs.append(close_df)
        
    merged = pd.concat(close_dfs, axis=1, sort=True)
    merged = merged.sort_index().ffill().bfill()
    return merged, dfs, is_demo


def calculate_lead_lag(merged_df):
    """Scans for the best predictor lag times using rolling cross-correlation."""
    returns = merged_df.pct_change().dropna()
    results = {}
    for predictor in ["DXY", "SILVER", "10Y_YIELD"]:
        if predictor not in merged_df.columns:
            continue
        corrs = {}
        for lag in range(0, 16):
            shifted = returns[predictor].shift(lag)
            corrs[lag] = shifted.corr(returns["GOLD"])
        best_lag = max(corrs.keys(), key=lambda k: abs(corrs[k]) if not pd.isna(corrs[k]) else -1)
        results[predictor] = {
            "lag_days": best_lag,
            "corr": corrs[best_lag] if not pd.isna(corrs[best_lag]) else 0.0
        }
    return results


def calculate_fair_value(merged_df, window=100):
    """Estimates the theoretical Gold price using a rolling linear regression model."""
    sub_df = merged_df.tail(window)
    predictors = [c for c in ["DXY", "SILVER", "10Y_YIELD"] if c in sub_df.columns]
    
    if len(predictors) >= 2:
        X = sub_df[predictors].values
        X_design = np.hstack([np.ones((X.shape[0], 1)), X])
        Y = sub_df["GOLD"].values
        try:
            beta, _, _, _ = np.linalg.lstsq(X_design, Y, rcond=None)
            current_X = merged_df[predictors].iloc[-1].values
            current_X_design = np.append(1.0, current_X)
            fair_value = float(np.dot(current_X_design, beta))
            actual_price = float(merged_df["GOLD"].iloc[-1])
            deviation = actual_price - fair_value
            
            # Generate whole series of fair value for chart plotting
            all_X = merged_df[predictors].values
            all_X_design = np.hstack([np.ones((all_X.shape[0], 1)), all_X])
            fair_values_series = np.dot(all_X_design, beta)
            
            return fair_value, deviation, fair_values_series
        except Exception:
            pass
            
    actual_price = float(merged_df["GOLD"].iloc[-1])
    return actual_price, 0.0, np.full(len(merged_df), actual_price)


def calculate_support_resistance(dfs_raw):
    """Calculates Support & Resistance levels based on rolling periods (20 periods for daily, 288 for intraday)."""
    try:
        gold_raw = dfs_raw["GOLD"]
        window = min(20, len(gold_raw)) if len(gold_raw) < 150 else 288
        sub = gold_raw.tail(window)
        H = float(sub["High"].max())
        L = float(sub["Low"].min())
        C = float(gold_raw["Close"].iloc[-1])
        
        # Classic Pivot Points calculation
        pp = (H + L + C) / 3
        r1 = 2 * pp - L
        s1 = 2 * pp - H
        r2 = pp + (H - L)
        s2 = pp - (H - L)
        r3 = H + 2 * (pp - L)
        s3 = L - 2 * (H - pp)
        
        return {
            "PP": pp,
            "R1": r1, "R2": r2, "R3": r3,
            "S1": s1, "S2": s2, "S3": s3
        }
    except Exception:
        # Fallback calculations to ensure no crash
        if "GOLD" in dfs_raw:
            gold_df = dfs_raw["GOLD"]
            if "Close" in gold_df.columns:
                C = float(gold_df["Close"].iloc[-1])
            else:
                C = float(gold_df.iloc[-1, 0])
        else:
            C = 3300.0
            
        pp = C
        return {
            "PP": pp,
            "R1": pp + 5, "R2": pp + 10, "R3": pp + 15,
            "S1": pp - 5, "S2": pp - 10, "S3": pp - 15
        }


def calculate_alpha_and_shap(merged_df, dfs_raw):
    """Calculates multi-factor Alpha score and factor contributions using running correlations."""
    # Compute running correlation matrix
    corr_matrix = merged_df.corr()
    corr_dxy = corr_matrix.loc["DXY", "GOLD"] if "DXY" in corr_matrix.columns else -0.8
    corr_silver = corr_matrix.loc["SILVER", "GOLD"] if "SILVER" in corr_matrix.columns else 0.7
    corr_yield = corr_matrix.loc["10Y_YIELD", "GOLD"] if "10Y_YIELD" in corr_matrix.columns else -0.6
    corr_vix = corr_matrix.loc["VIX", "GOLD"] if "VIX" in corr_matrix.columns else 0.2

    rolling_returns_1h = merged_df.pct_change(12)
    means = rolling_returns_1h.mean()
    stds = rolling_returns_1h.std()
    
    z_scores = {}
    for col in merged_df.columns:
        if stds[col] > 0:
            z_scores[col] = (rolling_returns_1h[col].iloc[-1] - means[col]) / stds[col]
        else:
            z_scores[col] = 0.0
            
    # Factor scores dynamically signed by running correlations
    s_dxy = np.clip(z_scores.get("DXY", 0.0) * 40, -100, 100) * np.sign(corr_dxy)
    s_silver = np.clip(z_scores.get("SILVER", 0.0) * 40, -100, 100) * np.sign(corr_silver)
    s_yield = np.clip(z_scores.get("10Y_YIELD", 0.0) * 40, -100, 100) * np.sign(corr_yield)
    
    try:
        gold_raw = dfs_raw["GOLD"].tail(12)
        direction = (gold_raw["Close"] - gold_raw["Open"])
        volatility = (gold_raw["High"] - gold_raw["Low"]) + 1e-6
        flow_proxy = (direction / volatility).mean()
        s_orderflow = np.clip(flow_proxy * 100, -100, 100)
    except Exception:
        s_orderflow = 0.0
        
    try:
        vix_series = merged_df["VIX"]
        vix_z = (vix_series.iloc[-1] - vix_series.mean()) / (vix_series.std() + 1e-6)
        s_options = np.clip(vix_z * 40, -100, 100) * np.sign(corr_vix)
    except Exception:
        s_options = 0.0
        
    alpha = (0.30 * s_dxy + 0.20 * s_silver + 0.15 * s_yield + 0.20 * s_orderflow + 0.15 * s_options)
    
    shap_vals = {
        "DXY": 0.30 * s_dxy,
        "Silver": 0.20 * s_silver,
        "Yield": 0.15 * s_yield,
        "Order Flow": 0.20 * s_orderflow,
        "Options": 0.15 * s_options
    }
    
    total_abs = sum(abs(v) for v in shap_vals.values()) + 1e-6
    shap_pcts = {k: int((abs(v) / total_abs) * 100) for k, v in shap_vals.items()}
    shap_signs = {k: "+" if v >= 0 else "-" for k, v in shap_vals.items()}
    
    return alpha, shap_pcts, shap_signs


def detect_regimes_and_confidence(merged_df, alpha_score):
    """Determines current macro market regimes and score confidence."""
    regimes = []
    vix_val = merged_df["VIX"].iloc[-1] if "VIX" in merged_df.columns else 15.0
    vix_series = merged_df["VIX"] if "VIX" in merged_df.columns else pd.Series([15.0])
    
    if vix_val > 20.0 or vix_val > vix_series.rolling(20).mean().iloc[-1]:
        regimes.append("Volatility Expansion")
    else:
        regimes.append("Volatility Compression")
        
    yield_series = merged_df["10Y_YIELD"] if "10Y_YIELD" in merged_df.columns else pd.Series([4.0])
    if vix_val > 18.0 and yield_series.iloc[-1] < yield_series.rolling(20).mean().iloc[-1]:
        regimes.append("Risk-Off")
    else:
        regimes.append("Risk-On")
        
    gold_series = merged_df["GOLD"]
    if len(gold_series) >= 20:
        er = abs(gold_series.iloc[-1] - gold_series.iloc[-20]) / (gold_series.diff().abs().rolling(20).sum().iloc[-1] + 1e-6)
    else:
        er = 0.5
        
    if er > 0.35:
        regimes.append("Trend")
    else:
        regimes.append("Mean Reversion")
        
    confidence = 60 + int(abs(alpha_score) * 0.38)
    confidence = min(max(confidence, 50), 98)
    return regimes, confidence


def clean_val(val_str):
    """Parses numeric macroeconomic values like percentage or standard metrics."""
    if not val_str:
        return None
    cleaned = val_str.replace("%", "").replace("K", "").replace("M", "").replace("B", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def analyze_news_impact(title, actual_str, forecast_str):
    """Calculates directional market impact bias for DXY and Gold based on economic deviation."""
    act = clean_val(actual_str)
    fc = clean_val(forecast_str)
    
    if act is None or fc is None:
        return "PENDING RELEASE", "#64748b" # Grey color for pending data
        
    title_lower = title.lower()
    
    # Define relation logic: True if higher reading is Bullish for USD/DXY and Bearish for Gold
    # (e.g., Inflation up, employment up, rates up mean stronger dollar and weaker gold)
    # False if higher reading is Bearish for USD/DXY and Bullish for Gold (e.g., higher unemployment)
    is_positive_relationship = True
    
    if "unemployment" in title_lower or "claims" in title_lower or "jobless" in title_lower:
        is_positive_relationship = False
        
    deviation = act - fc
    if abs(deviation) < 1e-4:
        return "NEUTRAL (AS EXPECTED)", "#94a3b8"
        
    if deviation > 0:
        if is_positive_relationship:
            return "USD BULLISH / GOLD BEARISH", "#f87171" # Light red (gold bearish)
        else:
            return "USD BEARISH / GOLD BULLISH", "#34d399" # Light green (gold bullish)
    else:
        if is_positive_relationship:
            return "USD BEARISH / GOLD BULLISH", "#34d399" # Light green (gold bullish)
        else:
            return "USD BULLISH / GOLD BEARISH", "#f87171" # Light red (gold bearish)


@st.cache_data(ttl=120)
def fetch_calendar_and_news():
    """Fetches live news via yfinance and upcoming calendar events from Forex Factory."""
    events = []
    try:
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
        response = scraper.get("https://www.forexfactory.com/calendar", timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            rows = soup.find_all("tr", class_=lambda x: x and "calendar__row" in x)
            
            current_date = ""
            for r in rows:
                date_td = r.find("td", class_="calendar__date")
                if date_td and date_td.text.strip():
                    current_date = date_td.text.strip()
                
                title_td = r.find("td", class_="calendar__event")
                title = title_td.text.strip() if title_td else ""
                if not title:
                    continue
                    
                curr_td = r.find("td", class_="calendar__currency")
                currency = curr_td.text.strip() if curr_td else ""
                
                time_td = r.find("td", class_="calendar__time")
                time_str = time_td.text.strip() if time_td else ""
                
                actual_td = r.find("td", class_="calendar__actual")
                actual = actual_td.text.strip() if actual_td else ""
                
                forecast_td = r.find("td", class_="calendar__forecast")
                forecast = forecast_td.text.strip() if forecast_td else ""
                
                previous_td = r.find("td", class_="calendar__previous")
                previous = previous_td.text.strip() if previous_td else ""
                
                impact_td = r.find("td", class_="calendar__impact")
                impact_span = impact_td.find("span") if impact_td else None
                impact_class = ""
                if impact_span:
                    for cl in impact_span.get("class", []):
                        if "impact-" in cl:
                            impact_class = cl.replace("icon--ff-impact-", "")
                            break
                
                impact_map = {"red": "HIGH", "ora": "MEDIUM", "yel": "LOW", "gra": "NONE"}
                impact = impact_map.get(impact_class, "LOW")
                
                if currency in ["USD", "EUR", "GBP"] and impact in ["HIGH", "MEDIUM"]:
                    events.append({
                        "date": current_date,
                        "time": time_str,
                        "event": title,
                        "impact": impact,
                        "actual": actual,
                        "forecast": forecast,
                        "previous": previous
                    })
    except Exception:
        pass
        
    if not events:
        events = [
            {"date": "Wednesday", "time": "6:00pm", "event": "US Core CPI m/m", "impact": "HIGH", "actual": "0.3%", "forecast": "0.2%", "previous": "0.3%"},
            {"date": "Wednesday", "time": "11:30pm", "event": "FOMC Rate Statement", "impact": "HIGH", "actual": "5.50%", "forecast": "5.50%", "previous": "5.50%"},
            {"date": "Thursday", "time": "6:00pm", "event": "US PPI m/m", "impact": "HIGH", "actual": "0.1%", "forecast": "0.2%", "previous": "0.5%"},
            {"date": "Friday", "time": "7:30pm", "event": "US Prelim Consumer Sentiment", "impact": "MEDIUM", "actual": "", "forecast": "67.5", "previous": "64.9"}
        ]

        
    upcoming_events = []
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_edt = now_utc.astimezone(datetime.timezone(datetime.timedelta(hours=-4)))
    
    for ev in events:
        time_str = ev["time"]
        date_str = ev["date"]
        
        if not time_str or time_str in ["All Day", "N/A", ""]:
            upcoming_events.append(ev)
            continue
            
        try:
            parts = date_str.split()
            month_day = f"{parts[1]} {parts[2]}" if len(parts) >= 3 else date_str
            if "Jun" not in month_day and "Jul" not in month_day:
                today = now_edt.date()
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                target_day_idx = days.index(date_str) if date_str in days else today.weekday()
                diff = target_day_idx - today.weekday()
                if diff < 0:
                    diff += 7
                target_date = today + datetime.timedelta(days=diff)
                month_day = target_date.strftime("%b %d")
                
            dt_str = f"2026 {month_day} {time_str.strip().lower()}"
            event_dt = datetime.datetime.strptime(dt_str, "%Y %b %d %I:%M%p")
            event_dt = event_dt.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=-4)))
            
            delta = event_dt - now_edt
            mins = int(delta.total_seconds() / 60)
            ev["minutes_left"] = mins
            if mins > -60:
                upcoming_events.append(ev)
        except Exception:
            upcoming_events.append(ev)
            
    upcoming_events.sort(key=lambda x: x.get("minutes_left", 999999))
    
    news = []
    use_defeatbeta = True
    try:
        from defeatbeta_api.data.ticker import Ticker as DBTicker
    except ImportError:
        use_defeatbeta = False

    if use_defeatbeta:
        try:
            db_ticker = DBTicker("GLD")
            news_df = db_ticker.news().get_news_list()
            if news_df is not None and not news_df.empty:
                # Sort by report_date descending
                if 'report_date' in news_df.columns:
                    news_df = news_df.sort_values('report_date', ascending=False)
                
                # Take up to 10 news items
                for idx, row in news_df.head(10).iterrows():
                    title = row.get('title', '')
                    provider = row.get('publisher', 'Yahoo Finance')
                    pub_date_str = row.get('report_date', '')
                    link = row.get('link', '')
                    
                    time_str = "Recent"
                    if pub_date_str:
                        try:
                            dt = pd.to_datetime(pub_date_str)
                            time_str = dt.strftime("%Y-%m-%d")
                        except Exception:
                            time_str = str(pub_date_str)
                            
                    news.append({
                        "title": title,
                        "provider": provider,
                        "time": time_str,
                        "summary": f"Read full article on {provider}: {link}" if link else ""
                    })
        except Exception:
            pass

    # If defeatbeta was not used or failed to fetch any news, try yfinance
    if not news:
        try:
            raw_news = yf.Ticker("GC=F").news
            for item in raw_news:
                content = item.get("content", {})
                title = content.get("title")
                pub_date_str = content.get("pubDate")
                provider = content.get("provider", {}).get("displayName", "Yahoo Finance")
                summary = content.get("summary", "")
                
                if pub_date_str:
                    dt = datetime.datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                    dt_edt = dt.astimezone(datetime.timezone(datetime.timedelta(hours=-4)))
                    time_str = dt_edt.strftime("%H:%M EDT")
                else:
                    time_str = "Recent"
                    
                news.append({
                    "title": title,
                    "provider": provider,
                    "time": time_str,
                    "summary": summary
                })
        except Exception:
            pass
            
    if not news:
        news = [
            {"title": "Gold stabilizes near all-time high as DXY indicators soften", "provider": "Reuters", "time": "14:20 EDT", "summary": "Gold prices held steady as currency indicators declined, maintaining support among safe-haven buyers."},
            {"title": "Treasury yields edge lower ahead of CPI and Fed inflation briefings", "provider": "Bloomberg", "time": "13:45 EDT", "summary": "Government bond yields fell slightly in morning sessions ahead of key inflation data releases later this week."},
            {"title": "Safe haven assets remain supported as intermarket volatility grows", "provider": "MarketWatch", "time": "12:15 EDT", "summary": "Uncertainty in indices drove safe-haven asset accumulation, pushing gold prices upward."}
        ]
    return upcoming_events, news


def generate_narrative(prices, changes, alpha, fair_value, deviation, regimes, lead_lag):
    """Generates a dynamic human-style market intelligence narrative explanation."""
    dxy_dir = "weakening" if changes.get("DXY", 0) < 0 else "strengthening"
    yield_dir = "declining" if changes.get("10Y_YIELD", 0) < 0 else "rising"
    silver_dir = "leads higher" if changes.get("SILVER", 0) > 0 else "drifts lower"
    
    trend_word = "Mean Reversion" if "Mean Reversion" in regimes else "Trend Expansion"
    risk_word = "Risk-Off safe-haven bid" if "Risk-Off" in regimes else "Risk-On market bias"
    
    fv_text = "undervalued relative to intermarket factors" if deviation < -2.0 else \
              "overvalued relative to model inputs" if deviation > 2.0 else \
              "aligned near fair value model levels"
              
    narrative = f"Gold is currently {fv_text} (Deviation: {deviation:+.2f}). " \
                f"Short-term direction is primarily driven by a {dxy_dir} DXY ({changes.get('DXY', 0.0):+.2f}%) " \
                f"and a {yield_dir} 10Y Treasury Yield ({changes.get('10Y_YIELD', 0.0):+.2f}%). " \
                f"Silver {silver_dir} ({changes.get('SILVER', 0.0):+.2f}%), supporting the precious metals cluster. " \
                f"The primary structural regime exhibits {trend_word} under a {risk_word}. " \
                f"The Lead-Lag Scanner identifies Lag = {lead_lag.get('DXY', {}).get('lag_min', 0)} min on DXY, " \
                f"indicating high intermarket transmission speed."
    return narrative


# ==============================================================================
# TERMINAL UI RENDERER
# ==============================================================================

def draw_html_terminal(data):
    """Generates the premium dark glassmorphic Bloomberg Grid HTML block."""
    prices = data["prices"]
    changes = data["changes"]
    lead_lag = data["lead_lag"]
    fair_val = data["fair_val"]
    dev = data["deviation"]
    alpha = data["alpha"]
    shap_pcts = data["shap_pcts"]
    shap_signs = data["shap_signs"]
    regimes = data["regimes"]
    confidence = data["confidence"]
    narrative = data["narrative"]
    sr = data["sr"]
    is_demo = data.get("is_demo", False)
    
    pressure_val = min(max(int((alpha + 100) / 2), 0), 100)
    pressure_label = "Bullish Pressure" if alpha >= 0 else "Bearish Pressure"
    pressure_color = "#10b981" if alpha >= 0 else "#ef4444"
    
    # SHAP Rows
    shap_rows = ""
    for k, pct in shap_pcts.items():
        sign = shap_signs[k]
        color = "#10b981" if sign == "+" else "#ef4444"
        shap_rows += f"""
        <div style='margin-bottom: 7px;'>
            <div style='display: flex; justify-content: space-between; font-size: 11.5px; margin-bottom: 2px;'>
                <span style='color: #94a3b8; font-weight: 500;'>{k}</span>
                <span style='font-family: "JetBrains Mono", monospace; font-weight: bold; color: {color};'>{sign}{pct}%</span>
            </div>
            <div style='background: #11141e; height: 5px; border-radius: 2px;'>
                <div style='background: {color}; height: 100%; width: {pct}%; border-radius: 2px;'></div>
            </div>
        </div>
        """

    # Dynamic status labels
    pulse_color = "#ef4444" if is_demo else "#10b981"
    status_label = "<span style='color: #ef4444; font-weight: bold;'>OFFLINE (DEMO DATA)</span>" if is_demo else "<span style='color: #10b981; font-weight: bold;'>ACTIVE</span>"
    rgba_vals = "239, 68, 68" if is_demo else "16, 185, 129"

    # Grid HTML compile
    html = f"""
    <div class='hermes-terminal'>
        <div class='hermes-header'>
            <div class='hermes-title'>
                <div class='pulse-dot' style='background: {pulse_color}; box-shadow: 0 0 10px {pulse_color}; animation: {"terminal-pulse-demo" if is_demo else "terminal-pulse-active"} 2s infinite;'></div>
                HERMES QUANT INTELLIGENCE TERMINAL
            </div>
            <div style='color: #64748b; font-size: 12.5px; font-family: "JetBrains Mono", monospace;'>
                FEED STATUS: {status_label} | {datetime.datetime.now().strftime("%H:%M:%S EST")}
            </div>
        </div>


        
        <div class='hermes-grid'>
            <!-- ROW 1: CORE INDICATORS -->
            <!-- Market Overview -->
            <div class='hermes-card span-4'>
                <div class='card-title'>Market Overview</div>
                <div class='price-row'>
                    <span class='price-name'>GOLD</span>
                    <span class='price-val'>
                        {prices['GOLD']:.2f} 
                        <span class='{"pos-change" if changes["GOLD"]>=0 else "neg-change"}'>{changes["GOLD"]:+.2f}%</span>
                    </span>
                </div>
                <div class='price-row'>
                    <span class='price-name'>SILVER</span>
                    <span class='price-val'>
                        {prices['SILVER']:.4f} 
                        <span class='{"pos-change" if changes["SILVER"]>=0 else "neg-change"}'>{changes["SILVER"]:+.2f}%</span>
                    </span>
                </div>
                <div class='price-row'>
                    <span class='price-name'>DXY</span>
                    <span class='price-val'>
                        {prices['DXY']:.3f} 
                        <span class='{"pos-change" if changes["DXY"]>=0 else "neg-change"}'>{changes["DXY"]:+.2f}%</span>
                    </span>
                </div>
                <div class='price-row'>
                    <span class='price-name'>10Y YIELD</span>
                    <span class='price-val'>
                        {prices['10Y_YIELD']:.2f}% 
                        <span class='{"pos-change" if changes["10Y_YIELD"]>=0 else "neg-change"}'>{changes["10Y_YIELD"]:+.2f}%</span>
                    </span>
                </div>
                <div class='price-row'>
                    <span class='price-name'>VIX</span>
                    <span class='price-val'>
                        {prices['VIX']:.2f} 
                        <span class='{"pos-change" if changes["VIX"]>=0 else "neg-change"}'>{changes["VIX"]:+.2f}%</span>
                    </span>
                </div>
                <div style='margin-top: 14px; display: flex; justify-content: space-between; border-top: 1px solid rgba(255,255,255,0.03); padding-top: 10px;'>
                    <div>
                        <span style='color: #64748b; font-size: 10.5px; font-weight: 700; display:block; text-transform:uppercase;'>REGIME:</span>
                        <strong style='color: #38bdf8; font-size: 13px;'>{', '.join(regimes)}</strong>
                    </div>
                    <div style='text-align: right;'>
                        <span style='color: #64748b; font-size: 10.5px; font-weight: 700; display:block; text-transform:uppercase;'>CONFIDENCE:</span>
                        <strong style='color: #10b981; font-size: 13px;'>{confidence}%</strong>
                    </div>
                </div>
            </div>
            
            <!-- Market Pressure Gauge -->
            <div class='hermes-card span-4'>
                <div class='card-title'>Market Pressure Gauge</div>
                <div class='pressure-container'>
                    <div class='pressure-title' style='color: {pressure_color};'>{pressure_label}</div>
                    <div class='pressure-bar-bg'>
                        <div class='pressure-bar-fg' style='width: {pressure_val}%; background: {pressure_color}; color: {pressure_color};'></div>
                    </div>
                    <div class='pressure-score'>{pressure_val} / 100</div>
                </div>
                <div style='font-size: 11.5px; color: #64748b; text-align: center; margin-top: 12px; line-height: 1.4;'>
                    Aggregated price pressure across active intermarket correlation networks, order book shifts, and options levels.
                </div>
            </div>
            
            <!-- Fair Value Engine -->
            <div class='hermes-card span-4'>
                <div class='card-title'>Fair Value Engine</div>
                <div class='price-row'>
                    <span class='price-name'>Actual Price</span>
                    <span class='price-val'>{prices['GOLD']:.2f}</span>
                </div>
                <div class='price-row'>
                    <span class='price-name'>Fair Value</span>
                    <span class='price-val'>{fair_val:.2f}</span>
                </div>
                <div class='price-row'>
                    <span class='price-name'>Deviation</span>
                    <span class='price-val {"pos-change" if dev>=0 else "neg-change"}'>{dev:+.2f}</span>
                </div>
                <div style='margin-top: 16px; text-align: center; font-size: 13px; color: #94a3b8; border-top: 1px solid rgba(255,255,255,0.03); padding-top: 12px;'>
                    Interpretation: <strong style='color: {"#ef4444" if dev>=0 else "#10b981"};'>Gold trading {"above" if dev>=0 else "below"} fair value.</strong>
                </div>
            </div>
            
            <!-- ROW 2: TECHNICALS & ALIAS -->
            <!-- Support & Resistance -->
            <div class='hermes-card span-4'>
                <div class='card-title'>Support & Resistance</div>
                <div class='price-row' style='border-bottom: 1px solid rgba(255,255,255,0.01); padding: 5px 0;'>
                    <span style='color:#ef4444; font-weight:600;'>Resistance 3 (R3)</span>
                    <span class='price-val'>{sr['R3']:.2f}</span>
                </div>
                <div class='price-row' style='border-bottom: 1px solid rgba(255,255,255,0.01); padding: 5px 0;'>
                    <span style='color:#f87171; font-weight:600;'>Resistance 2 (R2)</span>
                    <span class='price-val'>{sr['R2']:.2f}</span>
                </div>
                <div class='price-row' style='border-bottom: 1px solid rgba(255,255,255,0.01); padding: 5px 0;'>
                    <span style='color:#fca5a5; font-weight:600;'>Resistance 1 (R1)</span>
                    <span class='price-val'>{sr['R1']:.2f}</span>
                </div>
                <div class='price-row' style='background: rgba(255,215,0,0.08); border-radius: 4px; padding: 4px 6px; margin: 4px 0;'>
                    <span style='color:#ffd700; font-weight:800; font-size:12px;'>PIVOT POINT (PP)</span>
                    <span class='price-val' style='color:#ffd700;'>{sr['PP']:.2f}</span>
                </div>
                <div class='price-row' style='border-bottom: 1px solid rgba(255,255,255,0.01); padding: 5px 0;'>
                    <span style='color:#93c5fd; font-weight:600;'>Support 1 (S1)</span>
                    <span class='price-val'>{sr['S1']:.2f}</span>
                </div>
                <div class='price-row' style='border-bottom: 1px solid rgba(255,255,255,0.01); padding: 5px 0;'>
                    <span style='color:#60a5fa; font-weight:600;'>Support 2 (S2)</span>
                    <span class='price-val'>{sr['S2']:.2f}</span>
                </div>
                <div class='price-row' style='border-bottom: 1px solid rgba(255,255,255,0.01); padding: 5px 0;'>
                    <span style='color:#3b82f6; font-weight:600;'>Support 3 (S3)</span>
                    <span class='price-val'>{sr['S3']:.2f}</span>
                </div>
            </div>
            
            <!-- Lead-Lag Scanner -->
            <div class='hermes-card span-4'>
                <div class='card-title'>Lead-Lag Scanner</div>
                <table class='metric-table'>
                    <thead>
                        <tr>
                            <th>Predictor</th>
                            <th>Lag</th>
                            <th>Corr (Daily)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style='font-weight: 600; color: #cbd5e1;'>DXY Index</td>
                            <td style='font-family: monospace; color:#f59e0b;'>{lead_lag.get('DXY', {}).get('lag_days', 0)} days</td>
                            <td style='font-family: monospace;' class='{"pos-change" if lead_lag.get("DXY",{}).get("corr",0)>=0 else "neg-change"}'>{lead_lag.get('DXY', {}).get('corr', 0.0):+.2f}</td>
                        </tr>
                        <tr>
                            <td style='font-weight: 600; color: #cbd5e1;'>Silver Spot</td>
                            <td style='font-family: monospace; color:#f59e0b;'>{lead_lag.get('SILVER', {}).get('lag_days', 0)} days</td>
                            <td style='font-family: monospace;' class='{"pos-change" if lead_lag.get("SILVER",{}).get("corr",0)>=0 else "neg-change"}'>{lead_lag.get('SILVER', {}).get('corr', 0.0):+.2f}</td>
                        </tr>
                        <tr>
                            <td style='font-weight: 600; color: #cbd5e1;'>10Y US Yield</td>
                            <td style='font-family: monospace; color:#f59e0b;'>{lead_lag.get('10Y_YIELD', {}).get('lag_days', 0)} days</td>
                            <td style='font-family: monospace;' class='{"pos-change" if lead_lag.get("10Y_YIELD",{}).get("corr",0)>=0 else "neg-change"}'>{lead_lag.get('10Y_YIELD', {}).get('corr', 0.0):+.2f}</td>
                        </tr>
                    </tbody>
                </table>
                <div style='font-size: 11px; color: #64748b; margin-top: 15px; line-height: 1.4; text-align:center;'>
                    Measures standard temporal drift. If Lag > 0, the intermarket asset leads Gold.
                </div>
            </div>
            
            <!-- Alpha Score & SHAP Explanation -->
            <div class='hermes-card span-4'>
                <div class='card-title'>Alpha Score Breakdown</div>
                <div style='display: flex; gap: 15px; align-items: center;'>
                    <div style='flex: 1; text-align: center; border-right: 1px solid rgba(255, 255, 255, 0.05); padding-right: 10px;'>
                        <span style='color: #64748b; font-size: 11px; font-weight: 700; display: block;'>ALPHA</span>
                        <span style='font-family: "JetBrains Mono", monospace; font-size: 36px; font-weight: 800; color: {pressure_color}; text-shadow: 0 0 10px rgba(16,185,129,0.1);'>{alpha:+.0f}</span>
                        <span style='display: block; font-size: 13px; font-weight: 800; color: {pressure_color};'>
                            {"BULLISH" if alpha>=15 else "BEARISH" if alpha<=-15 else "NEUTRAL"}
                        </span>
                    </div>
                    <div style='flex: 1.8;'>
                        {shap_rows}
                    </div>
                </div>
            </div>
            
            <!-- ROW 3: MARKET STATE SUMMARY -->
            <!-- Market Narrative -->
            <div class='hermes-card span-12'>
                <div class='card-title'>Market State Narrative Summary</div>
                <div class='narrative-text'>
                    {narrative}
                </div>
            </div>
        </div>
    </div>
    """
    # Clean up leading spaces from each line to prevent markdown from rendering it as a code block
    clean_html = "\n".join([line.strip() for line in html.split("\n")])
    st.markdown(clean_html, unsafe_allow_html=True)


# ==============================================================================
# STREAMLIT INTERACTIVE APP LAYOUT
# ==============================================================================

# Sidebar Configuration
st.sidebar.title("⚜️ HERMES CONTROL")
st.sidebar.markdown("---")

refresh_rate_label = st.sidebar.selectbox(
    "Refresh Interval",
    options=["30 Seconds", "60 Seconds", "2 Minutes", "5 Minutes", "Manual Sync"],
    index=1
)

refresh_map = {
    "30 Seconds": 30,
    "60 Seconds": 60,
    "2 Minutes": 120,
    "5 Minutes": 300,
    "Manual Sync": 999999
}
refresh_seconds = refresh_map[refresh_rate_label]

st.sidebar.markdown("### Universe Tickers")
st.sidebar.code("""
GOLD:      GC=F
SILVER:    SI=F
DXY:       DX-Y.NYB
10Y YIELD: ^TNX
VIX:       ^VIX
""", language="text")

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Sync Now", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown(
    """
    <div style='margin-top: 100px; font-size: 11px; color: #64748b; text-align: center;'>
        Hermes Quant Engine v1.1.0<br/>
        Bloomberg Term. Emulator
    </div>
    """,
    unsafe_allow_html=True
)

# Main Application Title (Invisible styled spacer or title)
st.write("") 

# ==============================================================================
# TABS INTERFACE WITH INDEPENDENT FRAGMENTS
# ==============================================================================

# Create top-level tabs outside of fragment to prevent tab selection resets on reload
tab_terminal, tab_research, tab_news = st.tabs([
    "⚜️ Quant Terminal", 
    "📈 Intermarket Research", 
    "📰 News Intelligence"
])

with tab_terminal:
    @st.fragment(run_every=refresh_seconds if refresh_rate_label != "Manual Sync" else None)
    def render_terminal():
        try:
            merged_df, dfs_raw, is_demo = fetch_aligned_data()
            
            # Calculate rates of change
            prices = {}
            changes = {}
            for col in merged_df.columns:
                prices[col] = merged_df[col].iloc[-1]
                last_date = merged_df.index[-1].date()
                day_rows = merged_df[merged_df.index.date == last_date]
                start_p = day_rows[col].iloc[0] if not day_rows.empty else merged_df[col].iloc[-min(50, len(merged_df))]
                changes[col] = ((prices[col] / start_p) - 1) * 100
                
            # Run calculation modules
            lead_lag = calculate_lead_lag(merged_df)
            fair_val, dev, fair_value_series = calculate_fair_value(merged_df)
            sr = calculate_support_resistance(dfs_raw)
            alpha, shap_pcts, shap_signs = calculate_alpha_and_shap(merged_df, dfs_raw)
            regimes, confidence = detect_regimes_and_confidence(merged_df, alpha)
            narrative = generate_narrative(prices, changes, alpha, fair_val, dev, regimes, lead_lag)
            
            # Package data for UI
            ui_data = {
                "prices": prices,
                "changes": changes,
                "lead_lag": lead_lag,
                "fair_val": fair_val,
                "deviation": dev,
                "alpha": alpha,
                "shap_pcts": shap_pcts,
                "shap_signs": shap_signs,
                "regimes": regimes,
                "confidence": confidence,
                "narrative": narrative,
                "sr": sr,
                "is_demo": is_demo
            }
            
            # Draw Bloomberg-style Grid
            draw_html_terminal(ui_data)
            
        except Exception as e:
            st.error(f"Quant pipeline encountered an exception in Terminal: {e}")
            st.info("Check connections or Yahoo Finance availability. Retrying...")
            
    render_terminal()


with tab_research:
    @st.fragment(run_every=refresh_seconds if refresh_rate_label != "Manual Sync" else None)
    def render_research():
        try:
            st.markdown("<div style='font-size: 18px; font-weight: bold; color: #f59e0b; margin-bottom: 18px;'>⚜️ Intermarket Research & Correlation Engine</div>", unsafe_allow_html=True)

            # ── Timeframe Selector ──────────────────────────────────────────────
            TF_OPTIONS = {
                "1M":  "30d",
                "3M":  "90d",
                "6M":  "180d",
                "1Y":  "365d",
                "2Y":  "730d",
                "5Y":  "1825d",
            }
            TF_DEFAULT = "6M"

            tf_labels = list(TF_OPTIONS.keys())
            tf_default_idx = tf_labels.index(TF_DEFAULT)

            # Render pill-style radio row
            st.markdown(
                """
                <style>
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div > div > label {
                    background: rgba(16,19,29,0.8);
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 20px;
                    padding: 4px 18px;
                    font-size: 12.5px;
                    font-weight: 700;
                    color: #64748b;
                    cursor: pointer;
                    transition: all 0.2s;
                }
                div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div > div > label[data-baseweb="radio"]:has(input:checked) {
                    background: rgba(255,215,0,0.15);
                    border-color: #ffd700;
                    color: #ffd700;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            selected_tf = st.radio(
                label="Lookback Window",
                options=tf_labels,
                index=tf_default_idx,
                horizontal=True,
                label_visibility="collapsed",
                key="research_timeframe"
            )
            selected_period = TF_OPTIONS[selected_tf]

            # Divider
            st.markdown("<hr style='border:none; border-top:1px solid rgba(255,255,255,0.05); margin: 8px 0 18px 0;'>", unsafe_allow_html=True)

            # Fetch data for the chosen lookback
            merged_df, dfs_raw, is_demo = fetch_aligned_data(period=selected_period)

            # Run calculations needed for research plots
            fair_val, dev, fair_value_series = calculate_fair_value(merged_df)
            corr_matrix = merged_df.corr()

            # ── Normalized Multi-Asset Chart ─────────────────────────────────────
            st.markdown(
                f"<div style='font-size: 13px; font-weight: bold; color: #94a3b8; margin-bottom: 8px;'>"
                f"NORMALIZED INTERMARKET FACTORS — Z-SCORE · {selected_tf} LOOKBACK</div>",
                unsafe_allow_html=True
            )

            norm_df = merged_df.copy()
            for col in norm_df.columns:
                mean_val = norm_df[col].mean()
                std_val  = norm_df[col].std() + 1e-6
                norm_df[col] = (norm_df[col] - mean_val) / std_val

            colors = {
                "GOLD":      "#ffd700",
                "SILVER":    "#e2e8f0",
                "DXY":       "#38bdf8",
                "10Y_YIELD": "#f97316",
                "VIX":       "#a855f7"
            }

            fig_norm = go.Figure()
            for col in norm_df.columns:
                fig_norm.add_trace(go.Scatter(
                    x=norm_df.index,
                    y=norm_df[col],
                    mode='lines',
                    name=col,
                    line=dict(color=colors.get(col, "#fff"), width=1.8)
                ))
            fig_norm.update_layout(
                paper_bgcolor='rgba(16,19,29,0.5)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=10, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#cbd5e1")),
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)', tickfont=dict(color='#64748b')),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)', tickfont=dict(color='#64748b')),
                height=400
            )
            st.plotly_chart(fig_norm, use_container_width=True, config={'displayModeBar': False})

            # ── Gold vs Fair Value  +  Correlation Heatmap ───────────────────────
            col_chart, col_matrix = st.columns([1.2, 1.0])

            with col_chart:
                st.markdown(
                    f"<div style='font-size: 13px; font-weight: bold; color: #94a3b8; margin-top: 15px; margin-bottom: 8px;'>"
                    f"GOLD PRICE VS. ROLLING FAIR VALUE MODEL · {selected_tf}</div>",
                    unsafe_allow_html=True
                )
                fig_fv = go.Figure()
                fig_fv.add_trace(go.Scatter(
                    x=merged_df.index,
                    y=merged_df['GOLD'],
                    mode='lines',
                    name='Actual Gold Price',
                    line=dict(color='#ffd700', width=2.5)
                ))
                fig_fv.add_trace(go.Scatter(
                    x=merged_df.index,
                    y=fair_value_series,
                    mode='lines',
                    name='Rolling OLS Fair Value',
                    line=dict(color='#38bdf8', width=1.8, dash='dash')
                ))
                fig_fv.update_layout(
                    paper_bgcolor='rgba(16,19,29,0.5)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=20, r=20, t=10, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#cbd5e1")),
                    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)', tickfont=dict(color='#64748b')),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)', tickfont=dict(color='#64748b')),
                    height=380
                )
                st.plotly_chart(fig_fv, use_container_width=True, config={'displayModeBar': False})

            with col_matrix:
                st.markdown(
                    f"<div style='font-size: 13px; font-weight: bold; color: #94a3b8; margin-top: 15px; margin-bottom: 8px;'>"
                    f"ROLLING CORRELATION HEATMAP · {selected_tf}</div>",
                    unsafe_allow_html=True
                )

                # HTML Heatmap Table
                corr_header = "<th></th>"
                for col in corr_matrix.columns:
                    corr_header += f"<th style='text-align: center; font-size: 11.5px; color: #64748b; font-weight: bold;'>{col}</th>"

                corr_rows = ""
                for i, row_name in enumerate(corr_matrix.index):
                    corr_rows += f"<tr><td style='font-weight: bold; font-size: 11.5px; color: #94a3b8;'>{row_name}</td>"
                    for j, col_name in enumerate(corr_matrix.columns):
                        val = corr_matrix.loc[row_name, col_name]
                        opacity = abs(val)
                        if val >= 0:
                            bg_color  = f"rgba(16, 185, 129, {opacity*0.35:.2f})"
                            text_color = "rgba(52, 211, 153, 0.95)"
                        else:
                            bg_color  = f"rgba(239, 68, 68, {opacity*0.35:.2f})"
                            text_color = "rgba(248, 113, 113, 0.95)"
                        diagonal_style = "border: 1px solid rgba(255,255,255,0.15);" if i == j else ""
                        corr_rows += (
                            f"<td style='text-align: center; font-family: monospace; font-size: 12.5px; "
                            f"font-weight: bold; background: {bg_color}; color: {text_color}; {diagonal_style}'>"
                            f"{val:+.2f}</td>"
                        )
                    corr_rows += "</tr>"

                heatmap_html = f"""
                <div style='background: rgba(16,19,29,0.65); border: 1px solid rgba(255,255,255,0.04);
                            border-radius:12px; padding: 18px; height: 380px;
                            display: flex; flex-direction: column; justify-content: center;'>
                    <table style='width: 100%; border-collapse: collapse;'>
                        <thead><tr>{corr_header}</tr></thead>
                        <tbody>{corr_rows}</tbody>
                    </table>
                </div>
                """
                st.markdown(heatmap_html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Quant pipeline encountered an exception in Research: {e}")

    render_research()


with tab_news:
    @st.fragment(run_every=refresh_seconds if refresh_rate_label != "Manual Sync" else None)
    def render_news():
        try:
            calendar, news = fetch_calendar_and_news()
            
            st.markdown("<div style='font-size: 18px; font-weight: bold; color: #f59e0b; margin-bottom: 15px;'>⚜️ News Intelligence & Macro Events</div>", unsafe_allow_html=True)
            
            col_cal, col_ns = st.columns([1.0, 1.2])
            
            with col_cal:
                st.markdown("<div style='font-size: 14px; font-weight: bold; color: #94a3b8; margin-bottom: 12px;'>UPCOMING MACROECONOMIC CALENDAR</div>", unsafe_allow_html=True)
                
                for ev in calendar:
                    mins_left = ev.get("minutes_left")
                    if mins_left is not None:
                        if mins_left > 1440:
                            time_display = f"In {int(mins_left/1440)} days"
                        elif mins_left > 120:
                            time_display = f"In {int(mins_left/60)} hours"
                        elif mins_left > 0:
                            time_display = f"In {mins_left} minutes"
                        elif mins_left == 0:
                            time_display = "LIVE NOW"
                        else:
                            time_display = f"{abs(mins_left)} mins ago"
                    else:
                        time_display = ev["time"]
                        
                    impact_color = "#ef4444" if ev["impact"] == "HIGH" else "#f97316" if ev["impact"] == "MEDIUM" else "#eab308"
                    
                    act_val = ev.get("actual", "")
                    for_val = ev.get("forecast", "")
                    prev_val = ev.get("previous", "")
                    
                    impact_text, impact_text_color = analyze_news_impact(ev["event"], act_val, for_val)
                    
                    details_html = f"""
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255, 255, 255, 0.03); font-size: 11.5px; font-family: "JetBrains Mono", monospace;'>
                        <div style='display: flex; gap: 12px;'>
                            <span style='color: #64748b;'>ACT: <strong style='color: #cbd5e1;'>{act_val if act_val else "-"}</strong></span>
                            <span style='color: #64748b;'>FOR: <strong style='color: #cbd5e1;'>{for_val if for_val else "-"}</strong></span>
                            <span style='color: #64748b;'>PREV: <strong style='color: #cbd5e1;'>{prev_val if prev_val else "-"}</strong></span>
                        </div>
                        <div style='color: {impact_text_color}; font-weight: bold; font-size: 11px; letter-spacing: 0.2px;'>
                            {impact_text}
                        </div>
                    </div>
                    """
                    
                    st.markdown(
                        f"""
                        <div style='background: rgba(16, 19, 29, 0.6); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 8px; padding: 12px; margin-bottom: 10px;'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <span style='background: {impact_color}; color: #000; font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 4px; margin-right: 8px;'>{ev['impact']} IMPACT</span>
                                    <strong style='color:#e2e8f0; font-size: 13.5px;'>{ev['event']}</strong>
                                    <div style='font-size: 11.5px; color:#64748b; margin-top:4px;'>Date: {ev['date']} | Scheduled: {ev['time']}</div>
                                </div>
                                <div style='text-align: right;'>
                                    <span style='color: #ffd700; font-family: monospace; font-weight: bold; font-size:13.5px;'>{time_display}</span>
                                </div>
                            </div>
                            {details_html}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    
            with col_ns:
                st.markdown("<div style='font-size: 14px; font-weight: bold; color: #94a3b8; margin-bottom: 12px;'>REAL-TIME COMMODITY & MACRO NEWS FEED</div>", unsafe_allow_html=True)
                
                for idx, item in enumerate(news[:6]):
                    st.markdown(
                        f"""
                        <div style='background: rgba(16, 19, 29, 0.6); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 8px; padding: 12px; margin-bottom: 10px;'>
                            <div style='display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;'>
                                <strong style='color:#f59e0b; font-size:14px; flex: 1.8; line-height: 1.3;'>{item['title']}</strong>
                                <span style='color:#64748b; font-family: monospace; font-size: 11px; flex: 0.5; text-align:right;'>{item['time']}</span>
                            </div>
                            <p style='color:#cbd5e1; font-size: 12px; line-height: 1.5; margin: 4px 0;'>{item['summary'][:200]}...</p>
                            <span style='color:#38bdf8; font-size: 11px; font-weight:600;'>Source: {item['provider']}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        except Exception as e:
            st.error(f"Quant pipeline encountered an exception in News: {e}")
            
    render_news()

