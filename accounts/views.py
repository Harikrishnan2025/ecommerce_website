from rest_framework import generics, status
from rest_framework.response import Response
from django.core.mail import send_mail
from rest_framework.views import APIView
from .models import User
from .serializers import (RegisterSerializer, VerifyOTPSerializer,
                          ResetPasswordSerializer,UserProfileSerializer,
                          DeleteUserAccounrSerializer,ChangePasswordSerializer,LoginSerializer,ForgotPasswordSerializer)
from .otp import generate_otp, otp_is_valid
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_staff or request.user.role == 'admin')

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        existing_user = User.objects.filter(email=email).first()

        if existing_user and not existing_user.is_active:
            otp = generate_otp()
            existing_user.email_otp = otp
            existing_user.otp_created_at = timezone.now()
            existing_user.set_password(request.data.get('password'))  
            existing_user.save()
            send_mail(
                'Your OTP Code',
                f'Your new OTP is: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            return Response({'detail': 'User already registered but not verified. New OTP sent.'}, status=200)

        elif existing_user and existing_user.is_active:
            return Response({'detail': 'Email already registered and verified.'}, status=400)
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = serializer.save()
        otp = generate_otp()
        user.email_otp = otp
        user.otp_created_at = timezone.now()
        user.save()
        send_mail(
            'Your OTP Code',
            f'Your verification OTP is: {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )

class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        try:
            user = User.objects.get(email=email, is_active=False)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid email or already verified'}, status=400)

        if user.email_otp != otp or not otp_is_valid(user):
            return Response({'detail': 'Invalid or expired OTP'}, status=400)
     
        user.is_active = True
        user.email_otp = ''
        user.otp_created_at = None
        user.save()
        return Response({'detail': 'Email verified successfully'}, status=200)
    


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        if not email or not password:
            return Response({"message": "Email and password must  required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request=request, username=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Authenticated successfully",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": user.role 
            }, status=status.HTTP_200_OK)

        return Response({"message": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully Logged out"},status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            raise ValidationError("Invalid refresh token")
        
class ForgotPasswordView(APIView):
    def post(self,request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            otp = generate_otp()
            existing_user.email_otp = otp
            existing_user.otp_created_at = timezone.now()
            existing_user.save()
            send_mail(
                'Your OTP Code',
                f'Your new OTP is: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            return Response({'detail': '. New OTP sent to Email.'}, status=200)
        else:
            return Response({'detail': 'No account with this email.'}, status=400)

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.set_password(serializer.validated_data['new_password'])
            user.email_otp = None
            user.otp_created_at = None
            user.save()
            return Response({'message': 'Password reset successful'}, status=200)
        return Response(serializer.errors, status=400)
    


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer
    def get_object(self):
        return self.request.user
    
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserDeleteProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        serializer = DeleteUserAccounrSerializer(data=request.data)
        if serializer.is_valid():
            request.user.delete()
            return Response({'detail': 'Account deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()


class AdminRetrieveDeleteView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    def perform_destroy(self, instance):
        if instance.role == 'admin' or instance.is_staff:
            raise ValidationError("Admin users cannot be deleted.")
        instance.delete()