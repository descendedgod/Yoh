from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'chat'

urlpatterns = [
    # Authentication URLs
    path('', views.landing_view, name='landing'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main app URLs
    path('home/', views.home_view, name='home'),
    
    # Message URLs
    path('api/send_message/<int:friend_id>/', views.send_message, name='send_message'),
    path('api/get_messages/<int:friend_id>/', views.get_messages, name='get_messages'),
    path('api/mark_read/<int:friend_id>/', views.mark_messages_read, name='mark_messages_read'),
    
    # Friend management URLs
    path('api/search_users/', views.search_users, name='search_users'),
    path('api/add_friend/', views.add_friend, name='add_friend'),
    
    # Status URLs
    path('api/unread_count/', views.get_unread_count, name='get_unread_count'),
    path('api/online_status/<int:user_id>/', views.get_online_status, name='get_online_status'),
    path('api/typing_status/<int:friend_id>/', views.update_typing_status, name='update_typing_status'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)