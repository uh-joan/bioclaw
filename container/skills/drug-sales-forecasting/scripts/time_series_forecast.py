"""Time-series forecasting module with patent cliff modeling.

Uses Prophet for forecasting with external regressors for:
- Patent status (active/expired)
- Competitor count (generic entries)
- Market size growth

Also includes erosion curve modeling for post-patent scenarios.
"""

import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

# Add parent directories to path for imports
_script_dir = os.path.dirname(os.path.abspath(__file__))
_claude_dir = os.path.dirname(os.path.dirname(os.path.dirname(_script_dir)))
sys.path.insert(0, _claude_dir)

# Try to import Prophet, fall back to simple model if not available
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("  Note: Prophet not installed. Using simple forecasting model.")

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("  Note: pandas/numpy not installed. Using basic forecasting.")


def calculate_erosion_curve(
    months_since_expiry: int,
    erosion_rate: float = 0.15,
    min_share: float = 0.10,
    is_biologic: bool = False
) -> float:
    """
    Model market share erosion after patent expiry.

    Industry benchmarks:
    - Small molecules: 80-90% erosion in first 12 months
    - Biologics: 30-40% erosion in first 24 months (biosimilar adoption slower)

    Args:
        months_since_expiry: Months since patent expiry (negative if still protected)
        erosion_rate: Monthly decay rate (default 0.15 for small molecules)
        min_share: Minimum market share floor (branded loyalists)
        is_biologic: If True, use slower biosimilar erosion curve

    Returns:
        float: Retained market share (0.0 to 1.0)
    """
    if months_since_expiry <= 0:
        return 1.0  # Full market share during patent protection

    # Biologics erode slower
    if is_biologic:
        erosion_rate = erosion_rate * 0.5  # Half the erosion rate
        min_share = 0.20  # Higher floor for biologics

    # Exponential decay with floor
    decay = (1 - min_share) * np.exp(-erosion_rate * months_since_expiry) if PANDAS_AVAILABLE else \
            (1 - min_share) * (2.718 ** (-erosion_rate * months_since_expiry))

    return min_share + decay


def generate_forecast_simple(
    current_sales: float,
    patent_expiry_date: str,
    forecast_years: int = 5,
    market_growth_rate: float = 0.05,
    is_biologic: bool = False,
    scenario: str = "base",
    historical_cagr: float = None
) -> Dict[str, Any]:
    """
    Simple forecasting model (no Prophet required).

    Uses:
    - Market growth rate for pre-expiry growth
    - Erosion curve for post-expiry decline
    - CRITICAL FIX (2026-01-21): For already-expired patents (mature generics),
      use historical CAGR instead of erosion model

    Args:
        current_sales: Current annual sales (USD)
        patent_expiry_date: Patent expiry date (YYYY-MM-DD)
        forecast_years: Years to forecast
        market_growth_rate: Annual market growth rate
        is_biologic: Whether drug is a biologic
        scenario: "base", "optimistic", "pessimistic"
        historical_cagr: Historical compound annual growth rate (for mature generics)

    Returns:
        dict: Forecast with yearly projections
    """
    # CRITICAL FIX: Industry maximum - no drug has ever exceeded ~$30B
    INDUSTRY_MAX_SALES = 30_000_000_000

    # Parse patent expiry
    # CRITICAL FIX: Distinguish already-expired (mature generic) from specific expiry date
    is_mature_generic = False
    try:
        if patent_expiry_date == 'EXPIRED':
            # CRITICAL FIX: Don't apply erosion for mature generics
            # They have stable markets - use historical CAGR instead
            is_mature_generic = True
            expiry = None  # Don't trigger erosion
        else:
            expiry = datetime.strptime(patent_expiry_date, '%Y-%m-%d')
    except (ValueError, TypeError):
        expiry = None

    # Scenario adjustments
    scenario_adjustments = {
        'optimistic': {'growth_mult': 1.3, 'erosion_mult': 0.7},
        'base': {'growth_mult': 1.0, 'erosion_mult': 1.0},
        'pessimistic': {'growth_mult': 0.7, 'erosion_mult': 1.3}
    }
    adj = scenario_adjustments.get(scenario, scenario_adjustments['base'])

    # Generate yearly forecasts
    current_year = datetime.now().year
    forecasts = {}
    running_sales = current_sales
    was_capped = False

    for year_offset in range(forecast_years + 1):
        year = current_year + year_offset
        year_date = datetime(year, 6, 30)  # Mid-year

        if is_mature_generic:
            # CRITICAL FIX: For mature generics, use historical CAGR or stable market assumption
            if historical_cagr is not None:
                # Use actual historical trend (can be positive or negative)
                growth_rate = historical_cagr * adj['growth_mult']
            else:
                # Assume stable market with small growth (generic utilization tends to grow)
                growth_rate = 0.03 * adj['growth_mult']  # 3% default for mature generics

            running_sales *= (1 + growth_rate)
            # Floor at 50% of current (market can't collapse completely for mature generic)
            running_sales = max(running_sales, current_sales * 0.5)
            # Ceiling at 150% of current (limited upside for mature generic)
            running_sales = min(running_sales, current_sales * 1.5)
        else:
            # Original logic for patent-protected or specific expiry date
            if expiry:
                months_since_expiry = (year_date.year - expiry.year) * 12 + (year_date.month - expiry.month)
            else:
                months_since_expiry = -999  # Far in the future

            if months_since_expiry < 0:
                # Pre-expiry: Apply market growth
                growth = 1 + (market_growth_rate * adj['growth_mult'])
                running_sales *= growth
            else:
                # Post-expiry: Apply erosion (only for specific expiry date)
                erosion_rate = 0.15 * adj['erosion_mult']
                market_share = calculate_erosion_curve(
                    months_since_expiry,
                    erosion_rate=erosion_rate,
                    is_biologic=is_biologic
                )
                # First year post-expiry, calculate from peak
                if year_offset > 0 and months_since_expiry <= 12:
                    peak_sales = forecasts.get(str(year - 1), current_sales)
                    running_sales = peak_sales * market_share
                else:
                    running_sales = running_sales * market_share

        # CRITICAL FIX: Apply industry ceiling
        if running_sales > INDUSTRY_MAX_SALES:
            running_sales = INDUSTRY_MAX_SALES
            was_capped = True

        forecasts[str(year)] = round(running_sales, 0)

    return {
        'forecasts': forecasts,
        'model': 'mature_generic_trend' if is_mature_generic else 'simple_erosion',
        'scenario': scenario,
        'is_mature_generic': is_mature_generic,
        'was_capped_at_industry_max': was_capped,
        'assumptions': {
            'market_growth_rate': market_growth_rate if not is_mature_generic else (historical_cagr or 0.03),
            'erosion_rate': 0.15 * adj['erosion_mult'] if not is_mature_generic else None,
            'is_biologic': is_biologic,
            'patent_expiry_date': patent_expiry_date,
            'historical_cagr': historical_cagr,
            'industry_ceiling_applied': was_capped
        }
    }


