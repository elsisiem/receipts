def checkout_total(items, student=False):
    """Calculate the checkout total for a list of items.

    Args:
        items (list[dict]): List of item dicts with keys:
            - name (str)
            - price (float)
            - qty (int)
            - kind ('food' | 'book' | 'gift_card')
        student (bool): Whether the customer is a student (10% discount on non-gift cards).

    Returns:
        float: Total price rounded to cents.

    Raises:
        ValueError: If any item has a negative quantity.
    """
    total = 0.0
    for item in items:
        qty = item["qty"]
        if qty < 0:
            raise ValueError(f"Quantity cannot be negative: {qty}")

        price = float(item["price"])
        kind = item["kind"]

        # Students get 10% off, but never on gift cards
        discount = 0.10 if (student and kind != "gift_card") else 0.0
        discounted_amount = price * qty * (1.0 - discount)

        # Food is tax-free; everything else has 8% sales tax after discounts
        tax_rate = 0.0 if kind == "food" else 0.08
        tax = discounted_amount * tax_rate

        total += discounted_amount + tax

    return round(total, 2)
