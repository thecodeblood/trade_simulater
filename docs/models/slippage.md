# Slippage Models Documentation

The project implements multiple slippage estimation models to account for different market conditions and requirements.

## Base Slippage Estimator

The `SlippageEstimator` serves as the abstract base class for all slippage models, defining the core interface for slippage estimation.

## Simple Slippage Model

The `SimpleSlippageModel` implements a square-root formula commonly used in market impact models:

### Key Features
- Uses order size relative to market volume
- Adjusts for market volatility
- Implements both volume-aware and volume-naive calculations

### Formula
When market volume is available:
```python
slippage = impact_factor * current_price * sqrt(order_size / volume)
```

When market volume is not available:
```python
slippage = impact_factor * current_price * sqrt(order_size)
```
