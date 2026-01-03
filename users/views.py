from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializer import LogoutSerializer
from django.shortcuts import render
from rest_framework import generics, permissions, status 
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializer import RegisterSerializer


# регистрация
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# views.py

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Неверный refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"detail": "Выход выполнен успешно"},
            status=status.HTTP_205_RESET_CONTENT
        )