def generate_forecast_prophet(
    historical_sales: List[Dict[str, Any]],
    patent_expiry_date: str,
    forecast_years: int = 5,
    market_growth_rate: float = 0.05,
    is_biologic: bool = False,
    scenario: str = "base"
) -> Dict[str, Any]:
    """
    Prophet-based forecasting with external regressors.

    Handles both:
    - Monthly data (12+ points) - full Prophet with seasonality
    - Annual data (3+ points) - Prophet with growth modeling

    Args:
        historical_sales: List of {'date': 'YYYY-MM-DD', 'sales': float} or
                         {'year': 'YYYY', 'sales': float}
        patent_expiry_date: Patent expiry date
        forecast_years: Years to forecast
        market_growth_rate: Annual market growth
        is_biologic: Whether drug is a biologic
        scenario: Forecast scenario

    Returns:
        dict: Prophet forecast results
    """
    if not PROPHET_AVAILABLE or not PANDAS_AVAILABLE:
        # Fall back to simple model
        latest_sales = historical_sales[-1]['sales'] if historical_sales else 1_000_000_000
        return generate_forecast_simple(
            current_sales=latest_sales,
            patent_expiry_date=patent_expiry_date,
            forecast_years=forecast_years,
            market_growth_rate=market_growth_rate,
            is_biologic=is_biologic,
            scenario=scenario
        )

    # Prepare data for Prophet
    df = pd.DataFrame(historical_sales)

    # Handle different date formats
    if 'date' in df.columns:
        df['ds'] = pd.to_datetime(df['date'])
    elif 'year' in df.columns:
        # Convert annual data to mid-year dates for Prophet
        df['ds'] = pd.to_datetime(df['year'].astype(str) + '-07-01')
    else:
        raise ValueError("historical_sales must have 'date' or 'year' column")

    df['y'] = df['sales'].astype(float)

    # Sort by date
    df = df.sort_values('ds').reset_index(drop=True)

    # Determine if we have enough data
    n_points = len(df)
    is_annual_data = n_points < 12

    # Parse patent expiry
    expiry = None
    if patent_expiry_date and patent_expiry_date != 'EXPIRED':
        try:
            expiry = pd.to_datetime(patent_expiry_date)
        except:
            pass
    elif patent_expiry_date == 'EXPIRED':
        expiry = pd.to_datetime('2020-01-01')  # Past date

    # Scenario adjustments
    scenario_adjustments = {
        'optimistic': {'growth_mult': 1.2, 'uncertainty': 0.8},
        'base': {'growth_mult': 1.0, 'uncertainty': 1.0},
        'pessimistic': {'growth_mult': 0.8, 'uncertainty': 1.2}
    }
    adj = scenario_adjustments.get(scenario, scenario_adjustments['base'])

    # Calculate patent status regressor
    def calc_patent_status(date):
        if expiry is None:
            return 1.0
        if date < expiry:
            return 1.0
        # Gradual decline after expiry (erosion curve)
        months_since = (date.year - expiry.year) * 12 + (date.month - expiry.month)
        erosion_rate = 0.10 if is_biologic else 0.15
        min_share = 0.20 if is_biologic else 0.10
        decay = (1 - min_share) * np.exp(-erosion_rate * max(0, months_since))
        return min_share + decay

    # Calculate market growth regressor
    start_date = df['ds'].min()
    def calc_market_growth(date):
        years_from_start = (date - start_date).days / 365.25
        adjusted_growth = market_growth_rate * adj['growth_mult']
        return (1 + adjusted_growth) ** years_from_start

    df['patent_status'] = df['ds'].apply(calc_patent_status)
    df['market_growth'] = df['ds'].apply(calc_market_growth)

    # Initialize Prophet with appropriate settings
    if is_annual_data:
        # For annual data: disable seasonality, use linear growth
        model = Prophet(
            growth='linear',
            yearly_seasonality=False,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode='multiplicative',
            interval_width=0.80 * adj['uncertainty']
        )
    else:
        # For monthly+ data: enable yearly seasonality
        model = Prophet(
            growth='linear',
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode='multiplicative',
            interval_width=0.80 * adj['uncertainty']
        )

    # Add regressors
    model.add_regressor('patent_status', mode='multiplicative')
    model.add_regressor('market_growth', mode='multiplicative')

    # Suppress Prophet stdout
    import logging
    logging.getLogger('prophet').setLevel(logging.WARNING)
    logging.getLogger('cmdstanpy').setLevel(logging.WARNING)

    # Fit model
    model.fit(df[['ds', 'y', 'patent_status', 'market_growth']])

    # Create future dataframe
    if is_annual_data:
        # For annual data, create yearly predictions
        future_dates = pd.date_range(
            start=df['ds'].max() + pd.DateOffset(years=1),
            periods=forecast_years,
            freq='YS'
        ) + pd.DateOffset(months=6)  # Mid-year
        future = pd.DataFrame({'ds': future_dates})
        # Add historical dates for complete forecast
        future = pd.concat([df[['ds']], future]).reset_index(drop=True)
    else:
        future = model.make_future_dataframe(periods=forecast_years * 12, freq='MS')

    future['patent_status'] = future['ds'].apply(calc_patent_status)
    future['market_growth'] = future['ds'].apply(calc_market_growth)

    # Predict
    forecast = model.predict(future)

    # Extract yearly forecasts (use year-end values for annual, mean for monthly)
    forecast['year'] = forecast['ds'].dt.year
    current_year = datetime.now().year

    # Get unique future years
    future_years = sorted(forecast[forecast['year'] >= current_year]['year'].unique())

    # CRITICAL FIX (2026-01-21): Cap forecasts at industry maximum
    # No single drug has ever exceeded ~$25-30B in annual sales
    # Examples: Humira peaked at ~$21B, Keytruda at ~$25B
    INDUSTRY_MAX_SALES = 30_000_000_000  # $30B ceiling

    # Build yearly forecasts dict
    yearly_forecasts = {}
    was_capped = False
    for year in future_years[:forecast_years + 1]:
        year_data = forecast[forecast['year'] == year]
        if not year_data.empty:
            # Use mean for the year, ensuring positive values
            yhat = max(0, year_data['yhat'].mean())
            # CRITICAL FIX: Apply industry ceiling
            if yhat > INDUSTRY_MAX_SALES:
                yhat = INDUSTRY_MAX_SALES
                was_capped = True
            yearly_forecasts[str(year)] = round(yhat, 0)

    return {
        'forecasts': yearly_forecasts,
        'model': 'prophet',
        'scenario': scenario,
        'was_capped_at_industry_max': was_capped,
        'industry_max': INDUSTRY_MAX_SALES if was_capped else None,
        'confidence_intervals': {
            str(year): {
                'lower': round(max(0, forecast[forecast['year'] == year]['yhat_lower'].mean()), 0),
                'upper': round(min(INDUSTRY_MAX_SALES, forecast[forecast['year'] == year]['yhat_upper'].mean()), 0)
            }
            for year in future_years[:forecast_years + 1]
            if not forecast[forecast['year'] == year].empty
        },
        'assumptions': {
            'market_growth_rate': market_growth_rate,
            'is_biologic': is_biologic,
            'patent_expiry_date': patent_expiry_date,
            'data_points': n_points,
            'data_type': 'annual' if is_annual_data else 'monthly',
            'industry_ceiling_applied': was_capped
        }
    }


