from django.db.models import Q
from django.test import TestCase
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapps2023.settings')
django.setup()
from django.urls import reverse
from register.models import User
from payapp.models import Transaction, TransactionRequest
from rest_framework.test import APITestCase, APIClient
from rest_framework import status


class TransactionViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com', username='user1', password='password123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com', username='user2', password='password123'
        )

    def test_transaction_list_view(self):
        url = reverse('payapp:transactions')
        self.client.login(email='user1@example.com', password='password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        tran = Transaction.objects.filter(Q(sender=self.user1)
                                          | Q(receiver=self.user2))
        self.assertTrue(response, tran)


class TransactionCreateViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com', username="user1", password='password123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com', username="user2", password='password123'
        )

    def test_get(self):
        self.client.login(email='user1@example.com', password='password123')
        response = self.client.get(reverse('payapp:transaction-create'))
        self.assertEqual(response.status_code, 200)

    def test_post_success(self):
        self.client.login(email='user1@example.com', password='password123')
        data = {'email': 'user2@example.com', 'amount': '50'}
        response = self.client.post(reverse('payapp:transaction-create'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('payapp:transactions'))

    def test_post_missing_parameters(self):
        self.client.login(email='user1@example.com', password='password123')
        data = {'email': 'user2@example.com'}
        response = self.client.post(reverse('payapp:transaction-create'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('payapp:transaction-create'))

    def test_post_no_receiver(self):
        self.client.login(email='user1@example.com', password='password123')
        data = {'email': 'user3@example.com', 'amount': '50'}
        response = self.client.post(reverse('payapp:transaction-create'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('payapp:transaction-create'))

    def test_post_same_user(self):
        self.client.login(email='user1@example.com', password='password123')
        data = {'email': 'user1@example.com', 'amount': '50'}
        response = self.client.post(reverse('payapp:transaction-create'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('payapp:transaction-create'))

    def test_post_insufficient_balance(self):
        self.client.login(email='user1@example.com', password='password123')
        data = {'email': 'user2@example.com', 'amount': '150'}
        response = self.client.post(reverse('payapp:transaction-create'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('payapp:transactions'))


class RequestTransactionListViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com', username='user1', password='password123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com', username='user2', password='password123'
        )

    def test_transaction_list_view(self):
        url = reverse('payapp:requests')
        self.client.login(email='user1@example.com', password='password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        tran = TransactionRequest.objects.filter(Q(sender=self.user1) | Q(receiver=self.user2))
        self.assertTrue(response, tran)


class RequestTransactionCreateViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com', username="user1", password='password123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com', username="user2", password='password123'
        )

    def test_get(self):
        self.client.login(email='user1@example.com', password='password123')
        response = self.client.get(reverse('payapp:request-create'))
        self.assertEqual(response.status_code, 200)

    def test_post_success(self):
        self.client.login(email='user1@example.com', password='password123')
        data = {'email': 'user2@example.com', 'amount': '50'}
        response = self.client.post(reverse('payapp:request-create'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('payapp:requests'))

    def test_post_missing_parameters(self):
        self.client.login(email='user1@example.com', password='password123')
        data = {'email': 'user2@example.com'}
        response = self.client.post(reverse('payapp:request-create'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('payapp:request-create'))

    def test_post_no_receiver(self):
        self.client.login(email='user1@example.com', password='password123')
        data = {'email': 'user3@example.com', 'amount': '50'}
        response = self.client.post(reverse('payapp:request-create'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('payapp:request-create'))

    def test_post_same_user(self):
        self.client.login(email='user1@example.com', password='password123')
        data = {'email': 'user1@example.com', 'amount': '50'}
        response = self.client.post(reverse('payapp:request-create'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('payapp:request-create'))

    def test_post_insufficient_balance(self):
        self.client.login(email='user1@example.com', password='password123')
        data = {'email': 'user2@example.com', 'amount': '150'}
        response = self.client.post(reverse('payapp:request-create'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('payapp:requests'))


class TransactionRequestUpdateViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@example.com', username="user1", password='password123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com', username="user2", password='password123'
        )
        self.transaction_request = TransactionRequest.objects.create(
            sender=self.user1, receiver=self.user2, amount=100, status='pending'
        )

    def test_transaction_request_update_view_approve(self):
        url = reverse('payapp:request-update', args=[self.transaction_request.pk])
        self.client.login(email='user2@example.com', password='password123')
        response = self.client.get(url, {'status': 'approved'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('payapp:requests'))
        self.transaction_request.refresh_from_db()
        self.assertEqual(self.transaction_request.status, 'accepted')
        self.assertIsNotNone(self.transaction_request.checked_on)

    def test_transaction_request_update_view_cancel(self):
        url = reverse('payapp:request-update', args=[self.transaction_request.pk])
        self.client.login(email='user2@example.com', password='password123')
        response = self.client.get(url, {'status': 'cancel'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('payapp:requests'))
        self.transaction_request.refresh_from_db()
        self.assertEqual(self.transaction_request.status, 'cancelled')
        self.assertIsNotNone(self.transaction_request.checked_on)

    def test_transaction_request_update_view_invalid_status(self):
        url = reverse('payapp:request-update', args=[self.transaction_request.pk])
        self.client.login(email='user2@example.com', password='password123')
        response = self.client.get(url, {'status': 'invalid'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('payapp:requests'))
        self.transaction_request.refresh_from_db()
        self.assertEqual(self.transaction_request.status, 'pending')
        self.assertIsNone(self.transaction_request.checked_on)


class CurrencyConversionAPITestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user2@example.com', username="user1", password='password123'
        )
        self.client = APIClient()

    def test_conversion_valid_currencies(self):
        self.client.login(email='user2@example.com', password='password123')
        response = self.client.get('/conversion/USD/EURO/100/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], 83.0)

    def test_currency_not_supported(self):
        self.client.login(email='user2@example.com', password='password123')
        response = self.client.get('/conversion/USD/JPY/10/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Only USD, EURO and GBP are supported')

    def test_conversion_invalid_amount(self):
        self.client.login(email='user2@example.com', password='password123')
        response = self.client.get('/conversion/USD/EURO/abc/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Amount must be number (integer, float)')

    def test_conversion_negative_amount(self):
        self.client.login(email='user2@example.com', password='password123')
        response = self.client.get('/conversion/USD/EURO/-100/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['error'], 'Amount must be numeric and greater than 0')
