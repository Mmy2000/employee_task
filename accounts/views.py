from django.shortcuts import render
from accounts.models import User
from accounts.serializers import RegisterSerializer
from config.response import CustomResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, generics
from rest_framework.views import APIView

# Create your views here.


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return CustomResponse(
                data={
                    "user": {
                        "id": user.id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "username": user.username, 
                        "role": user.role,
                        "company": user.company_id,
                    },
                    "tokens": {
                        "access": access_token,
                        "refresh": str(refresh),
                    },
                },
                status=status.HTTP_201_CREATED,
                message="User registered successfully",
            )

        return CustomResponse(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    def post(self, request):
        email_or_username = request.data.get("email_or_username")
        password = request.data.get("password")

        if not email_or_username or not password:
            return CustomResponse(
                data={"error": "Email/Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Check if the input is an email or username
            if "@" in email_or_username:
                user = User.objects.get(email=email_or_username)
            else:
                user = User.objects.get(username=email_or_username)
        except User.DoesNotExist:
            return CustomResponse(
                data={"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(password):
            return CustomResponse(
                data={"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Tokens & data
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return CustomResponse(
            data={
                "access": access_token,
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
            message="Login successful",
        )
