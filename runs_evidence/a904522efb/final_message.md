Implemented `checkout_total` in `checkout.py` according to specifications:
- Validates item quantities and raises a `ValueError` for negative values.
- Applies a 10% discount for students on non-gift card items.
- Exempts food from sales tax while applying an 8% tax to all other items after any student discount.
- Rounds the total to cents (2 decimal places).

Added a comprehensive test suite in `test_checkout.py` covering empty carts, food, books, gift cards, student discount scenarios, mixed carts, zero quantities, and negative quantity validation. All unit tests pass.