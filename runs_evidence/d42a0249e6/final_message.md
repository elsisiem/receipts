Implemented `checkout_total` in `checkout.py` according to all specified rules:
- Buy 2 books get the cheapest 3rd book free (per group of 3, cheapest first across units).
- Multiplicative coupon stacking capped at 25% total discount.
- Student discount (additional 10% after coupons), also capped at 25% total discount.
- Gift cards are excluded from discounts and taxes.
- Food is untaxed.
- Taxable items (paid books and other taxable goods) incur 8.25% tax on discounted amount.
- Banker's rounding (`round(total, 2)`) applied only at the final total.
- ValueError raised for negative quantities and coupon values outside [0, 100].

All test cases pass including edge cases, discount caps, tax rules, and rounding.