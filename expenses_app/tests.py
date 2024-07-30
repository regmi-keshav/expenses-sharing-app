from rest_framework.test import APITestCase
from rest_framework import status
from .models import Expense, ExpenseSplit
from django.contrib.auth import get_user_model

User = get_user_model()  # This gets your custom user model


class ExpenseTests(APITestCase):

    def setUp(self):
        # Create users with required fields
        self.user1 = User.objects.create_user(
            email='user1@example.com', name='User One', mobile_number='1234567890', password='password')
        self.user2 = User.objects.create_user(
            email='user2@example.com', name='User Two', mobile_number='0987654321', password='password')
        self.user3 = User.objects.create_user(
            email='user3@example.com', name='User Three', mobile_number='1029384756', password='password')

    def test_create_expense_equal_split(self):
        url = '/api/expenses/'  # Update with your actual endpoint
        data = {
            'payer': self.user1.id,
            'total_amount': '3000.00',
            'split_method': 'equal',
            'description': 'Dinner',
            'date': '2024-08-25',
            'splits': [
                {'user': self.user1.id},
                {'user': self.user2.id},
                {'user': self.user3.id},
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        expense = Expense.objects.get(id=response_data['id'])
        self.assertEqual(expense.total_amount, 3000)
        self.assertEqual(expense.split_method, 'equal')
        splits = ExpenseSplit.objects.filter(expense=expense)
        self.assertEqual(splits.count(), 3)
        for split in splits:
            self.assertEqual(split.amount, 1000)
            self.assertIsNone(split.percentage)

    def test_create_expense_exact_split(self):
        url = '/api/expenses/'  # Update with your actual endpoint
        data = {
            'payer': self.user1.id,
            'total_amount': '4299.00',
            'split_method': 'exact',
            'description': 'Shopping',
            'date': '2024-08-25',
            'splits': [
                {'user': self.user1.id, 'amount': '799.00'},
                {'user': self.user2.id, 'amount': '2000.00'},
                {'user': self.user3.id, 'amount': '1500.00'},
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        expense = Expense.objects.get(id=response_data['id'])
        self.assertEqual(expense.total_amount, 4299)
        self.assertEqual(expense.split_method, 'exact')
        splits = ExpenseSplit.objects.filter(expense=expense)
        self.assertEqual(splits.count(), 3)
        self.assertEqual(splits[0].amount, 799)
        self.assertEqual(splits[1].amount, 2000)
        self.assertEqual(splits[2].amount, 1500)
        self.assertIsNone(splits[0].percentage)
        self.assertIsNone(splits[1].percentage)
        self.assertIsNone(splits[2].percentage)

    def test_create_expense_percentage_split(self):
        url = '/api/expenses/'  # Update with your actual endpoint
        data = {
            'payer': self.user1.id,
            'total_amount': '3000.00',
            'split_method': 'percentage',
            'description': 'Party',
            'date': '2024-08-25',
            'splits': [
                {'user': self.user1.id, 'percentage': '50.00'},
                {'user': self.user2.id, 'percentage': '25.00'},
                {'user': self.user3.id, 'percentage': '25.00'},
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        expense = Expense.objects.get(id=response_data['id'])
        self.assertEqual(expense.total_amount, 3000)
        self.assertEqual(expense.split_method, 'percentage')
        splits = ExpenseSplit.objects.filter(expense=expense)
        self.assertEqual(splits.count(), 3)
        self.assertEqual(splits[0].percentage, 50)
        self.assertEqual(splits[1].percentage, 25)
        self.assertEqual(splits[2].percentage, 25)
        self.assertEqual(splits[0].amount, 1500)
        self.assertEqual(splits[1].amount, 750)
        self.assertEqual(splits[2].amount, 750)
        self.assertIsNone(splits[0].amount)
        self.assertIsNone(splits[1].amount)
        self.assertIsNone(splits[2].amount)

    def test_invalid_split_method(self):
        url = '/api/expenses/'  # Update with your actual endpoint
        data = {
            'payer': self.user1.id,
            'total_amount': '3000.00',
            'split_method': 'invalid_method',
            'description': 'Invalid Split',
            'date': '2024-08-25',
            'splits': [
                {'user': self.user1.id, 'amount': '1500.00'},
                {'user': self.user2.id, 'amount': '1500.00'},
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertIn('split_method', response_data)

    def test_missing_splits_for_equal_split(self):
        url = '/api/expenses/'  # Update with your actual endpoint
        data = {
            'payer': self.user1.id,
            'total_amount': '3000.00',
            'split_method': 'equal',
            'description': 'Dinner',
            'date': '2024-08-25',
            'splits': []  # No splits provided
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertIn('splits', response_data)

    def test_mismatched_amounts_for_exact_split(self):
        url = '/api/expenses/'  # Update with your actual endpoint
        data = {
            'payer': self.user1.id,
            'total_amount': '3000.00',
            'split_method': 'exact',
            'description': 'Shopping',
            'date': '2024-08-25',
            'splits': [
                {'user': self.user1.id, 'amount': '1000.00'},
                {'user': self.user2.id, 'amount': '2000.00'},
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertIn(
            'The sum of exact amounts must equal the total amount.', response_data)

    def test_invalid_percentage_sum(self):
        url = '/api/expenses/'  # Update with your actual endpoint
        data = {
            'payer': self.user1.id,
            'total_amount': '3000.00',
            'split_method': 'percentage',
            'description': 'Party',
            'date': '2024-08-25',
            'splits': [
                {'user': self.user1.id, 'percentage': '50.00'},
                # Total is 90%, should be 100%
                {'user': self.user2.id, 'percentage': '40.00'},
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertIn('The sum of percentages must equal 100%.', response_data)
