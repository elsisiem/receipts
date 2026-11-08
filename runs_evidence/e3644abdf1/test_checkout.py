import unittest
from checkout import checkout_total


class TestCheckoutTotal(unittest.TestCase):
    def test_empty_cart(self):
        self.assertEqual(checkout_total([]), 0.0)

    def test_negative_quantity_raises(self):
        items = [{'name': 'Apple', 'price': 1.0, 'qty': -1, 'kind': 'food'}]
        with self.assertRaises(ValueError):
            checkout_total(items)

    def test_coupon_over_100_raises(self):
        items = [{'name': 'Apple', 'price': 1.0, 'qty': 1, 'kind': 'food'}]
        with self.assertRaises(ValueError):
            checkout_total(items, coupons=[101])

    def test_negative_coupon_raises(self):
        items = [{'name': 'Apple', 'price': 1.0, 'qty': 1, 'kind': 'food'}]
        with self.assertRaises(ValueError):
            checkout_total(items, coupons=[-5])

    def test_gift_cards_no_tax_no_discount(self):
        items = [{'name': 'GC', 'price': 50.0, 'qty': 2, 'kind': 'gift_card'}]
        # Total: 100.0, no discounts or taxes despite coupons and student flag
        self.assertEqual(checkout_total(items, coupons=[20], student=True), 100.0)

    def test_food_untaxed_with_discount(self):
        # 10% coupon on food of $20.00 -> $18.00
        items = [{'name': 'Bread', 'price': 20.0, 'qty': 1, 'kind': 'food'}]
        self.assertEqual(checkout_total(items, coupons=[10]), 18.0)

    def test_discount_cap_at_25_percent(self):
        # 20% + 20% = 1 - (0.8 * 0.8) = 36% discount -> capped at 25%
        # 100.0 food -> 75.0
        items = [{'name': 'Steak', 'price': 100.0, 'qty': 1, 'kind': 'food'}]
        self.assertEqual(checkout_total(items, coupons=[20, 20]), 75.0)

    def test_student_discount_and_cap(self):
        # 10% coupon -> factor = 0.9
        # student 10% -> factor = 0.9 * 0.9 = 0.81 (19% discount)
        # 100 food -> 81.0
        items = [{'name': 'Groceries', 'price': 100.0, 'qty': 1, 'kind': 'food'}]
        self.assertEqual(checkout_total(items, coupons=[10], student=True), 81.0)

        # 20% coupon + student -> factor = 0.8 * 0.9 = 0.72 (28% discount -> capped at 25%)
        self.assertEqual(checkout_total(items, coupons=[20], student=True), 75.0)

    def test_book_b2g1_cheapest_free(self):
        # 3 books: 10, 20, 30. Cheapest (10) free. Paid: 20 + 30 = 50.
        # Books taxed at 8.25%: 50 * 1.0825 = 54.125 -> rounds to 54.12 (banker's round half to even)
        items = [
            {'name': 'B1', 'price': 30.0, 'qty': 1, 'kind': 'book'},
            {'name': 'B2', 'price': 10.0, 'qty': 1, 'kind': 'book'},
            {'name': 'B3', 'price': 20.0, 'qty': 1, 'kind': 'book'},
        ]
        self.assertEqual(checkout_total(items), 54.12)

    def test_book_b2g1_multiple_groups(self):
        # 7 books: 5, 10, 15, 20, 25, 30, 35 -> 7 // 3 = 2 free books (5 and 10).
        # Paid books: 15 + 20 + 25 + 30 + 35 = 125.
        # Tax: 125 * 1.0825 = 135.3125 -> rounds to 135.31
        items = [
            {'name': f'B{i}', 'price': float(p), 'qty': 1, 'kind': 'book'}
            for i, p in enumerate([35, 10, 25, 5, 30, 15, 20])
        ]
        self.assertEqual(checkout_total(items), 135.31)

    def test_mixed_cart_with_bankers_rounding(self):
        # Book: qty 3 @ 10.0 -> 1 free -> paid 20.0
        # Food: qty 1 @ 15.0
        # GC: qty 1 @ 25.0
        # Coupon: 10% -> discount 10%
        # Discounted book = 20.0 * 0.9 = 18.0; tax = 18.0 * 0.0825 = 1.485
        # Discounted food = 15.0 * 0.9 = 13.5
        # GC = 25.0
        # Total = 25.0 + 13.5 + 18.0 + 1.485 = 57.985
        # Banker's rounding on 57.985 -> round to even cents -> 57.98
        items = [
            {'name': 'Book', 'price': 10.0, 'qty': 3, 'kind': 'book'},
            {'name': 'Snack', 'price': 15.0, 'qty': 1, 'kind': 'food'},
            {'name': 'Card', 'price': 25.0, 'qty': 1, 'kind': 'gift_card'},
        ]
        self.assertEqual(checkout_total(items, coupons=[10]), 57.98)

    def test_zero_quantity_item(self):
        items = [
            {'name': 'Book', 'price': 10.0, 'qty': 0, 'kind': 'book'},
            {'name': 'Food', 'price': 10.0, 'qty': 2, 'kind': 'food'},
        ]
        self.assertEqual(checkout_total(items), 20.0)


if __name__ == '__main__':
    unittest.main()
