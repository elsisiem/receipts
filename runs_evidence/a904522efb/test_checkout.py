import unittest
from checkout import checkout_total


class TestCheckoutTotal(unittest.TestCase):
    def test_empty_items(self):
        self.assertEqual(checkout_total([]), 0.0)
        self.assertEqual(checkout_total([], student=True), 0.0)

    def test_food_non_student(self):
        items = [{'name': 'Apple', 'price': 2.0, 'qty': 3, 'kind': 'food'}]
        # 2.0 * 3 = 6.0, no tax, no discount
        self.assertEqual(checkout_total(items), 6.0)

    def test_food_student(self):
        items = [{'name': 'Apple', 'price': 2.0, 'qty': 3, 'kind': 'food'}]
        # 6.0 * 0.9 = 5.4, no tax
        self.assertEqual(checkout_total(items, student=True), 5.4)

    def test_book_non_student(self):
        items = [{'name': 'Novel', 'price': 10.0, 'qty': 1, 'kind': 'book'}]
        # 10.0 * 1.08 = 10.8
        self.assertEqual(checkout_total(items), 10.8)

    def test_book_student(self):
        items = [{'name': 'Novel', 'price': 10.0, 'qty': 1, 'kind': 'book'}]
        # 10.0 * 0.9 * 1.08 = 9.72
        self.assertEqual(checkout_total(items, student=True), 9.72)

    def test_gift_card_non_student(self):
        items = [{'name': 'Card', 'price': 50.0, 'qty': 1, 'kind': 'gift_card'}]
        # 50.0 * 1.08 = 54.0
        self.assertEqual(checkout_total(items), 54.0)

    def test_gift_card_student(self):
        items = [{'name': 'Card', 'price': 50.0, 'qty': 1, 'kind': 'gift_card'}]
        # No student discount on gift cards; tax is 8% -> 50.0 * 1.08 = 54.0
        self.assertEqual(checkout_total(items, student=True), 54.0)

    def test_mixed_cart(self):
        items = [
            {'name': 'Bread', 'price': 3.50, 'qty': 2, 'kind': 'food'},       # 7.00 * 0.9 = 6.30 (tax-free)
            {'name': 'Book', 'price': 15.00, 'qty': 1, 'kind': 'book'},       # 15.00 * 0.9 * 1.08 = 14.58
            {'name': 'Gift', 'price': 25.00, 'qty': 1, 'kind': 'gift_card'},  # 25.00 * 1.08 = 27.00
        ]
        # Total: 6.30 + 14.58 + 27.00 = 47.88
        self.assertEqual(checkout_total(items, student=True), 47.88)

    def test_negative_quantity_raises_value_error(self):
        items = [{'name': 'Apple', 'price': 2.0, 'qty': -1, 'kind': 'food'}]
        with self.assertRaises(ValueError):
            checkout_total(items)

    def test_zero_quantity(self):
        items = [{'name': 'Apple', 'price': 2.0, 'qty': 0, 'kind': 'food'}]
        self.assertEqual(checkout_total(items), 0.0)


if __name__ == '__main__':
    unittest.main()
