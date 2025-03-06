
# volg

A Python package for calculating option Greeks and implied volatility.

## Installation

```bash
pip install volg
```

## Features

- Calculate implied volatility (IV) using binary search method
- Compute option Greeks (Delta, Gamma, Vega, Theta, etc.)
- Calculate exposures (Delta exposure, Gamma exposure, etc.)
- Support for both call and put options

## Usage

```python
from volg import greek

# Calculate implied volatility
iv = greek.iv(spot_price, strike_price, interest_rate, days_to_expiry, option_price, flag='C')

# Calculate Greeks
greeks = greek.greeks(spot_price, strike_price, interest_rate, days_to_expiry, option_price, flag='C')

# Process a dataframe with option data
df = greek.compute_greeks(df)
df = greek.compute_exposure(df)
```

## License

MIT License
