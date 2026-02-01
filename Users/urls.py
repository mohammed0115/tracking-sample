from django.urls import path
from .views import register_view, login_view, logout_view, password_reset_view, password_reset_confirm_view, profile_edit_view
from .views import user_management_view, user_create_view, user_edit_view, user_toggle_active_view, user_reset_password_view

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('password_reset/', password_reset_view, name='password_reset'),
    path('reset/<uidb64>/<token>/', password_reset_confirm_view, name='password_reset_confirm'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),
    path('management/', user_management_view, name='user_management'),
    path('management/add/', user_create_view, name='user_create'),
    path('management/<int:user_id>/edit/', user_edit_view, name='user_edit'),
    path('management/<int:user_id>/toggle/', user_toggle_active_view, name='user_toggle_active'),
    path('management/<int:user_id>/reset-password/', user_reset_password_view, name='user_reset_password'),
]