def forecast_drug_sales(
    drug_name: str,
    current_sales: float = None,
    historical_sales: List[Dict[str, Any]] = None,
    patent_expiry_date: str = None,
    forecast_years: int = 5,
    market_growth_rate: float = 0.05,
    is_biologic: bool = False,
    scenario: str = "base"
) -> Dict[str, Any]:
    """
    Main forecasting function.

    Args:
        drug_name: Drug name for reporting
        current_sales: Current annual sales (if no historical data)
        historical_sales: List of {'date': 'YYYY-MM-DD', 'sales': float}
        patent_expiry_date: Patent expiry date (YYYY-MM-DD)
        forecast_years: Years to forecast
        market_growth_rate: Annual market growth rate
        is_biologic: Whether drug is a biologic
        scenario: "base", "optimistic", "pessimistic"

    Returns:
        dict: Complete forecast with projections and assumptions
    """
    result = {
        'drug_name': drug_name,
        'forecast_period': f"{datetime.now().year}-{datetime.now().year + forecast_years}",
        'patent_expiry': patent_expiry_date,
        'is_biologic': is_biologic,
        'scenario': scenario
    }

    # Calculate historical CAGR if we have historical data (critical for mature generics)
    historical_cagr = None
    if historical_sales and len(historical_sales) >= 2:
        first_sales = historical_sales[0].get('sales', 0)
        last_sales = historical_sales[-1].get('sales', 0)
        n_years = len(historical_sales) - 1
        if first_sales > 0 and n_years > 0:
            historical_cagr = (last_sales / first_sales) ** (1 / n_years) - 1

    # Use Prophet if historical data available (3+ points) and Prophet installed
    # Prophet can work with annual data (3-5 years from Medicare) or monthly data
    if historical_sales and len(historical_sales) >= 3 and PROPHET_AVAILABLE:
        forecast_result = generate_forecast_prophet(
            historical_sales=historical_sales,
            patent_expiry_date=patent_expiry_date,
            forecast_years=forecast_years,
            market_growth_rate=market_growth_rate,
            is_biologic=is_biologic,
            scenario=scenario
        )
    else:
        # Use simple model
        sales = current_sales or 1_000_000_000  # Default $1B if unknown
        forecast_result = generate_forecast_simple(
            current_sales=sales,
            patent_expiry_date=patent_expiry_date,
            forecast_years=forecast_years,
            market_growth_rate=market_growth_rate,
            is_biologic=is_biologic,
            scenario=scenario,
            historical_cagr=historical_cagr  # Pass CAGR for mature generic handling
        )

    result['forecasts'] = forecast_result['forecasts']
    result['model_used'] = forecast_result['model']
    result['assumptions'] = forecast_result['assumptions']

    # Add risk factors
    result['risk_factors'] = []

    if patent_expiry_date:
        try:
            expiry = datetime.strptime(patent_expiry_date, '%Y-%m-%d')
            years_to_expiry = (expiry - datetime.now()).days / 365.25

            if years_to_expiry < 2:
                result['risk_factors'].append('High risk: Patent expiry within 2 years')
            elif years_to_expiry < 5:
                result['risk_factors'].append('Medium risk: Patent expiry within 5 years')
        except:
            pass

    if is_biologic:
        result['risk_factors'].append('Biologic: Biosimilar erosion typically slower than generics')
    else:
        result['risk_factors'].append('Small molecule: Rapid generic erosion expected post-expiry')

    return result


