from rest_framework import generics, status
from rest_framework.response import Response
from django.core.mail import send_mail
from rest_framework.views import APIView
from .models import User
from .serializers import (RegisterSerializer, VerifyOTPSerializer,
                          ResetPasswordSerializer,UserProfileSerializer,
                          DeleteUserAccountSerializer,ChangePasswordSerializer,LoginSerializer,ForgotPasswordSerializer)
from .otp import generate_otp, otp_is_valid
from django.contrib.auth import authenticate
# from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def home_view(request):
    return render(request, 'home.html', {'user': request.user})

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
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'login.html'  

    def get(self, request):
        return Response({'serializer': LoginSerializer()}) 
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request=request, username=email, password=password)
        if user:
            login(request, user)  
            return redirect("home")  
        return render(request, "login.html", {"error": "Invalid credentials"})

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)  
        return redirect('login')
        
        
class ForgotPasswordView(generics.CreateAPIView):
    serializer_class = ForgotPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
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
                [email]
                
            )
            return Response({'detail': 'New OTP sent to Email.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'No account with this email.'}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(generics.CreateAPIView):
    serializer_class = ResetPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.set_password(serializer.validated_data['new_password'])
            user.email_otp = None
            user.otp_created_at = None
            user.save()
            return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer
    def get_object(self):
        return self.request.user
    
class ChangePasswordView(generics.CreateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)    

class UserDeleteProfileView(generics.CreateAPIView):
    serializer_class = DeleteUserAccountSerializer  
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request.user.delete()
        return Response({'detail': 'Account deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)  

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