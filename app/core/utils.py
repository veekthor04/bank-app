from decimal import Decimal

from django.contrib.auth import get_user_model

from drf_yasg.inspectors import SwaggerAutoSchema

from core.models import Bank, Account, Transfer


class CustomAutoSchema(SwaggerAutoSchema):
    """Custom SwaggerAutoSchema to add tags to views"""

    def get_tags(self, operation_keys=None) -> list:
        tags = self.overrides.get("tags", None) or getattr(
            self.view, "my_tags", []
        )
        if not tags:
            tags = [operation_keys[0]]

        return tags


def sample_bank(name: str = "testname") -> Bank:
    """Create a sample bank"""
    return Bank.objects.create(name=name)


def sample_account(
    bank: Bank, name: str = "testname", balance: Decimal = 0
) -> Account:
    """Create a sample bank"""
    return Account.objects.create(name=name, bank=bank, balance=balance)


def sample_transfer(**params) -> Transfer:
    """Create and return a sample recipe"""
    defaults = {
        "info": "test info",
    }
    defaults.update(params)

    return Transfer.objects.create(**defaults)


def sample_user(
    username="testuser", email="test@test.com", password="Testpassword_123"
):
    """Create a sample user"""
    return get_user_model().objects.create_user(
        username,
        email,
        password,
    )
