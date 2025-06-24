from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count, Max
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Friendship, Message, UserProfile
import json

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class MessageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, max_length=1000)

class AddFriendForm(forms.Form):
    friend_id = forms.IntegerField()

def landing_view(request):
    return render(request, 'chat/landing.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('home')
            
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)
        return redirect('landing')
    
    return redirect('landing')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Update last seen
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.last_seen = timezone.now()
                profile.is_online = True
                profile.save()
                return redirect('home')
                
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)
        return redirect('landing')
    
    return redirect('landing')

@login_required
def logout_view(request):
    # Update user status
    try:
        profile = request.user.userprofile
        profile.is_online = False
        profile.last_seen = timezone.now()
        profile.save()
    except:
        pass
    logout(request)
    return redirect('landing')

@login_required
def home_view(request):
    # Get friends with last message and unread counts
    friendships = Friendship.objects.filter(user=request.user).select_related('friend__userprofile')
    friends_data = []
    
    for friendship in friendships:
        friend = friendship.friend
        
        # Get last message between users
        last_message = Message.objects.filter(
            Q(sender=request.user, receiver=friend) |
            Q(sender=friend, receiver=request.user)
        ).order_by('-timestamp').first()
        
        # Get unread count
        unread_count = Message.objects.filter(
            sender=friend,
            receiver=request.user,
            is_read=False
        ).count()
        
        friends_data.append({
            'friend': friend,
            'last_message': last_message,
            'unread_count': unread_count,
            'profile': getattr(friend, 'userprofile', None)
        })
    
    # Sort by last message timestamp
    friends_data.sort(key=lambda x: x['last_message'].timestamp if x['last_message'] else timezone.now(), reverse=True)
    
    return render(request, 'chat/home.html', {
        'friends_data': friends_data,
        'user_profile': getattr(request.user, 'userprofile', None)
    })

@login_required
@require_POST
def send_message(request, friend_id):
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'status': 'error', 'message': 'Message cannot be empty'}, status=400)
        
        friend = get_object_or_404(User, id=friend_id)
        
        # Check if friendship exists
        if not Friendship.objects.filter(user=request.user, friend=friend).exists():
            return JsonResponse({'status': 'error', 'message': 'Not friends with this user'}, status=403)
        
        message = Message.objects.create(
            sender=request.user,
            receiver=friend,
            content=content
        )
        
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'content': message.content,
                'timestamp': message.timestamp.strftime("%H:%M"),
                'full_timestamp': message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'is_sent': True,
                'delivery_status': 'sent'
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Something went wrong'}, status=500)

@login_required
def get_messages(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    page = request.GET.get('page', 1)
    
    # Mark received messages as read
    Message.objects.filter(
        sender=friend,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)
    
    # Get messages with pagination
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=friend) |
        Q(sender=friend, receiver=request.user)
    ).order_by('-timestamp')
    
    paginator = Paginator(messages, 50)
    page_obj = paginator.get_page(page)
    
    # Reverse for display (oldest first)
    messages_list = list(reversed(page_obj.object_list))
    
    return JsonResponse({
        'messages': [
            {
                'id': msg.id,
                'content': msg.content,
                'timestamp': msg.timestamp.strftime("%H:%M"),
                'full_timestamp': msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'date': msg.timestamp.strftime("%Y-%m-%d"),
                'is_sent': msg.sender == request.user,
                'is_read': msg.is_read,
                'delivery_status': 'read' if msg.is_read else 'delivered'
            } 
            for msg in messages_list
        ],
        'friend': {
            'id': friend.id,
            'username': friend.username,
            'full_name': f"{friend.first_name} {friend.last_name}".strip() or friend.username,
            'is_online': getattr(friend, 'userprofile', None) and friend.userprofile.is_online,
            'last_seen': friend.userprofile.last_seen.strftime("%H:%M") if hasattr(friend, 'userprofile') and friend.userprofile.last_seen else None
        },
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages
    })

@login_required
def get_unread_count(request):
    unread_count = Message.objects.filter(
        receiver=request.user,
        is_read=False
    ).count()
    
    return JsonResponse({'unread_count': unread_count})

@login_required
def search_users(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    ).exclude(id=request.user.id)[:10]
    
    results = []
    for user in users:
        is_friend = Friendship.objects.filter(user=request.user, friend=user).exists()
        results.append({
            'id': user.id,
            'username': user.username,
            'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'email': user.email,
            'is_friend': is_friend,
            'is_online': getattr(user, 'userprofile', None) and user.userprofile.is_online if hasattr(user, 'userprofile') else False
        })
    
    return JsonResponse({'results': results})

@login_required
@require_POST
def add_friend(request):
    try:
        data = json.loads(request.body)
        friend_id = data.get('friend_id')
        
        friend = get_object_or_404(User, id=friend_id)
        
        if friend == request.user:
            return JsonResponse({'status': 'error', 'message': 'Cannot add yourself as friend'}, status=400)
        
        # Create bidirectional friendship
        friendship1, created1 = Friendship.objects.get_or_create(user=request.user, friend=friend)
        friendship2, created2 = Friendship.objects.get_or_create(user=friend, friend=request.user)
        
        if created1 or created2:
            return JsonResponse({'status': 'success', 'message': 'Friend added successfully'})
        else:
            return JsonResponse({'status': 'info', 'message': 'Already friends'})
            
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

@login_required
def mark_messages_read(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    
    updated_count = Message.objects.filter(
        sender=friend,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)
    
    return JsonResponse({
        'status': 'success',
        'updated_count': updated_count
    })

@login_required
def get_online_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = getattr(user, 'userprofile', None)
    
    if profile:
        return JsonResponse({
            'is_online': profile.is_online,
            'last_seen': profile.last_seen.strftime("%H:%M") if profile.last_seen else None
        })
    
    return JsonResponse({'is_online': False, 'last_seen': None})

@login_required
def update_typing_status(request, friend_id):
    """Update typing status for real-time typing indicators"""
    try:
        data = json.loads(request.body)
        is_typing = data.get('is_typing', False)
        
        # Here you would typically use WebSockets or Server-Sent Events
        # For now, we'll just return success
        return JsonResponse({'status': 'success'})
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)