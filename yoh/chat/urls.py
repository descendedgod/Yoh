from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('send_message/<int:friend_id>/', views.send_message, name='send_message'),
    path('get_messages/<int:friend_id>/', views.get_messages, name='get_messages'),
]