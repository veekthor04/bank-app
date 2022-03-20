from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import Http404

from rest_framework import generics, status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.models import Transfer, Account, Bank
from bank.serializers import (
    BankSerializer,
    AccountSerializer,
    TransferSerializer,
    FundSerializer,
    IntraBankTransferSerializer,
)


class BankListView(generics.ListAPIView):
    """Bank list"""

    serializer_class = BankSerializer
    permission_classes = [IsAuthenticated]
    queryset = Bank.objects.all()
    my_tags = ["Bank"]


class BankAccountListView(generics.ListAPIView):
    """Bank Account list for a bank"""

    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    queryset = Transfer.objects.all()
    lookup_field = "bank_id"
    my_tags = ["Account"]

    def get_queryset(self):
        if self.lookup_field is None:
            return None
        bank_id = self.kwargs[self.lookup_field]

        try:
            queryset = Account.objects.filter(bank__uuid=bank_id)
        except ValidationError:
            raise Http404

        return queryset


class TransferListView(generics.ListAPIView):
    """Transfer list for an account"""

    serializer_class = TransferSerializer
    permission_classes = [IsAuthenticated]
    queryset = Transfer.objects.all()
    lookup_field = "account_id"
    my_tags = ["Transfer"]

    def get_queryset(self):
        if self.lookup_field is None:
            return None
        account_id = self.kwargs[self.lookup_field]

        try:
            queryset = Transfer.objects.filter(
                Q(source__uuid=account_id) | Q(destination__uuid=account_id)
            )
        except ValidationError:
            raise Http404

        return queryset


@swagger_auto_schema(
    method="put",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "source": openapi.Schema(
                type=openapi.TYPE_STRING, description="($uuid) title: Source"
            ),
            "destination": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="($uuid) title: Destination",
            ),
            "amount": openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description="($decimal) title: Amount",
            ),
            "info": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="title: Info maxLength: 255",
            ),
        },
    ),
    responses={
        201: openapi.Response("Success", IntraBankTransferSerializer),
        400: "Bad Request",
    },
    operation_description="Intra-bank transfer from one account to another",
    tags=[
        "Transfer",
    ],
)
@permission_classes(IsAuthenticated)
@api_view(["PUT"])
def make_transfer(request):
    """Transfers fund from one account to another within the same bank"""

    # copy request data, set transfer type to intra bank transfer
    data = request.data.copy()
    data.update({"transfer_type": Transfer.INTRA_BANK_TRANSFER})

    serializer = IntraBankTransferSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="put",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "src_bank": openapi.Schema(
                type=openapi.TYPE_STRING, description="($uuid) title: Src bank"
            ),
            "amount": openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description="($decimal) title: Amount",
            ),
            "info": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="title: Info maxLength: 255",
            ),
        },
        required=["amount", "info"],
    ),
    responses={
        201: openapi.Response("Success", FundSerializer),
        400: "Bad Request",
    },
    operation_description="Add fund to an account",
    tags=[
        "Transfer",
    ],
)
@permission_classes(IsAuthenticated)
@api_view(["PUT"])
def add_fund(request, account_id):
    """Adds fund to an account"""

    # set fund type and account to data
    data = request.data.copy()
    data.update(
        {"destination": account_id, "transfer_type": Transfer.ADD_FUND}
    )

    # request.data._mutable = True
    # request.data.update(
    #     {"account": account_id, "transfer_type": Transfer.ADD_FUND}
    # )
    # request.data._mutable = False

    serializer = FundSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="put",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "dst_bank": openapi.Schema(
                type=openapi.TYPE_STRING, description="($uuid) title: Dst bank"
            ),
            "amount": openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description="($decimal) title: Amount",
            ),
            "info": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="title: Info maxLength: 255",
            ),
        },
    ),
    responses={
        201: openapi.Response("Success", FundSerializer),
        400: "Bad Request",
    },
    operation_description="Removes fund from an account",
    tags=[
        "Transfer",
    ],
)
@permission_classes(IsAuthenticated)
@api_view(["PUT"])
def remove_fund(request, account_id):
    """Removes fund from an account"""

    # copy request data, set fund type to remove fund and account to data
    data = request.data.copy()
    data.update({"source": account_id, "transfer_type": Transfer.REMOVE_FUND})

    serializer = FundSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
