from django.urls import path

from bank.views import (
    BankListView,
    BankAccountListView,
    TransferListView,
    make_transfer,
    add_fund,
    remove_fund,
)

app_name = "bank"

urlpatterns = [
    path(
        "bank/",
        BankListView.as_view(),
        name="bank-list",
    ),
    path(
        "bank/<uuid:bank_id>/account/",
        BankAccountListView.as_view(),
        name="bank-account-list",
    ),
    path(
        "<uuid:account_id>/list/",
        TransferListView.as_view(),
        name="transfer-list",
    ),
    path("transfer/", make_transfer, name="transfer-make"),
    path(
        "<uuid:account_id>/add/",
        add_fund,
        name="fund-add",
    ),
    path(
        "<uuid:account_id>/retire/",
        remove_fund,
        name="fund-retire",
    ),
]
