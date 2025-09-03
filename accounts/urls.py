from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    RefreshTokenView,
    UserListView,
    ProfileView,
)
from .views import PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    # Authentication
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token_refresh"),

    # User endpoints
    path("users/", UserListView.as_view(), name="user_list"),
    path("me/", ProfileView.as_view(), name="profile"),
    
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
