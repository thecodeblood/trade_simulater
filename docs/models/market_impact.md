# Market Impact Model Documentation

## Almgren-Chriss Model Implementation

The project implements the Almgren-Chriss model for market impact estimation through the `AlmgrenChrissModel` class. This sophisticated model divides market impact into two key components:

1. **Temporary Impact**: Affects only the current trade and decays afterward
2. **Permanent Impact**: Persists in the market and affects all future trades

### Model Parameters

- `lambda_temp`: Temporary market impact factor (default: 1e-6)
- `gamma`: Risk aversion parameter (default: 0.1)
- `sigma`: Asset volatility (default: 0.3)
- `eta`: Permanent market impact factor (default: 2.5e-7)
- `epsilon`: Fixed trading cost (default: 0.01)
- `tau`: Time interval between trades (default: 1.0)

### Key Calculations

1. **Adjusted Permanent Impact**:
   ```python
   eta_tilde = eta - 0.5 * gamma * tau
   ```

2. **Kappa Parameter :**:
   ```python
   kappa_tilde_squared = (lambda_temp * sigma**2) / eta_tilde
   kappa = arccosh(0.5 * (kappa_tilde_squared * tau**2) + 1) / tau
   ```

3. **Temporary Impact Calculation**:
   ```python
   temp_impact = (lambda_temp * sigma**2) / (2 * eta_tilde) * (sinh(kappa * (tau - t)) - sinh(kappa * t))
   ```

4. **Permanent Impact Calculation**:
   ```python
   perm_impact = (eta_tilde / (2 * kappa_tilde_squared)) * (cosh(kappa * (tau - t)) - cosh(kappa * t))
   ```

5. **Total Impact Calculation**:
   ```python
   total_impact = temp_impact + perm_impact
   ```

### Usage

The `AlmgrenChrissModel` class provides a method `calculate_impact` to calculate market impact for a given trade size and time. The method takes the trade size and time as inputs and returns the total market impact.

```python
from market_impact import AlmgrenChrissModel

model = AlmgrenChrissModel()
trade_size = 10000
time = 5
impact = model.calculate_impact(trade_size, time)
print(f"Market impact for trade size {trade_size} at time {time}: {impact}")
```




