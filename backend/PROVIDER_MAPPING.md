# Market Data Provider Mapping

## Overview
The backend uses a hybrid market data provider that combines multiple data sources to ensure reliability and coverage for different markets, including Indian equities.

## Primary Provider: Finnhub
- Used as the primary data source for most endpoints
- API Key: Configured via `FINNHUB_API_KEY` environment variable
- Base URL: `https://finnhub.io/api/v1`

## Fallback Provider: Yahoo Finance (yfinance)
- Used as fallback when Finnhub returns 403 errors or fails
- No API key required (uses yfinance Python library)
- Supports global markets including Indian equities (NSE, BSE)

## Endpoint Provider Mapping

### Search Companies
- **Endpoint**: `GET /api/v1/companies/search`
- **Primary Provider**: Finnhub
- **Fallback**: None
- **Notes**: Search is only available via Finnhub API

### Company Profile
- **Endpoint**: `GET /api/v1/companies/{symbol}/profile`
- **Primary Provider**: Finnhub (`/stock/profile2`)
- **Fallback**: Yahoo Finance (yfinance)
- **Fallback Trigger**: 403 error, API failure, or empty response
- **Notes**: Fallback supports Indian companies like TCS, RELIANCE, INFY, HDFCBANK

### Company Quote
- **Endpoint**: `GET /api/v1/companies/{symbol}/quote`
- **Primary Provider**: Finnhub (`/quote`)
- **Fallback**: Yahoo Finance (yfinance)
- **Fallback Trigger**: 403 error, API failure, or empty response
- **Notes**: Fallback provides current price, change, volume, market cap, PE ratio, EPS, 52-week high/low

### Company Financials
- **Endpoint**: `GET /api/v1/companies/{symbol}/financials`
- **Primary Provider**: Finnhub (`/stock/financials-reported`)
- **Fallback**: Yahoo Finance (yfinance)
- **Fallback Trigger**: 403 error, API failure, or empty response
- **Notes**: Fallback provides revenue, net income, assets, liabilities, equity, cash flows

### Company News
- **Endpoint**: `GET /api/v1/companies/{symbol}/news`
- **Primary Provider**: Finnhub (`/company-news`)
- **Fallback**: Yahoo Finance (yfinance)
- **Fallback Trigger**: 403 error, API failure, or empty response
- **Notes**: Fallback supports news filtering by date range

### Historical Prices
- **Endpoint**: `GET /api/v1/companies/{symbol}/history`
- **Primary Provider**: Alpha Vantage (via Finnhub provider)
- **Fallback**: Yahoo Finance (yfinance)
- **Fallback Trigger**: 403 error, API failure, or empty response
- **Notes**: Fallback supports various time resolutions (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)

## Indian Equity Support

The hybrid provider ensures that Indian companies listed on NSE and BSE are supported through the yfinance fallback:

- **TCS** (Tata Consultancy Services): `.NS` suffix for NSE
- **RELIANCE** (Reliance Industries): `.NS` suffix for NSE  
- **INFY** (Infosys): `.NS` suffix for NSE
- **HDFCBANK** (HDFC Bank): `.NS` suffix for NSE

When searching for these companies, users should use the appropriate suffix:
- NSE: Add `.NS` (e.g., `TCS.NS`)
- BSE: Add `.BO` (e.g., `TCS.BO`)

## Implementation Details

### Hybrid Provider Flow
1. Try primary provider (Finnhub)
2. If successful, return data and log success
3. If failed (403, error, or empty), log warning and try fallback
4. If fallback successful, return data and log success
5. If both fail, return None/empty and log error

### Logging
All provider attempts are logged with:
- Success logs when data is retrieved
- Warning logs when primary fails and fallback is attempted
- Error logs when both primary and fallback fail

### Configuration
- Finnhub API key: `FINNHUB_API_KEY` in environment variables
- Alpha Vantage API key: `ALPHA_VANTAGE_API_KEY` in environment variables
- yfinance: No configuration required

## Files Modified
- `backend/app/providers/market/yfinance_provider.py` - New yfinance provider
- `backend/app/providers/market/hybrid.py` - New hybrid provider with fallback logic
- `backend/app/providers/market/provider.py` - Updated to use hybrid provider
- `backend/requirements.txt` - yfinance already included (version 1.5.2)
