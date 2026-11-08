Implemented `checkout_total` in `checkout.py` and wrote comprehensive test coverage in `test_checkout.py`.

Summary of implementation:
- Input validation: raises `ValueError` for negative quantities and coupon values outside [0, 100].
- Book promotion: buy 2 get 3rd cheapest free, taking groups of 3 with cheapest free.
- Discount calculation: multiplicative coupon stacking and additional 10% student discount capped at 25% total discount.
- Exclusions & Taxes: gift cards are never discounted and never taxed; food is discounted but untaxed; books and other items are discounted and subject to 8.25% sales tax.
- Rounding: precision calculations with Banker's rounding (`ROUND_HALF_EVEN`) to 2 decimal places applied only at the final total.
- All unit tests passed.