def estimate_carrying_capacity(
    current_sales: float,
    segment_revenue: float = None,
    tam: float = None,
    historical_cagr: float = None
) -> tuple:
    """
    Estimate carrying capacity (market ceiling) for logistic growth model.

    Uses multiple signals to estimate a reasonable market ceiling:
    1. Segment revenue (if available) - drug can capture portion of segment
    2. TAM (total addressable market) - theoretical maximum
    3. Historical CAGR - if growth is explosive, ceiling is higher
    4. Industry benchmarks - largest drugs historically peak at ~$20-25B

    Returns:
        tuple: (cap_mean, cap_std) for Monte Carlo sampling
    """
    estimates = []

    # Signal 1: Segment revenue - drug could capture 30-70% of segment
    if segment_revenue and segment_revenue > current_sales:
        cap_from_segment = segment_revenue * 0.5  # Assume 50% capture on average
        estimates.append(cap_from_segment)

    # Signal 2: TAM - drug could capture 5-20% of TAM
    if tam and tam > current_sales:
        cap_from_tam = tam * 0.10  # Assume 10% capture on average
        estimates.append(cap_from_tam)

    # Signal 3: Historical CAGR suggests growth trajectory
    if historical_cagr and historical_cagr > 0.3:  # High-growth drug (>30% CAGR)
        # High-growth drugs can reach larger peaks
        # But growth eventually slows - estimate 3-5x current sales
        cap_from_growth = current_sales * 4
        estimates.append(cap_from_growth)

    # Signal 4: Industry benchmark - largest single drugs peak ~$20-25B
    # Humira peaked at ~$21B, Keytruda at ~$25B
    industry_benchmark = 25_000_000_000  # $25B
    estimates.append(industry_benchmark)

    # Signal 5: Current sales floor - ceiling must be > current
    # Minimum ceiling is 1.5x current sales
    min_ceiling = current_sales * 1.5
    estimates.append(min_ceiling)

    if estimates:
        # Use median of estimates as mean, with reasonable uncertainty
        cap_mean = float(np.median(estimates))
        # Ensure ceiling is at least 1.2x current sales
        cap_mean = max(cap_mean, current_sales * 1.2)
        # Standard deviation is 30% of mean (significant uncertainty)
        cap_std = cap_mean * 0.30
        return cap_mean, cap_std
    else:
        # Fallback: 3x current sales with high uncertainty
        return current_sales * 3, current_sales * 1.0


