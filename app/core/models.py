from decimal import Decimal
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class BaseModel(models.Model):
    """Base model that contains name and uuid"""

    name = models.CharField(max_length=150)
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )

    class Meta:
        ordering = ["-id"]
        abstract = True

    def __str__(self) -> str:
        return f"name: {self.name}, id: {self.uuid}"


class User(AbstractUser):
    """Custom user model"""

    email = models.EmailField(unique=True)


class Bank(BaseModel):
    """Bank model"""


class Account(BaseModel):
    """Account model"""

    bank = models.ForeignKey(
        Bank, on_delete=models.CASCADE, related_name="bank_account"
    )
    balance = models.DecimalField(
        decimal_places=2, max_digits=18, default=0.00
    )

    def is_intra_bank_account(self, destination: "Account") -> bool:
        """Check if account bank is same as destination bank

        Args:
            destination (Account): _description_

        Returns:
            bool: _description_
        """
        return self.bank == destination.bank

    def is_balance_sufficient(self, amount: Decimal) -> bool:
        """Check if account balance is enough for transaction

        Args:
            amount (Decimal): _description_

        Returns:
            bool: _description_
        """
        return self.balance - amount > 0


class Transfer(models.Model):
    """Transfer model"""

    ADD_FUND = "add_fund"
    REMOVE_FUND = "remove_fund"
    INTRA_BANK_TRANSFER = "intra_bank_transfer"

    TRANSFER_CHOICES = (
        (ADD_FUND, "Add Fund"),
        (REMOVE_FUND, "Remove Fund"),
        (INTRA_BANK_TRANSFER, "Intra_bank_transfer"),
    )

    source = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="source_account_transfer",
        null=True,
        blank=True,
    )
    destination = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="destination_account_transfer",
        null=True,
        blank=True,
    )

    src_bank = models.ForeignKey(
        Bank,
        on_delete=models.CASCADE,
        related_name="src_bank_transfer",
        null=True,
        blank=True,
    )
    dst_bank = models.ForeignKey(
        Bank,
        on_delete=models.CASCADE,
        related_name="dst_bank_transfer",
        null=True,
        blank=True,
    )

    amount = models.DecimalField(decimal_places=2, max_digits=18)
    info = models.CharField(max_length=255)
    transfer_type = models.CharField(max_length=255, choices=TRANSFER_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Transfer of {self.amount}"

    class Meta:
        ordering = ["-created"]

    def update_accounts(self) -> None:
        """Updates the connected accounts"""

        if self.transfer_type == self.INTRA_BANK_TRANSFER:
            self.source.balance -= self.amount
            self.source.save()

            self.destination.balance += self.amount
            self.destination.save()

        elif self.transfer_type == self.ADD_FUND:
            self.destination.balance += self.amount
            self.destination.save()

        elif self.transfer_type == self.REMOVE_FUND:
            self.source.balance -= self.amount
            self.source.save()
