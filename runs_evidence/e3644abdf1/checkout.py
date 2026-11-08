from decimal import Decimal, ROUND_HALF_EVEN


def checkout_total(items, coupons=(), student=False):
    for c in coupons:
        if c < 0 or c > 100:
            raise ValueError(f"Invalid coupon percentage: {c}")

    for item in items:
        if item.get('qty', 0) < 0:
            raise ValueError(f"Negative quantity not allowed: {item.get('qty')}")

    # Calculate discount factor
    # Coupons stack multiplicatively: factor = product of (1 - c/100)
    factor = 1.0
    for c in coupons:
        factor *= (1.0 - c / 100.0)

    if student:
        factor *= 0.9

    # Discount capped at 25%, meaning minimum factor is 0.75
    discount_rate = 1.0 - factor
    if discount_rate > 0.25:
        discount_rate = 0.25

    # Process books for "buy 2 get cheapest 3rd free"
    # Items: dicts with name, price (float), qty (int), kind ('food'|'book'|'gift_card')
    book_prices = []
    food_subtotal = 0.0
    gift_card_subtotal = 0.0
    other_subtotal = 0.0

    for item in items:
        price = float(item['price'])
        qty = int(item['qty'])
        kind = item.get('kind')

        if qty == 0:
            continue

        if kind == 'book':
            book_prices.extend([price] * qty)
        elif kind == 'food':
            food_subtotal += price * qty
        elif kind == 'gift_card':
            gift_card_subtotal += price * qty
        else:
            other_subtotal += price * qty

    # "Buy 2 books get the cheapest 3rd book free (per group of 3, cheapest first)"
    # For N books, number of free books is N // 3. Sort prices ascending, first N // 3 are free.
    book_prices.sort()
    num_free = len(book_prices) // 3
    paid_book_prices = book_prices[num_free:]
    book_subtotal = sum(paid_book_prices)

    # Apply discount: gift cards are NEVER discounted
    # Food, book, and other kinds are eligible for coupon/student discounts
    discount_mult = 1.0 - discount_rate
    discounted_food = food_subtotal * discount_mult
    discounted_books = book_subtotal * discount_mult
    discounted_other = other_subtotal * discount_mult

    # Taxes:
    # - gift cards: never taxed
    # - food: untaxed
    # - others (including books): 8.25% tax after discounts
    taxable_amount = discounted_books + discounted_other
    tax = taxable_amount * 0.0825

    total = gift_card_subtotal + discounted_food + taxable_amount + tax

    # Banker's rounding (ROUND_HALF_EVEN) to cents at the end only
    total_dec = Decimal(str(total)).quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)
    return float(total_dec)
