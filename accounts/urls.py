from django.urls import path
from .views import (RegisterView, VerifyOTPView,LoginView,LogoutView,
                    UserProfileView,UserDeleteProfileView,
                    ForgotPasswordView,ResetPasswordView,
                    AdminRetrieveDeleteView,UserListView,ChangePasswordView)
from rest_framework_simplejwt.views import TokenRefreshView,TokenObtainPairView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='custom_jwt_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forgotpw/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('delete/', UserDeleteProfileView.as_view(), name='delete-user'),
    path('resetpw/', ResetPasswordView.as_view(), name='reset-password'),
    path('admin/users/', UserListView.as_view(), name='user-list'),
    path('admin/users/<int:pk>/', AdminRetrieveDeleteView.as_view(), name='user-detail-delete'),
    path('changepw/', ChangePasswordView.as_view(), name='change-password'),
]
