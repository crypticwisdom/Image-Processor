import secrets
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from .serializers import ClientSerializer
from .utils import validate_email, validate_text, validate_password, list_of_extensions, list_of_content_types
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from account.models import Client, ValidatorBlock
from rest_framework.permissions import IsAuthenticated


"""
Even it sounds simple to be done, image check could be tricky. At least following actions should be done:

    - check size of image - width, height and size of itself;
    - check extension and name of image;
    - check content type;
    - limit amount of uploaded images;
    - limit access to uploaded images - better if user don't know where it is stored;
    - limit types of image extensions;
    - preferably change name of image;
Recommend change type of image explicitly after those checks, e.g. from PNG to JPG. Simple, but works well.
"""


class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            client_name = request.data.get('client_name', None)  # Required
            email = request.data.get('email', None)
            password, password_confirm = request.data.get('password', None), request.data.get('password_confirm', None)

            if not client_name:
                return Response({"detail": "'client_name' is required."}, status=HTTP_400_BAD_REQUEST)

            if not email:
                return Response({"detail": "'email' is required."}, status=HTTP_400_BAD_REQUEST)

            if not validate_email(email=email):
                return Response({"detail": "Invalid email format."}, status=HTTP_400_BAD_REQUEST)

            if not validate_text(text=client_name):
                return Response({"detail": "Service supports '-' and '_' special characters."},
                                status=HTTP_400_BAD_REQUEST)
            success, msg = validate_password(password=password)

            if not success:
                return Response({"detail": f"{msg}"}, status=HTTP_400_BAD_REQUEST)

            if not password_confirm:
                return Response({"detail": "Password Confirm field is required."}, status=HTTP_400_BAD_REQUEST)

            if password != password_confirm:
                return Response({"detail": "Passwords does not Match."}, status=HTTP_400_BAD_REQUEST)

            client_name = str(client_name).title()
            client_token = secrets.token_urlsafe(35)
            client = Client.objects.create_user(client_name=client_name,
                                                username=f"{client_name}",
                                                client_token=client_token,
                                                email=email, password=password)

            return Response({"detail": "Successfully created Client", "client_token": f"{client_token}",
                             "description": "Client token is used to make any request to the service, keep it safe."},
                            status=HTTP_200_OK)
        except (Exception,) as err:
            return Response({"detail": f"{err}"}, status=HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
        Login system for this service, is compulsory as users might want to have an interface for this service, so the
        user will login to have access to this service.
    """
    permission_classes = []

    def post(self, request):
        try:
            client_name = request.data.get('client_name', None)
            password = request.data.get('password', None)

            if not client_name:
                return Response({"detail": "'client_name' field is required."}, status=HTTP_400_BAD_REQUEST)

            if not password:
                return Response({"detail": "'password' field is required."}, status=HTTP_400_BAD_REQUEST)

            client_name = str(client_name).title()
            client = Client.objects.get(client_name=client_name)
            if check_password(password=password, encoded=client.password):
                return Response({"detail": "Success",
                                 "data": {
                                     "access_token": f"{AccessToken.for_user(user=client)}",
                                     "refresh_token": f"{RefreshToken.for_user(user=client)}",
                                     "client": ClientSerializer(instance=client, many=False).data}})

            return Response({"detail": f"Failed to login."}, status=HTTP_400_BAD_REQUEST)
        except (Exception,) as err:
            return Response({"detail": f"{err}"}, status=HTTP_400_BAD_REQUEST)

