import unittest
from checkout import checkout_total


class TestCheckoutTotal(TestCase := unittest.TestCase):
    def test_empty_items(self):
        self.assertEqual(checkout_total([]), 0.0)
        self.assertEqual(checkout_total([], student=True), 0.0)

    def test_food_no_discount_no_tax(self):
        items = [{"name": "Apple", "price": 2.50, "qty": 4, "kind": "food"}]
        # 2.50 * 4 = 10.00, no tax
        self.assertEqual(checkout_total(items, student=False), 10.0)

    def test_food_student_discount_no_tax(self):
        items = [{"name": "Apple", "price": 2.50, "qty": 4, "kind": "food"}]
        # 2.50 * 4 * 0.9 = 9.00, no tax
        self.assertEqual(checkout_total(items, student=True), 9.0)

    def test_book_no_discount_with_tax(self):
        items = [{"name": "Novel", "price": 10.00, "qty": 1, "kind": "book"}]
        # 10.00 + 8% tax = 10.80
        self.assertEqual(checkout_total(items, student=False), 10.8)

    def test_book_student_discount_with_tax(self):
        items = [{"name": "Textbook", "price": 100.00, "qty": 1, "kind": "book"}]
        # 100.00 * 0.9 = 90.00; 90.00 * 1.08 = 97.20
        self.assertEqual(checkout_total(items, student=True), 97.2)

    def test_gift_card_no_student_discount(self):
        items = [{"name": "Store Card", "price": 50.00, "qty": 1, "kind": "gift_card"}]
        # Gift cards do not get student discount; non-food has 8% tax: 50.00 * 1.08 = 54.00
        self.assertEqual(checkout_total(items, student=False), 54.0)
        self.assertEqual(checkout_total(items, student=True), 54.0)

    def test_mixed_cart(self):
        items = [
            {"name": "Bread", "price": 3.00, "qty": 2, "kind": "food"},        # 6.00 -> 5.40 (no tax)
            {"name": "Python Book", "price": 20.00, "qty": 1, "kind": "book"},  # 20.00 -> 18.00 * 1.08 = 19.44
            {"name": "Gift Card", "price": 25.00, "qty": 1, "kind": "gift_card"} # 25.00 -> 25.00 * 1.08 = 27.00
        ]
        # Total: 5.40 + 19.44 + 27.00 = 51.84
        self.assertEqual(checkout_total(items, student=True), 51.84)

    def test_zero_quantity(self):
        items = [{"name": "Free Sample", "price": 5.00, "qty": 0, "kind": "book"}]
        self.assertEqual(checkout_total(items), 0.0)

    def test_negative_quantity_raises_value_error(self):
        items = [{"name": "Invalid Item", "price": 10.00, "qty": -1, "kind": "food"}]
        with self.assertRaises(ValueError):
            checkout_total(items)

    def test_rounding_to_cents(self):
        items = [{"name": "Odd Book", "price": 12.99, "qty": 3, "kind": "book"}]
        # 12.99 * 3 = 38.97; 10% off = 35.073; 8% tax = 2.80584; total = 37.87884 -> 37.88
        self.assertEqual(checkout_total(items, student=True), 37.88)


if __name__ == "__main__":
    unittest.main()
