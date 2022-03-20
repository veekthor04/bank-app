from django.urls import path

from user.views import CreateUserView, CreateTokenView, ProfileUserView

app_name = "user"

urlpatterns = [
    path("signup/", CreateUserView.as_view(), name="signup"),
    path("login/", CreateTokenView.as_view(), name="login"),
    path("profile/", ProfileUserView.as_view(), name="profile"),
]
