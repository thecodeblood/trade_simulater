# Fee Models Documentation

## Fee Structure Implementation

The project implements a flexible fee calculation system through several key components:

### Fee Types (Enum)
- `MAKER`: For adding liquidity
- `TAKER`: For removing liquidity
- `DEPOSIT`: For depositing funds
- `WITHDRAWAL`: For withdrawing funds
- `NETWORK`: For blockchain network fees

### Fee Structures (Enum)
- `FLAT`: Fixed fee regardless of trade size
- `PERCENTAGE`: Fee as a percentage of trade value
- `TIERED`: Fee based on trading volume tiers

## Percentage Fee Calculator

The `PercentageFeeCalculator` implements the most common fee structure in cryptocurrency exchanges:

### Default Rates
- Maker fee: 0.1% (0.001)
- Taker fee: 0.2% (0.002)
- Deposit fee: 0% (0.0)
- Withdrawal fee: 0.05% (0.0005)

### Calculation Method
```python
fee = trade_value * fee_rate  # where trade_value = order_size * price

