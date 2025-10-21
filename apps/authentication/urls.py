from django.urls import path
from apps.authentication.views import  *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'), 
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('user/profile/', get_user_profile, name='user-profile'),
]