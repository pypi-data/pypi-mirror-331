from django.shortcuts import render
from django.views.generic import TemplateView



class CustomTemplateView(TemplateView):
    template_name = "base.html"


from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


from .user_serializers import UserSerializer
from rest_framework.exceptions import AuthenticationFailed

from django.apps import apps
# from .auth_settings import OIDC_RP_CLIENT_ID, OIDC_RP_CLIENT_SECRET, OIDC_OP_TOKEN_ENDPOINT
from django.conf import settings


import requests



class CheckAuthView(APIView):
    """
    Проверяет, аутентифицирован ли пользователь, и возвращает информацию о нем.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return Response(
                {"isAuthenticated": True, "user": serializer.data},
                status=status.HTTP_200_OK
            )
        else:
            raise AuthenticationFailed("Invalid token")



class CustomAuthView(APIView):
    """
    Обрабатывает аутентификацию через Authentik.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        authentik_url = OIDC_OP_TOKEN_ENDPOINT
        data = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": OIDC_RP_CLIENT_ID,
            "client_secret": OIDC_RP_CLIENT_SECRET,
            "scope": "openid profile email"
        }

        try:
            response = requests.post(authentik_url, data=data)
            response.raise_for_status()
            return Response(response.json(), status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        