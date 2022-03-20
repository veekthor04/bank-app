from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import Http404

from rest_framework import generics, status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.models import Transfer
from bank.serializers import (
    TransferSerializer,
    FundSerializer,
    IntraBankTransferSerializer,
)


class TransferListView(generics.ListAPIView):
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
            "source": openapi.Schema(type=openapi.TYPE_STRING),
            "destination": openapi.Schema(type=openapi.TYPE_STRING),
            "amount": openapi.Schema(type=openapi.TYPE_NUMBER),
            "info": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    responses={
        201: "Transfer was successful",
        404: "Not found.",
    },
    operation_description="Intra-bank transfer from one account to another",
    tags=[
        "Transfer",
    ],
)
@permission_classes(IsAuthenticated)
@api_view(["PUT"])
def make_transfer(request):

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
            "src_bank": openapi.Schema(type=openapi.TYPE_STRING),
            "amount": openapi.Schema(type=openapi.TYPE_NUMBER),
            "info": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    responses={
        201: "Fund was successful",
        404: "Not found.",
    },
    operation_description="Add fund to an account",
    tags=[
        "Fund",
    ],
)
@permission_classes(IsAuthenticated)
@api_view(["PUT"])
def add_fund(request, account_id):

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
            "dst_bank": openapi.Schema(type=openapi.TYPE_STRING),
            "amount": openapi.Schema(type=openapi.TYPE_NUMBER),
            "info": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    responses={
        201: "Fund was successfully",
        404: "Not found.",
    },
    operation_description="Removes fund from an account",
    tags=[
        "Fund",
    ],
)
@permission_classes(IsAuthenticated)
@api_view(["PUT"])
def remove_fund(request, account_id):

    # copy request data, set fund type to remove fund and account to data
    data = request.data.copy()
    data.update({"source": account_id, "transfer_type": Transfer.REMOVE_FUND})

    serializer = FundSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
