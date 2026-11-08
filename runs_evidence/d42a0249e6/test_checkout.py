import unittest
from checkout import checkout_total

class TestCheckoutTotal(unittest.TestCase):
    def test_validation_negative_qty(self):
        with self.assertRaises(ValueError):
            checkout_total([{'name': 'Apple', 'price': 1.0, 'qty': -1, 'kind': 'food'}])

    def test_validation_coupon_over_100(self):
        with self.assertRaises(ValueError):
            checkout_total([], coupons=[105])

    def test_validation_coupon_negative(self):
        with self.assertRaises(ValueError):
            checkout_total([], coupons=[-5])

    def test_gift_card_no_discount_no_tax(self):
        items = [{'name': 'GC', 'price': 50.0, 'qty': 2, 'kind': 'gift_card'}]
        total = checkout_total(items, coupons=[20], student=True)
        self.assertEqual(total, 100.0)

    def test_food_no_tax_with_discount(self):
        items = [{'name': 'Bread', 'price': 10.0, 'qty': 2, 'kind': 'food'}]
        # 20.0 * (1 - 0.10) = 18.0
        total = checkout_total(items, coupons=[10])
        self.assertEqual(total, 18.0)

    def test_buy_2_books_get_cheapest_free(self):
        # 3 books: 10, 20, 30. Cheapest is 10 (free). Paid: 20 + 30 = 50.
        # Tax: 50 * 0.0825 = 4.125. Total = 54.125 -> round to 54.12
        items = [
            {'name': 'B1', 'price': 10.0, 'qty': 1, 'kind': 'book'},
            {'name': 'B2', 'price': 20.0, 'qty': 1, 'kind': 'book'},
            {'name': 'B3', 'price': 30.0, 'qty': 1, 'kind': 'book'},
        ]
        total = checkout_total(items)
        self.assertEqual(total, 54.12)

    def test_six_books_two_cheapest_free(self):
        # 6 books: 5, 10, 15, 20, 25, 30. Cheapest 2 are 5 and 10 (free).
        # Paid: 15 + 20 + 25 + 30 = 90.0
        # Tax: 90 * 0.0825 = 7.425. Total = 97.425 -> round to 97.42
        items = [
            {'name': 'B', 'price': 5.0, 'qty': 1, 'kind': 'book'},
            {'name': 'B', 'price': 10.0, 'qty': 1, 'kind': 'book'},
            {'name': 'B', 'price': 15.0, 'qty': 1, 'kind': 'book'},
            {'name': 'B', 'price': 20.0, 'qty': 1, 'kind': 'book'},
            {'name': 'B', 'price': 25.0, 'qty': 1, 'kind': 'book'},
            {'name': 'B', 'price': 30.0, 'qty': 1, 'kind': 'book'},
        ]
        total = checkout_total(items)
        self.assertEqual(total, 97.42)

    def test_coupon_multiplicative_and_cap(self):
        # 10% and 10% coupon: factor = 0.9 * 0.9 = 0.81 (19% off)
        items = [{'name': 'Item', 'price': 100.0, 'qty': 1, 'kind': 'food'}]
        total = checkout_total(items, coupons=[10, 10])
        self.assertEqual(total, 81.0)

        # 20% and 10% coupon: factor = 0.8 * 0.9 = 0.72 -> capped at 0.75 (25% off)
        total_capped = checkout_total(items, coupons=[20, 10])
        self.assertEqual(total_capped, 75.0)

    def test_student_discount_and_cap(self):
        # Student gives extra 10% after coupons
        # 10% coupon + student: 0.9 * 0.9 = 0.81 (19% off)
        items = [{'name': 'Item', 'price': 100.0, 'qty': 1, 'kind': 'food'}]
        total = checkout_total(items, coupons=[10], student=True)
        self.assertEqual(total, 81.0)

        # 20% coupon + student: 0.8 * 0.9 = 0.72 -> capped at 0.75
        total_capped = checkout_total(items, coupons=[20], student=True)
        self.assertEqual(total_capped, 75.0)

    def test_mixed_cart_with_bankers_rounding(self):
        # 1 food @ 15.00
        # 3 books @ 10.00 each -> 1 free, 2 paid = 20.00
        # 1 gift card @ 25.00
        # Coupons: 10%, student=False -> factor = 0.9
        # Food discounted: 15.00 * 0.9 = 13.50 (no tax)
        # Books discounted: 20.00 * 0.9 = 18.00
        # Books tax: 18.00 * 0.0825 = 1.485
        # Gift card: 25.00 (no discount, no tax)
        # Subtotal + tax: 13.50 + 18.00 + 1.485 + 25.00 = 57.985
        # Banker's rounding to 2 decimal places: 57.98
        items = [
            {'name': 'Salad', 'price': 15.0, 'qty': 1, 'kind': 'food'},
            {'name': 'Novels', 'price': 10.0, 'qty': 3, 'kind': 'book'},
            {'name': 'Voucher', 'price': 25.0, 'qty': 1, 'kind': 'gift_card'},
        ]
        total = checkout_total(items, coupons=[10])
        self.assertEqual(total, 57.98)

if __name__ == '__main__':
    unittest.main()
