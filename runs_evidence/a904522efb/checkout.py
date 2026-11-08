def checkout_total(items, student=False):
    """Calculate total checkout price for a list of items.

    Each item is a dict with keys:
        - name (str)
        - price (float)
        - qty (int)
        - kind ('food' | 'book' | 'gift_card')

    Rules:
        - Students get 10% discount on non-gift_card items.
        - Food is tax-free (0% sales tax).
        - Everything else has 8% sales tax applied after discounts.
        - Negative quantities raise ValueError.
        - Final total is rounded to cents (2 decimal places).
    """
    total = 0.0
    for item in items:
        qty = item['qty']
        if qty < 0:
            raise ValueError(f"Quantity cannot be negative: {qty}")
        
        price = item['price']
        kind = item['kind']
        subtotal = price * qty
        
        # Student discount: 10% off on non-gift cards
        if student and kind != 'gift_card':
            subtotal *= 0.90
        
        # Tax: food is tax-free, everything else is 8% tax applied after discounts
        if kind != 'food':
            subtotal *= 1.08
        
        total += subtotal
        
    return round(total, 2)