def run_monte_carlo_simulation(
    current_sales: float,
    patent_expiry_date: str,
    forecast_years: int = 5,
    is_biologic: bool = False,
    n_simulations: int = 1000,
    market_growth_mean: float = 0.05,
    market_growth_std: float = 0.02,
    erosion_rate_mean: float = None,
    erosion_rate_std: float = 0.03,
    competitive_pressure: float = 0.0,
    carrying_capacity_mean: float = None,
    carrying_capacity_std: float = None,
    segment_revenue: float = None,
    tam: float = None,
    historical_cagr: float = None
) -> Dict[str, Any]:
    """
    Run Monte Carlo simulation with LOGISTIC GROWTH and uncertainty on carrying capacity.

    This is the best-in-class approach used by pharma commercial teams:
    1. Logistic growth (S-curve) - sales grow toward a ceiling, then saturate
    2. Monte Carlo on carrying capacity - captures uncertainty in market size
    3. Monte Carlo on growth rate - captures uncertainty in trajectory
    4. Monte Carlo on erosion rate - captures uncertainty in post-patent decline

    The logistic growth formula:
        sales(t+1) = sales(t) + r * sales(t) * (1 - sales(t) / K)

    Where:
        r = intrinsic growth rate
        K = carrying capacity (market ceiling)

    CRITICAL FIX (2026-01-21): For already-expired patents, use historical CAGR
    instead of erosion model. Mature generics have stable markets (e.g., atorvastatin
    has $1B/year stable Medicare spend, not exponential decay).

    Args:
        current_sales: Current annual sales
        patent_expiry_date: Patent expiry date (YYYY-MM-DD) or "EXPIRED"
        forecast_years: Years to forecast
        is_biologic: Whether drug is a biologic (slower biosimilar erosion)
        n_simulations: Number of Monte Carlo simulations (default 1000)
        market_growth_mean: Mean intrinsic growth rate for logistic model (default 5%)
        market_growth_std: Std dev of growth rate (default 2%)
        erosion_rate_mean: Mean erosion rate (None = use default based on drug type)
        erosion_rate_std: Std dev of erosion rate (default 3%)
        competitive_pressure: Additional competitive pressure factor (0-1)
        carrying_capacity_mean: Mean carrying capacity (market ceiling). If None, estimated.
        carrying_capacity_std: Std dev of carrying capacity. If None, estimated.
        segment_revenue: Manufacturer segment revenue (for ceiling estimation)
        tam: Total addressable market (for ceiling estimation)
        historical_cagr: Historical compound annual growth rate (for ceiling estimation)

    Returns:
        dict: Monte Carlo results with percentiles, statistics, and model parameters
    """
    if not PANDAS_AVAILABLE:
        return {'error': 'Monte Carlo requires numpy/pandas'}

    # Default erosion rates based on drug type
    if erosion_rate_mean is None:
        erosion_rate_mean = 0.08 if is_biologic else 0.15  # Monthly rate

    # Estimate carrying capacity if not provided
    if carrying_capacity_mean is None:
        carrying_capacity_mean, carrying_capacity_std = estimate_carrying_capacity(
            current_sales=current_sales,
            segment_revenue=segment_revenue,
            tam=tam,
            historical_cagr=historical_cagr
        )

    if carrying_capacity_std is None:
        carrying_capacity_std = carrying_capacity_mean * 0.30  # 30% uncertainty

    # Parse patent expiry
    # CRITICAL FIX: Distinguish between "EXPIRED" (mature generic - use CAGR) vs
    # specific expiry date (apply erosion only at cliff moment)
    expiry_year = None
    is_already_expired = False  # NEW: Track if patent expired long ago (mature generic)

    if patent_expiry_date and patent_expiry_date != 'EXPIRED':
        try:
            expiry_year = int(patent_expiry_date[:4])
        except:
            pass
    elif patent_expiry_date == 'EXPIRED':
        # CRITICAL FIX: For already-expired patents, DON'T apply erosion model
        # Instead, use historical CAGR (mature market with stable/growing sales)
        is_already_expired = True
        expiry_year = None  # Don't trigger erosion - market has already stabilized

    current_year = datetime.now().year
    years = list(range(current_year, current_year + forecast_years + 1))

    # Adjust growth rate based on historical CAGR
    # High-growth drugs should use higher intrinsic rate to reach ceiling faster
    if historical_cagr and historical_cagr > 0.30:
        # Scale growth rate based on historical performance (capped at 80%)
        adjusted_growth_mean = min(0.80, historical_cagr * 0.6)  # 60% of historical CAGR
        adjusted_growth_std = adjusted_growth_mean * 0.3  # 30% relative std
    elif is_already_expired and historical_cagr is not None:
        # CRITICAL FIX: For mature generics, use actual historical CAGR
        # This can be positive (growing generic market) or negative (declining brand)
        adjusted_growth_mean = historical_cagr
        adjusted_growth_std = abs(historical_cagr) * 0.3 + 0.02  # Uncertainty based on magnitude
    else:
        adjusted_growth_mean = market_growth_mean
        adjusted_growth_std = market_growth_std

    # Run simulations
    all_simulations = []
    sampled_caps = []

    for sim in range(n_simulations):
        # Sample parameters from distributions
        # Growth rate: higher for early-stage drugs, use log-normal to ensure positive
        if is_already_expired:
            # For mature generics: allow negative growth (declining) or positive (growing)
            growth_rate = np.random.normal(adjusted_growth_mean, adjusted_growth_std)
            # Clamp to reasonable range: -30% to +30% per year for mature markets
            growth_rate = max(-0.30, min(0.30, growth_rate))
        else:
            growth_rate = max(0.01, np.random.normal(adjusted_growth_mean, adjusted_growth_std))

        # Carrying capacity: sample from truncated normal (must be > current sales)
        # For mature generics, ceiling is closer to current (stable market)
        if is_already_expired:
            # Mature market: ceiling is 1.0-1.5x current (limited upside)
            cap = current_sales * np.random.uniform(1.0, 1.5)
        else:
            cap = np.random.normal(carrying_capacity_mean, carrying_capacity_std)
            cap = max(cap, current_sales * 1.1)  # Floor at 1.1x current
        sampled_caps.append(cap)

        # Erosion rate post-patent
        erosion_rate = max(0.01, np.random.normal(erosion_rate_mean, erosion_rate_std))
        min_share = 0.20 if is_biologic else 0.10

        # Competitive pressure variation
        comp_adjustment = np.random.uniform(0, competitive_pressure) if competitive_pressure > 0 else 0

        simulation = {}
        sales = current_sales

        for year in years:
            if is_already_expired:
                # CRITICAL FIX: For mature generics, use simple CAGR-based projection
                # No logistic growth, no erosion - just trend continuation with noise
                sales = sales * (1 + growth_rate)
                # Floor at 50% of current (market can't collapse completely)
                sales = max(sales, current_sales * 0.5)
                # Ceiling at 150% of current (limited upside for mature generic)
                sales = min(sales, current_sales * 1.5)
            else:
                # LOGISTIC GROWTH MODEL (S-curve) for patent-protected drugs
                # ds/dt = r * s * (1 - s/K)
                # Discrete version: s(t+1) = s(t) + r * s(t) * (1 - s(t)/K)
                if sales < cap:
                    # Growth phase: logistic growth toward ceiling
                    growth = growth_rate * sales * (1 - sales / cap)
                    growth = growth * (1 - comp_adjustment)  # Reduce by competitive pressure
                    sales = sales + growth
                else:
                    # At or above ceiling: no growth (or slight decline from competition)
                    sales = sales * (1 - comp_adjustment * 0.5)

                # Apply patent erosion ONLY at the cliff moment (not for already-expired)
                if expiry_year and year > expiry_year:
                    months_since = (year - expiry_year) * 12
                    erosion_mult = min_share + (1 - min_share) * np.exp(-erosion_rate * months_since)
                    sales = sales * erosion_mult

            # Add random noise (±3% volatility - reduced from 5% for stability)
            noise = np.random.normal(1.0, 0.03)
            sales = sales * noise
            sales = max(0, sales)  # Ensure non-negative

            simulation[str(year)] = sales

        all_simulations.append(simulation)

    # Convert to DataFrame for percentile calculations
    sim_df = pd.DataFrame(all_simulations)

    # Calculate percentiles for each year
    percentiles = {}
    for year in years:
        year_str = str(year)
        year_data = sim_df[year_str]
        percentiles[year_str] = {
            'p5': float(np.percentile(year_data, 5)),
            'p10': float(np.percentile(year_data, 10)),
            'p25': float(np.percentile(year_data, 25)),
            'p50': float(np.percentile(year_data, 50)),  # Median
            'p75': float(np.percentile(year_data, 75)),
            'p90': float(np.percentile(year_data, 90)),
            'p95': float(np.percentile(year_data, 95)),
            'mean': float(year_data.mean()),
            'std': float(year_data.std())
        }

    # Calculate summary statistics
    final_year = str(years[-1])
    final_dist = sim_df[final_year]

    # Determine model type for transparency
    if is_already_expired:
        model_type = 'mature_generic_cagr'  # Uses historical CAGR, stable market
    else:
        model_type = 'logistic_monte_carlo'  # Uses S-curve growth + patent erosion

    return {
        'n_simulations': n_simulations,
        'forecast_years': forecast_years,
        'is_biologic': is_biologic,
        'patent_expiry': patent_expiry_date,
        'model': model_type,
        'is_mature_generic': is_already_expired,
        'percentiles_by_year': percentiles,
        'summary': {
            'current_sales': current_sales,
            'final_year': final_year,
            'final_year_median': float(np.percentile(final_dist, 50)),
            'final_year_p10_p90': (float(np.percentile(final_dist, 10)), float(np.percentile(final_dist, 90))),
            'final_year_p5_p95': (float(np.percentile(final_dist, 5)), float(np.percentile(final_dist, 95))),
            'coefficient_of_variation': float(final_dist.std() / final_dist.mean()) if final_dist.mean() > 0 else 0
        },
        'carrying_capacity': {
            'mean': carrying_capacity_mean,
            'std': carrying_capacity_std,
            'sampled_median': float(np.median(sampled_caps)),
            'sampled_p10_p90': (float(np.percentile(sampled_caps, 10)), float(np.percentile(sampled_caps, 90)))
        },
        'parameters': {
            'market_growth_mean': adjusted_growth_mean,
            'market_growth_std': adjusted_growth_std,
            'historical_cagr': historical_cagr,
            'erosion_rate_mean': erosion_rate_mean,
            'erosion_rate_std': erosion_rate_std,
            'competitive_pressure': competitive_pressure
        }
    }


