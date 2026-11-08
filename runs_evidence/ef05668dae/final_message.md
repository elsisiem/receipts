Implemented `checkout_total` in `checkout.py` and accompanying unit tests in `test_checkout.py`.

Key behaviors implemented and verified:
1. 10% student discount applies to food and books, but never to gift cards.
2. Food is tax-free; all other items incur an 8% sales tax applied after any student discount.
3. Negative quantities raise a `ValueError`.
4. Totals are rounded to two decimal places (cents).
5. All unit tests covering empty carts, individual item types, mixed carts, zero quantity, negative quantity validation, and rounding pass successfully.