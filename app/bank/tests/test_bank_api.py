from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.db.models import Q

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Transfer, Bank, Account
from core.utils import sample_bank, sample_account, sample_transfer

from bank.serializers import (
    TransferSerializer,
    BankSerializer,
    AccountSerializer,
)


BANK_LIST_URL = reverse("bank:bank-list")
TRANSFER_MAKE_URL = reverse("bank:transfer-make")


def bank_account_list_url(bank_id: str):
    """Return the list account URL for a bank"""
    return reverse("bank:bank-account-list", args=[bank_id])


def account_transfer_list_url(account_id: str):
    """Return the list transfer URL for an account"""
    return reverse("bank:transfer-list", args=[account_id])


def account_fund_add_url(account_id: str):
    """Return the fund add URL for an account"""
    return reverse("bank:fund-add", args=[account_id])


def account_fund_retire_url(account_id: str):
    """Return the fund retire URL for an account"""
    return reverse("bank:fund-retire", args=[account_id])


class PublicBankAPITests(TestCase):
    """Test the unauthenticated bank api access"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required to access API"""
        url = account_transfer_list_url("test_id")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBankAPITests(TestCase):
    """Test the authenticated bank api access"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            username="testuser",
            email="test@test.com",
            password="Testpassword123",
        )
        self.client.force_authenticate(user=self.user)

    def test_bank_list_success(self):
        """Test Bank list"""

        sample_bank()
        sample_bank()

        res = self.client.get(BANK_LIST_URL)

        banks = Bank.objects.all()
        serializer = BankSerializer(banks, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_bank_account_list_success(self):
        """Test bank account list"""
        test_bank = sample_bank()
        test_bank_id = str(test_bank.uuid)

        sample_account(bank=test_bank, balance=20)
        sample_account(bank=test_bank, balance=20)

        url = bank_account_list_url(test_bank_id)
        res = self.client.get(url)

        accounts = Account.objects.filter(bank__uuid=test_bank_id)
        serializer = AccountSerializer(accounts, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_transfer_list_success(self):
        """Test transfer list for an account"""
        test_bank = sample_bank()

        test_account_1 = sample_account(bank=test_bank, balance=20)
        test_account_id = str(test_account_1.uuid)

        test_account_2 = sample_account(bank=test_bank, balance=20)

        sample_transfer(
            source=test_account_1,
            destination=test_account_2,
            amount=5,
            transfer_type=Transfer.INTRA_BANK_TRANSFER,
        )
        sample_transfer(
            source=test_account_2,
            destination=test_account_1,
            amount=3,
            transfer_type=Transfer.INTRA_BANK_TRANSFER,
        )

        url = account_transfer_list_url(test_account_id)
        res = self.client.get(url)

        transfers = Transfer.objects.filter(
            Q(source__uuid=test_account_id)
            | Q(destination__uuid=test_account_id)
        )
        serializer = TransferSerializer(transfers, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_transfer_list_not_found(self):
        """Test transfer list for an incorrect account"""

        test_account_id = "test-id"

        url = account_transfer_list_url(test_account_id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_make_transfer_success(self):
        """Test transfer make"""

        test_bank = sample_bank()

        test_account_1 = sample_account(bank=test_bank, balance=20)
        test_account_1_id = str(test_account_1.uuid)

        test_account_2 = sample_account(bank=test_bank, balance=20)
        test_account__2id = str(test_account_2.uuid)

        payload = {
            "source": test_account_1_id,
            "destination": test_account__2id,
            "amount": 10,
            "info": "test info",
        }
        res = self.client.put(TRANSFER_MAKE_URL, payload)

        test_account_1.refresh_from_db()
        test_account_2.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(test_account_1.balance, 10)
        self.assertEqual(test_account_2.balance, 30)

    def test_make_transfer_not_enough_fund(self):
        """Test transfer make when fund is not available"""

        test_bank = sample_bank()

        test_account_1 = sample_account(bank=test_bank, balance=5)
        test_account_1_id = str(test_account_1.uuid)

        test_account_2 = sample_account(bank=test_bank, balance=20)
        test_account__2id = str(test_account_2.uuid)

        payload = {
            "source": test_account_1_id,
            "destination": test_account__2id,
            "amount": 10,
            "info": "test info",
        }
        res = self.client.put(TRANSFER_MAKE_URL, payload)

        test_account_1.refresh_from_db()
        test_account_2.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(test_account_1.balance, 5)
        self.assertEqual(test_account_2.balance, 20)

    def test_make_transfer_bank_does_not_match(self):
        """Test transfer make when banks do not match"""

        test_bank_1 = sample_bank()
        test_bank_2 = sample_bank()

        test_account_1 = sample_account(bank=test_bank_1, balance=20)
        test_account_1_id = str(test_account_1.uuid)

        test_account_2 = sample_account(bank=test_bank_2, balance=20)
        test_account__2id = str(test_account_2.uuid)

        payload = {
            "source": test_account_1_id,
            "destination": test_account__2id,
            "amount": 10,
            "info": "test info",
        }
        res = self.client.put(TRANSFER_MAKE_URL, payload)

        test_account_1.refresh_from_db()
        test_account_2.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(test_account_1.balance, 20)
        self.assertEqual(test_account_2.balance, 20)

    def test_fund_add_success(self):
        """Test fund add"""

        test_bank = sample_bank()

        test_account = sample_account(bank=test_bank, balance=20)
        test_account_id = str(test_account.uuid)

        payload = {
            "src_bank": test_bank.uuid,
            "amount": 10,
            "info": "test info",
        }
        url = account_fund_add_url(test_account_id)
        res = self.client.put(url, payload)

        test_account.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(test_account.balance, 30)

    def test_fund_add_non_existing_account(self):
        """Test transfer list for a non existing account"""

        test_bank = sample_bank()

        test_account_id = "test-id"

        payload = {
            "src_bank": test_bank.uuid,
            "amount": 10,
            "info": "test info",
        }
        url = account_fund_add_url(test_account_id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fund_retire_success(self):
        """Test fund retire"""

        test_bank = sample_bank()

        test_account = sample_account(bank=test_bank, balance=20)
        test_account_id = str(test_account.uuid)

        payload = {
            "dst_bank": test_bank.uuid,
            "amount": 10,
            "info": "test info",
        }
        url = account_fund_retire_url(test_account_id)
        res = self.client.put(url, payload)

        test_account.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(test_account.balance, 10)

    def test_fund_retire_non_existing_account(self):
        """Test transfer retire for a non existing account"""

        test_bank = sample_bank()

        test_account_id = "test-id"

        payload = {
            "dst_bank": test_bank.uuid,
            "amount": 10,
            "info": "test info",
        }
        url = account_fund_retire_url(test_account_id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fund_retire_fund_not_enough_fund(self):
        """Test fund retire when fund is not enough"""

        test_bank = sample_bank()

        test_account = sample_account(bank=test_bank, balance=5)
        test_account_id = str(test_account.uuid)

        payload = {
            "dst_bank": test_bank.uuid,
            "amount": 10,
            "info": "test info",
        }
        url = account_fund_retire_url(test_account_id)
        res = self.client.put(url, payload)

        test_account.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(test_account.balance, 5)