def generate_all_scenarios(
    drug_name: str,
    current_sales: float,
    patent_expiry_date: str,
    forecast_years: int = 5,
    is_biologic: bool = False,
    historical_sales: List[Dict[str, Any]] = None,
    run_monte_carlo: bool = True,
    competitive_pressure: float = 0.0,
    segment_revenue: float = None,
    tam: float = None
) -> Dict[str, Any]:
    """
    Generate forecasts for all scenarios (base, optimistic, pessimistic).

    Runs Monte Carlo simulation with LOGISTIC GROWTH for realistic forecasting.
    The Monte Carlo model uses:
    - S-curve growth toward a carrying capacity (market ceiling)
    - Uncertainty on the ceiling itself (sampled from distribution)
    - Patent erosion modeling post-expiry

    Args:
        drug_name: Drug name
        current_sales: Current annual sales
        patent_expiry_date: Patent expiry date (YYYY-MM-DD) or "EXPIRED"
        forecast_years: Years to forecast
        is_biologic: Whether drug is a biologic
        historical_sales: Optional list of {'date': 'YYYY-MM-DD', 'sales': float}
                         If provided and Prophet available, uses ML-based forecasting
        run_monte_carlo: Whether to run Monte Carlo simulation (default True)
        competitive_pressure: Additional competitive pressure (0-1) based on active trials
        segment_revenue: Manufacturer segment revenue (for ceiling estimation)
        tam: Total addressable market (for ceiling estimation)

    Returns:
        dict: Forecasts for all three scenarios plus Monte Carlo results with logistic growth
    """
    scenarios = {}
    model_used = 'simple_erosion'

    for scenario in ['base', 'optimistic', 'pessimistic']:
        forecast = forecast_drug_sales(
            drug_name=drug_name,
            current_sales=current_sales,
            historical_sales=historical_sales,
            patent_expiry_date=patent_expiry_date,
            forecast_years=forecast_years,
            is_biologic=is_biologic,
            scenario=scenario
        )
        scenarios[scenario] = forecast['forecasts']
        model_used = forecast.get('model_used', 'simple_erosion')

    result = {
        'drug_name': drug_name,
        'current_sales': current_sales,
        'patent_expiry': patent_expiry_date,
        'forecast_years': forecast_years,
        'model_used': model_used,
        'historical_data_points': len(historical_sales) if historical_sales else 0,
        'scenarios': scenarios,
        'summary': {
            'peak_year': max(scenarios['base'].items(), key=lambda x: x[1])[0],
            'peak_sales_base': max(scenarios['base'].values()),
            'final_year_range': {
                'pessimistic': list(scenarios['pessimistic'].values())[-1],
                'base': list(scenarios['base'].values())[-1],
                'optimistic': list(scenarios['optimistic'].values())[-1]
            }
        }
    }

    # Calculate historical CAGR if we have historical data
    historical_cagr = None
    if historical_sales and len(historical_sales) >= 2:
        first_sales = historical_sales[0]['sales']
        last_sales = historical_sales[-1]['sales']
        n_years = len(historical_sales) - 1
        if first_sales > 0 and n_years > 0:
            historical_cagr = (last_sales / first_sales) ** (1 / n_years) - 1

    # Run Monte Carlo simulation with logistic growth if requested
    if run_monte_carlo and PANDAS_AVAILABLE:
        mc_result = run_monte_carlo_simulation(
            current_sales=current_sales,
            patent_expiry_date=patent_expiry_date,
            forecast_years=forecast_years,
            is_biologic=is_biologic,
            n_simulations=1000,
            competitive_pressure=competitive_pressure,
            segment_revenue=segment_revenue,
            tam=tam,
            historical_cagr=historical_cagr
        )
        result['monte_carlo'] = mc_result

    return result


