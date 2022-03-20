from rest_framework import generics, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


# Create your views here.
class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = UserSerializer
    my_tags = ["Authentication"]


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    my_tags = ["Authentication"]


class ProfileUserView(generics.RetrieveUpdateAPIView):
    """Retrieves and edits the authenticated user's profile"""

    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    my_tags = ["Authentication"]

    def get_object(self):
        """Retrieve and return authentication user"""
        return self.request.user
