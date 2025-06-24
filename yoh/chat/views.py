from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .forms import RegisterForm, LoginForm, AddFriendForm, MessageForm
from .models import Friendship, Message

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

def landing_view(request):
    return render(request, 'landing.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
            
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)
        return redirect('landing#register')
    
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
                return redirect('home')
                
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'errors': form.errors}, status=400)
        return redirect('landing')
    
    return redirect('landing')

@login_required
def logout_view(request):
    logout(request)
    return redirect('landing')

@login_required
def home_view(request):
    # Get friends with unread message counts
    friendships = Friendship.objects.filter(user=request.user).select_related('friend')
    friends = []
    
    for friendship in friendships:
        friend = friendship.friend
        friend.unread_count = Message.objects.filter(
            sender=friend,
            receiver=request.user,
            is_read=False
        ).count()
        friends.append(friend)
    
    # Get recent messages
    messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-timestamp')[:50]
    
    # Handle add friend form
    form = AddFriendForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            friend_id = form.cleaned_data['friend_id']
            friend = get_object_or_404(User, id=friend_id)
            if friend != request.user:
                Friendship.objects.get_or_create(user=request.user, friend=friend)
                return redirect('home')
        except (ValueError, User.DoesNotExist):
            pass
    
    return render(request, 'home.html', {
        'friends': friends,
        'messages': messages,
        'form': form,
        'message_form': MessageForm()
    })

@login_required
@require_POST
def send_message(request, friend_id):
    form = MessageForm(request.POST)
    if form.is_valid():
        try:
            friend = get_object_or_404(User, id=friend_id)
            Message.objects.create(
                sender=request.user,
                receiver=friend,
                content=form.cleaned_data['content']
            )
            return JsonResponse({'status': 'success'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
    
    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

@login_required
def get_messages(request, friend_id):
    friend = get_object_or_404(User, id=friend_id)
    
    # Mark received messages as read
    Message.objects.filter(
        sender=friend,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)
    
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=friend) |
        Q(sender=friend, receiver=request.user)
    ).order_by('timestamp')
    
    return JsonResponse({
        'messages': [
            {
                'content': msg.content,
                'timestamp': msg.timestamp.strftime("%Y-%m-%d %H:%M"),
                'is_sent': msg.sender == request.user
            } 
            for msg in messages
        ]
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
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        ).exclude(id=request.user.id)
        
        results = [{
            'id': user.id,
            'username': user.username,
            'email': user.email
        } for user in users]
        
        return JsonResponse({'results': results})
    
    return JsonResponse({'results': []})