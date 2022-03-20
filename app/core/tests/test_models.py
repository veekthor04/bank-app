from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Account, Transfer
from core.utils import sample_bank, sample_account


def sample_user(
    username="testuser", email="test@test.com", password="Testpassword_123"
):
    """Create a sample user"""
    return get_user_model().objects.create_user(
        username,
        email,
        password,
    )


class ModelTests(TestCase):
    def test_create_user_successful(self):
        """ "Test creating a new user with an email is successful"""
        username = "testuser"
        email = "test@test.com"
        password = "Testpassword1234"
        user = get_user_model().objects.create_user(
            username=username, email=email, password=password
        )

        self.assertEqual(user.username, username)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_invalid_credentials(self):
        """Test creating with invalid credentials raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "testuser")

    def test_bank_str(self):
        """Test the bank string representation"""
        bank = sample_bank(name="testbankname")

        self.assertEqual(str(bank), f"name: {bank.name}, id: {bank.uuid}")

    def test_account_str(self):
        """Test the account string representation"""
        account = Account.objects.create(
            name="testaccountname", bank=sample_bank(name="testaccount")
        )

        self.assertEqual(
            str(account), f"name: {account.name}, id: {account.uuid}"
        )

    def test_is_intra_bank_account(self):
        """Test the is_intra_bank_account method returns true if the banks match
        and false if it does not"""
        bank_1 = sample_bank(name="bank_1")
        bank_2 = sample_bank(name="bank_2")

        account1: Account = sample_account(
            name="test_name_1", bank=bank_1
        )  # matching banks
        account2: Account = sample_account(
            name="test_name_2", bank=bank_1
        )  # matching banks

        account3: Account = sample_account(
            name="test_name_3", bank=bank_2
        )  # diff bank

        self.assertTrue(account1.is_intra_bank_account(account2))
        self.assertFalse(account1.is_intra_bank_account(account3))

    def test_is_balance_sufficient(self):
        """Test the is_balance_sufficient method returns true if account balance
        is sufficient and false is it does not"""

        account: Account = sample_account(
            bank=sample_bank("test_bank"), balance=10
        )

        self.assertTrue(account.is_balance_sufficient(5))
        self.assertFalse(account.is_balance_sufficient(50))

    def test_transfer_str(self):
        """Test the transfer string representation"""
        transfer = Transfer.objects.create(
            source=sample_account(
                name="testaccount1", bank=sample_bank("testtransfer1")
            ),
            destination=sample_account(
                name="testaccount1", bank=sample_bank("testtransfer2")
            ),
            transfer_type=Transfer.INTRA_BANK_TRANSFER,
            amount=100,
            info="test info",
        )

        self.assertEqual(str(transfer), f"Transfer of {transfer.amount}")
