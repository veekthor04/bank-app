from django.urls import path

from bank.views import TransferListView, make_transfer, add_fund, remove_fund

app_name = "bank"

urlpatterns = [
    path(
        "<str:account_id>/list",
        TransferListView.as_view(),
        name="transfer-list",
    ),
    path("transfer/", make_transfer, name="transfer-make"),
    path(
        "<str:account_id>/add",
        add_fund,
        name="fund-add",
    ),
    path(
        "<str:account_id>/retire",
        remove_fund,
        name="fund-retire",
    ),
]