if __name__ == "__main__":
    # Test forecasting
    print("\n📈 Drug Sales Forecasting Test")
    print("=" * 60)

    # Test with sample data
    result = forecast_drug_sales(
        drug_name="Ozempic (semaglutide)",
        current_sales=15_000_000_000,  # $15B
        patent_expiry_date="2031-12-05",
        forecast_years=10,
        is_biologic=False,
        scenario="base"
    )

    print(f"\nDrug: {result['drug_name']}")
    print(f"Patent Expiry: {result['patent_expiry']}")
    print(f"Model Used: {result['model_used']}")
    print(f"\nForecasted Sales:")

    for year, sales in result['forecasts'].items():
        print(f"  {year}: ${sales:,.0f}")

    print(f"\nRisk Factors:")
    for risk in result['risk_factors']:
        print(f"  • {risk}")

    # Test all scenarios
    print("\n\n📊 All Scenarios Comparison")
    print("=" * 60)

    all_scenarios = generate_all_scenarios(
        drug_name="Ozempic",
        current_sales=15_000_000_000,
        patent_expiry_date="2031-12-05",
        forecast_years=10,
        is_biologic=False
    )

    print(f"\nPeak Year: {all_scenarios['summary']['peak_year']}")
    print(f"Peak Sales (Base): ${all_scenarios['summary']['peak_sales_base']:,.0f}")
    print(f"\nFinal Year Range:")
    final = all_scenarios['summary']['final_year_range']
    print(f"  Pessimistic: ${final['pessimistic']:,.0f}")
    print(f"  Base: ${final['base']:,.0f}")
    print(f"  Optimistic: ${final['optimistic']:,.0f}")
