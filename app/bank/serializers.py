from decimal import Decimal
from rest_framework import serializers

from core.models import Bank, Account, Transfer


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        exclude = ["id"]


class AccountSerializer(serializers.ModelSerializer):
    bank = BankSerializer()

    class Meta:
        model = Account
        exclude = ["id"]


class TransferSerializer(serializers.ModelSerializer):
    """Transfer Serializer"""

    src_bank = BankSerializer(required=False)
    dst_bank = BankSerializer(required=False)
    source = AccountSerializer(required=False)
    destination = AccountSerializer(required=False)

    # setting $1 to be min transfer
    amount = serializers.DecimalField(
        required=True, decimal_places=2, max_digits=18, min_value=1.00
    )

    class Meta:
        model = Transfer
        exclude = ["id"]
        depth = 2

    def create(self, validated_data):
        return super().create(validated_data)


class FundSerializer(TransferSerializer):
    """Transer serializer for add fund and remove fund transfer type"""

    src_bank = serializers.SlugRelatedField(
        slug_field="uuid", queryset=Bank.objects.all(), required=False
    )

    dst_bank = serializers.SlugRelatedField(
        slug_field="uuid", queryset=Bank.objects.all(), required=False
    )

    source = serializers.SlugRelatedField(
        slug_field="uuid", queryset=Account.objects.all(), required=False
    )

    destination = serializers.SlugRelatedField(
        slug_field="uuid", queryset=Account.objects.all(), required=False
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        source: Account = attrs.get("source")
        amount: Decimal = attrs.get("amount")
        transfer_type = attrs.get("transfer_type")

        # validates that balance is sufficient for a remove fund
        if (
            transfer_type == Transfer.REMOVE_FUND
            and not source.is_balance_sufficient(amount)
        ):
            raise serializers.ValidationError(
                {"source": "Account does not have enough fund"}
            )

        return attrs


class IntraBankTransferSerializer(TransferSerializer):
    """Transer serializer for intra bank transfer type"""

    source = serializers.SlugRelatedField(
        slug_field="uuid", queryset=Account.objects.all()
    )

    destination = serializers.SlugRelatedField(
        slug_field="uuid", queryset=Account.objects.all()
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        source: Account = attrs.get("source")
        destination: Account = attrs.get("destination")
        amount: Decimal = attrs.get("amount")

        # validates for intra-bank transfer
        if not source.is_intra_bank_account(destination):
            raise serializers.ValidationError(
                {"source": "Source bank does not match with destination bank"}
            )

        # validates that balance is sufficient
        elif not source.is_balance_sufficient(amount):
            raise serializers.ValidationError(
                {"source": "Account does not have enough fund"}
            )

        return attrs
