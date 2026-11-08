def checkout_total(items, coupons=(), student=False):
    for c in coupons:
        if c < 0 or c > 100:
            raise ValueError(f"Invalid coupon percentage: {c}")

    # Validate items
    for item in items:
        if item.get('qty', 0) < 0:
            raise ValueError(f"Negative quantity: {item.get('qty')}")

    # Expand books into individual units to apply buy 2 get 1 free
    # Rule: buy 2 books get the cheapest 3rd book free (per group of 3, cheapest first)
    books = []
    gift_card_total = 0.0
    food_items = []  # list of unit prices
    other_taxable_non_book = []  # list of unit prices

    for item in items:
        qty = item.get('qty', 0)
        if qty == 0:
            continue
        price = float(item['price'])
        kind = item.get('kind')

        if kind == 'book':
            books.extend([price] * qty)
        elif kind == 'gift_card':
            gift_card_total += price * qty
        elif kind == 'food':
            food_items.extend([price] * qty)
        else:
            # other taxable goods
            other_taxable_non_book.extend([price] * qty)

    # Process books
    # Sort books ascending so the cheapest books can be determined.
    # "buy 2 books get the cheapest 3rd book free (per group of 3, cheapest first)"
    # For N books, there are N // 3 free books, which are the N // 3 cheapest books.
    books.sort()
    num_free = len(books) // 3
    # The first num_free books in ascending order are the cheapest
    # and thus made free.
    paid_books = books[num_free:]

    # Calculate discount factor
    # Coupons stack multiplicatively: (1 - c1/100) * (1 - c2/100)...
    factor = 1.0
    for c in coupons:
        factor *= (1.0 - c / 100.0)

    if student:
        factor *= 0.9

    # Combined discount is capped at 25% (i.e. factor cannot be less than 0.75)
    effective_factor = max(0.75, factor)

    # Discount applies to everything except gift cards
    # Food is untaxed
    # Books and other taxable items have 8.25% tax after discounts
    food_subtotal = sum(food_items) * effective_factor
    taxable_subtotal = (sum(paid_books) + sum(other_taxable_non_book)) * effective_factor
    tax = taxable_subtotal * 0.0825

    total = gift_card_total + food_subtotal + taxable_subtotal + tax
    return round(total, 2)
