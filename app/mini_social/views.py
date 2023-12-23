from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from django.template import loader
from datetime import datetime
from random import randint
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from .models import *
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from .forms import *
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import  require_POST, require_GET
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from time import time
from datetime import datetime, timedelta
import redis




def base_context(request):
    banner_viewed = request.session.get('banner_viewed', False)
    if not banner_viewed:
        request.session['banner_viewed'] = True
    visit_count = request.session.get('visit_count', 0)
    visit_count += 1
    request.session['visit_count'] = visit_count
    return {
        'current_year': datetime.now().year,
        'banner_viewed': banner_viewed,
        'visit_count': visit_count
    }

def home_page(request):
    
    template = loader.get_template('home.html')
    
    return HttpResponse(template.render(base_context(request), request))
    
def signin(request):
    template = loader.get_template('signin.html')
    return HttpResponse(template.render(base_context(request), request))


    
def profile_edit_page(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(pk=request.user.id)
        template = loader.get_template('profile-edit.html')
        return HttpResponse(template.render(request=request, context={
            'user': user,
            'current_year': datetime.now().year,
        }))
    else:
        return redirect ("/user/signin")
    

def signin_action(request):
    input_email = request.GET['email']
    input_password = request.GET['password']
    user = authenticate(request, email=input_email, password=input_password, backend='mini_social.backends.EmailBackend')
    
    if user is not None:
        login(request, user)
        user = CustomUser.objects.get(pk=request.user.id)
        user.last_activity = timezone.now()
        user.save(update_fields=['last_activity'])
        return redirect("/user/profile")
    else:
        messages.error(request, "Invalid email or password")
        return HttpResponseRedirect('/user/signin')

@require_POST
def signup_action(request):
    input_first_name = request.POST['first_name']
    input_last_name = request.POST['last_name']
    input_email = request.POST['email']
    input_password = request.POST['password']
    input_confirm_password = request.POST['confirm_password']
    if input_confirm_password == input_password:
        c_user = CustomUser.objects.create_user(
            first_name=input_first_name,
            last_name=input_last_name,
            username=input_email,  
            email=input_email,
            password=input_password
        ) 
        login(request, c_user)
        return redirect('/user/profile')
    else:
        messages.error(request, "The passwords do not match")
        return redirect('/user/signup')


def profile_save_action(request):
    input_first_name = request.POST.get('first_name')
    input_last_name = request.POST.get('last_name')
    input_birth_date = request.POST.get('birth_date')
    input_email = request.POST.get('email')
    input_password = request.POST.get('password')
    input_file_avatar = request.FILES.get('avatar')
    input_current_city = request.POST.get('current_city')
    input_work = request.POST.get('work')
    input_educations = request.POST.get('educations')
    input_relationship_status = request.POST.get('relationship_status')

    user = CustomUser.objects.get(pk=request.user.id)
    user.first_name = input_first_name
    user.last_name = input_last_name
    user.email = input_email
    if input_password:
        user.set_password(input_password)
    if input_file_avatar:
        avatar_des_name = f"avatars/avatar{randint(1000000, 9000000)}-{int(time())}.png"
        path = default_storage.save(avatar_des_name, ContentFile(input_file_avatar.read()))
        user.avatar = path
    if input_birth_date:
        try:
            user.birth_date = datetime.strptime(input_birth_date, '%Y-%m-%d').date()
        except ValueError:
            error_message = "Data introdusă nu este validă. Te rog să folosești formatul YYYY-MM-DD."
            return redirect('/user/profile?error=' + error_message)
        
    user.current_city = input_current_city
    user.work = input_work
    user.educations = input_educations
    user.relationship_status = input_relationship_status
        
    user.save()
    update_session_auth_hash(request, user)
    return redirect ('/user/profile')
    
def signup(request):
    template = loader.get_template('signup.html')
    return HttpResponse(template.render(base_context(request), request))

def logout_view(request):
    user = CustomUser.objects.get(pk=request.user.id)
    user.time_of_logout = timezone.now()
    user.save(update_fields=['time_of_logout'])
    logout(request)
    return redirect('/user/signin')

def terms_and_conditions(request):
    template = loader.get_template('terms_and_conditions.html')
    return HttpResponse(template.render(base_context(request), request))

def about_page(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(pk=request.user.id)
        template = loader.get_template('about.html')
        return HttpResponse(template.render(request=request, context={
            'user': user,
            'current_year': datetime.now().year,
        }))
    else:
        return redirect ("/user/profile")

def create_post(request):
    user = CustomUser.objects.get(pk=request.user.id)
    template = loader.get_template('create_post.html')
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = user
            post.save()
            return redirect('/user/profile')
    else:
        form = PostForm()
    posts = Post.objects.all().order_by('-time')[:10]
    return HttpResponse(template.render(request=request, context={
            'user': user,
            'form': form,
            'posts': posts
        }))

def delete_post(request, post_id):
    user = CustomUser.objects.get(pk=request.user.id)
    post = get_object_or_404(Post, id=post_id)
    next_post = Post.objects.filter(id__gt=post_id).first()
    if request.method == 'POST':
        if post.author == user:
            post.delete()
            if next_post:
                return redirect(f'/user/profile#post-{next_post.id}')
            else:
                return redirect('/user/profile')
    return redirect('/user/profile')

def edit_post(request, post_id):
    user = CustomUser.objects.get(pk=request.user.id)
    template = loader.get_template('edit_post.html')
    post = get_object_or_404(Post, id=post_id)
    if post.author != user:
        return HttpResponseForbidden("You don't have permission to edit this post.")
    if request.method == 'POST':
        if request.method == 'POST':
            form = EditPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect(f'/user/profile#post-{post.id}')
    else:
        form = EditPostForm(instance=post)
    return HttpResponse(template.render(request=request, context={
            'user': user,
            'form': form,
            'current_year': datetime.now().year,
        }))

@login_required
def delete_account(request, user_id):
    user = CustomUser.objects.get(pk=request.user.id)
    try:
        user.delete()
        messages.success(request, "Your account and all associated data have been successfully deleted.")
    except Exception as e:
        messages.error(request, f"An error occurred while deleting your account: {e}")
    return redirect('/user/signin')

def my_posts_page(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(pk=request.user.id)
        posts = Post.objects.filter(author=user).order_by('-time')[:20]
        template = loader.get_template('my-posts.html')
        return HttpResponse(template.render(request=request, context={
            'user': user,
            'posts': posts,
            'current_year': datetime.now().year,
        }))
    else:
        return redirect ("/user/signin")
#############################################################################   
@login_required  
def user_posts_page(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    current_user = CustomUser.objects.get(pk=request.user.id)
    posts = Post.objects.filter(author=user).order_by('-time')[:10]
    template = loader.get_template('user-profile.html')
    return HttpResponse(template.render(request=request, context={
        'user': user,  
        'current_user': current_user,
        'posts': posts,  
        'current_year': datetime.now().year,  
    }))


@login_required
def hide_post(request, post_id):
    current_user = CustomUser.objects.get(pk=request.user.id)
    post = get_object_or_404(Post, id=post_id)
    next_post = Post.objects.filter(id__gt=post_id).first()
    if post.author != current_user:
        HiddenPost.objects.get_or_create(user=current_user, post=post)
        if next_post:
            return redirect(f'/user/profile#post-{next_post.id}')
        else:
            return redirect('/user/profile')
    return redirect('/user/profile')





#############################################################################

@login_required
def users_list_page(request):
    user = CustomUser.objects.get(pk=request.user.id)
    template = loader.get_template('users_list.html')
    return HttpResponse(template.render(request=request, context={
        'user': user,
        'current_year': datetime.now().year,
    }))

@login_required
def search_users(request):
    user = CustomUser.objects.get(pk=request.user.id)
    template = loader.get_template('users_list.html')
    query = request.GET.get('q', '')
    users = CustomUser.objects.none()

    if query:
        users = CustomUser.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )

    user_requests = {
        u.id: Friendship.has_sent_request(user, u)
        for u in users
    }
    friends = Friendship.get_friends(request.user)
    friend_ids = [f.id for f in friends]
    return HttpResponse(template.render(request=request, context={
        'user': user,
        'users': users,
        'friends': friends,
        'friend_ids': friend_ids,
        'current_year': datetime.now().year,
        'user_requests': user_requests
    }))
#############################################################################

#############################################################################
@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(CustomUser, id=user_id)
    from_user = CustomUser.objects.get(id=request.user.id)
    Friendship.create_friend_request(from_user, to_user)
    return JsonResponse({'message': 'Request sent successfully.'})

@login_required
def cancel_friend_request(request, user_id):
    to_user = get_object_or_404(CustomUser, id=user_id)
    friendship_request = Friendship.objects.filter(creator=request.user, friend=to_user, status='sent').first()
    if friendship_request:
        friendship_request.delete()  
        return JsonResponse({'message': 'Request cancelled successfully.'})
    else:
        return JsonResponse({'message': 'Friend request not found or already processed.'}, status=404)

@login_required
def accept_friend_request(request, friendship_id):
    friendship = get_object_or_404(Friendship, id=friendship_id)
    if friendship.friend.email == request.user.email:
        if Friendship.accept_friend_request(friendship.creator, request.user):
            friend = friendship.creator
            friend_data = {
                'id': friend.id,
                'firstName': friend.first_name,
                'lastName': friend.last_name,
                'avatarUrl': friend.avatar.url  
            }
            return JsonResponse({'status': 'success', 'message': 'Friend request accepted.', 'friendData': friend_data})
    return JsonResponse({'status': 'error', 'message': 'Unable to accept friend request.'}, status=400)


@login_required
def reject_friend_request(request, friendship_id):
    friendship = get_object_or_404(Friendship, id=friendship_id)
    if friendship.friend.email == request.user.email:
        friendship.delete() 
        return JsonResponse({'status': 'success', 'message': 'Friend request rejected.'})
    return JsonResponse({'status': 'error', 'message': 'Unable to reject friend request.'}, status=400)


@login_required
def sent_friend_requests(request):
    sent_requests = Friendship.objects.filter(creator=request.user, status='sent')
    return render(request, 'friends_app/sent_requests.html', {'requests': sent_requests})

@login_required
def remove_friend(request, user_id):
    try:
        friend = get_object_or_404(CustomUser, id=user_id)
        Friendship.remove_friend(request.user, friend)
        return JsonResponse({'status': 'success', 'message': 'Friend removed successfully.'})
    except CustomUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
    except Exception as e:
        print(f"Error removing friend: {e}")
        return JsonResponse({'status': 'error', 'message': 'Internal server error.'}, status=500)

@login_required
def mutual_friends(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)
    mutuals = Friendship.get_mutual_friends(request.user, other_user)
    return render(request, 'friends_app/mutual_friends.html', {'mutuals': mutuals})
#######################################################################################
#######################################################################################
@login_required
def friends_page(request):
    user = CustomUser.objects.get(pk=request.user.id)
    template = loader.get_template('friends_list.html')
    received_requests = Friendship.objects.filter(friend=user, status='sent')
    friends = Friendship.get_friends(user)
    return HttpResponse(template.render(request=request, context={
        'user': user,
        'requests': received_requests,
        'friends': friends,
        'current_year': datetime.now().year,
    }))

#######################################################################################


def send_message(request, friend_id):
    form = MessageForm(request.POST)
    
    if form.is_valid():
        try:
            user = CustomUser.objects.get(pk=request.user.id)
            friend = CustomUser.objects.get(pk=friend_id)
            message = form.save(commit=False)
            message.sender = user  
            message.recipient = friend  
            message.save()
            
            return JsonResponse({'success': True})
        except Exception as e:  
            return JsonResponse({'success': False, 'errors': str(e)})
    else:
        
        return JsonResponse({'success': False, 'errors': form.errors})


####################################


@login_required
def message_list(request):
    inbox_messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    outbox_messages = Message.objects.filter(sender=request.user).order_by('-timestamp')
    return render(request, 'message_list.html', {
        'inbox_messages': inbox_messages,
        'outbox_messages': outbox_messages
    })

#########################


def chat_view(request, friend_id):
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient_id = friend_id
            message.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        messages = Message.objects.filter(
            (Q(sender=request.user, recipient_id=friend_id) | Q(sender_id=friend_id, recipient=request.user))
        ).order_by('timestamp')
        form = MessageForm()
        return render(request, 'friends_and_chat.html', {'messages': messages, 'form': form})

######################

@login_required
def friends_and_chat(request, friend_id=None):
    
    try:
        user = CustomUser.objects.get(pk=request.user.id)
    except CustomUser.DoesNotExist:
        return HttpResponseNotFound('User not found')

    template = loader.get_template('friends_and_chat.html')
    received_requests = Friendship.objects.filter(friend=user, status='sent')

    friends_ids_with_messages = Friendship.get_friends_with_messages(user)
    friends_with_messages = CustomUser.objects.filter(
        Q(sent_messages__recipient=user) | Q(received_messages__sender=user),
        id__in=friends_ids_with_messages
    ).distinct()

    for friend in friends_with_messages:
        time_since_last_activity = (timezone.now() - friend.last_activity).total_seconds() if friend.last_activity else float('inf')
        time_since_logout = (timezone.now() - friend.time_of_logout).total_seconds() if friend.time_of_logout else float('inf')
        friend.is_online = time_since_last_activity > 60 and time_since_last_activity < time_since_logout
    sorted_friends = sorted(friends_with_messages, key=lambda friend: friend.is_online, reverse=True)

    messages, form = None, None
    if friend_id:
        # now = timezone.now()
        # is_online = (now - friend.last_activity).total_seconds() > 60  # 5 минут
        try:
            friend = CustomUser.objects.get(pk=friend_id)
            messages = Message.objects.filter(
                (Q(sender=user, recipient=friend) | Q(sender=friend, recipient=user))
            ).order_by('timestamp')

            for message in messages:
                message.formatted_time = message.timestamp.strftime("%H:%M")
                message.formatted_date = message.timestamp.date()

            form = MessageForm()
        except CustomUser.DoesNotExist:
            return HttpResponseNotFound('Friend not found')

    return HttpResponse(template.render(request=request, context={
        'user': user,
        'requests': received_requests,
        'friends': friends_with_messages,
        'current_year': datetime.now().year,
        'friend_id': friend_id,
        'messages': messages,
        'form': form,
        'friends': sorted_friends,
    }))




@login_required
def load_messages(request):
    if request.method == 'GET':
        friend_id = request.GET.get('friend_id')
        if friend_id:
            user = CustomUser.objects.get(pk=request.user.id)
            friend = CustomUser.objects.get(pk=friend_id)
            messages = Message.objects.filter(
                (Q(sender=user, recipient=friend) | Q(sender=friend, recipient=user)),
                is_deleted=False  
            ).order_by('timestamp')

            if messages:
                last_message_time = messages.last().timestamp
                if timezone.is_naive(last_message_time):
                    last_message_time = timezone.make_aware(last_message_time, timezone.get_default_timezone())
                request.session['last_message_time'] = last_message_time.isoformat()
            

            messages_data = [
                {
                    'id': message.id,
                    'sender': message.sender.username,
                    'body': message.body,
                    'avatar_url': message.sender.avatar.url if message.sender.avatar else settings.MEDIA_URL + 'avatars/default.png',
                    'is_sender': message.sender == user,
                    'timestamp': message.timestamp.isoformat(),  
                    'date': message.timestamp.strftime("%e %B %Y")  
                    
                }
                for message in messages
            ]
            return JsonResponse(messages_data, safe=False)

        return JsonResponse([], safe=False)

redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
@login_required
def check_messages_updates(request):
    user = request.user
    friend_id = request.GET.get('friend_id', None)
    redis_key_last_check = f'user:{user.id}:friend:{friend_id}:last_check' if friend_id else None

    if request.method == 'GET' and friend_id:
        try:
            friend = CustomUser.objects.get(pk=friend_id)
            # print(f"Found friend with ID {friend_id}")
            last_check_str = redis_client.get(redis_key_last_check)
            # print(f"Last check string from Redis: {last_check_str}")
            if last_check_str:
                last_check = datetime.fromisoformat(last_check_str.decode('utf-8'))
                if timezone.is_naive(last_check):
                    last_check = timezone.make_aware(last_check, timezone.get_default_timezone())
            else:
                last_check = timezone.now()
            # print(f"Last check datetime: {last_check}")
            current_time = timezone.now()
            # print(f"Current time: {current_time}")
            new_messages_exist = Message.objects.filter(
                (Q(sender=user, recipient=friend) | Q(sender=friend, recipient=user)),
                timestamp__gt=last_check
            ).exists()
            # print(f'new_messages_exist: {new_messages_exist}')
            redis_key_deleted = f'user:{user.id}:deleted_message_count'
            current_deleted_message_count = Message.objects.filter(
                (Q(sender=user, recipient=friend) | Q(sender=friend, recipient=user)),
                is_deleted=True
            ).count()
            last_deleted_message_count = int(redis_client.get(redis_key_deleted) or 0)
            deleted_messages_changed = current_deleted_message_count != last_deleted_message_count
            # print(f'deleted_messages_changed: {deleted_messages_changed}')
            redis_key_edited = f'user:{user.id}:edited_message_count'
            current_edited_message_count = Message.objects.filter(
                (Q(sender=user, recipient=friend) | Q(sender=friend, recipient=user)),
                is_edited=True
            ).count()
            last_edited_message_count = int(redis_client.get(redis_key_edited) or 0)
            edited_messages_changed = current_edited_message_count != last_edited_message_count
            # print(f'edited_messages_changed: {edited_messages_changed}')
            if deleted_messages_changed:
                redis_client.set(redis_key_deleted, current_deleted_message_count)
            if edited_messages_changed:
                redis_client.set(redis_key_edited, current_edited_message_count)

            if new_messages_exist or deleted_messages_changed or edited_messages_changed:
                redis_client.set(redis_key_last_check, current_time.isoformat())
                # print(f"Updated last check in Redis: {current_time.isoformat()}")
                return JsonResponse({'updates': True})
            
            return JsonResponse({'updates': False})

        except CustomUser.DoesNotExist:
            # print("CustomUser.DoesNotExist error")
            return JsonResponse({'error': 'User or friend not found'}, status=404)
        except Exception as e:
            # print(f"Exception occurred: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    else:
        if redis_key_last_check:
            current_time = timezone.now()
            redis_client.set(redis_key_last_check, current_time.isoformat())
            # print(f"Updated last check in Redis for non-GET request: {current_time.isoformat()}")
        return JsonResponse({'updates': False})





def get_friend_data(request, friend_id):
    friend = CustomUser.objects.get(pk=friend_id)
    now = timezone.now()

    time_since_last_activity = (now - friend.last_activity).total_seconds() if friend.last_activity else float('inf')
    time_since_logout = (now - friend.time_of_logout).total_seconds() if friend.time_of_logout else float('inf')

    is_online = time_since_last_activity > 60 and time_since_last_activity < time_since_logout
    is_offline = not is_online

    data = {
        'avatar_url': friend.avatar.url if friend.avatar else None,
        'last_name': friend.last_name,
        'first_name': friend.first_name,
        'last_activity': friend.last_activity.isoformat() if friend.last_activity else None,
        'time_of_logout': friend.time_of_logout.isoformat() if friend.time_of_logout else None,
        'is_online': is_online,
        'is_offline': is_offline
    }
    return JsonResponse(data)


##########################

@login_required
def edit_message(request, message_id):
    try:
        user = CustomUser.objects.get(pk=request.user.id) 
        message = Message.objects.get(pk=message_id) 
        if message.sender != user:
            return JsonResponse({'success': False, 'error': 'You do not have permission to edit this message.'}, status=403)

        if request.method == 'POST':
            form = MessageForm(request.POST, instance=message)
            if form.is_valid():
                form.save()
                message.last_edited_time = timezone.now()
                message.is_edited = True
                message.save()  

                return JsonResponse({'success': True, 'body': message.body})
            else:
                return JsonResponse({'success': False, 'errors': form.errors})

    except Message.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message not found.'}, status=404)



    
@login_required
def delete_message(request, message_id):
    try:
        user = CustomUser.objects.get(pk=request.user.id)
        message = Message.objects.get(pk=message_id)
        print(f"Sender ID: {message.sender.id}, Request User ID: {user.id}")

        
        if message.sender != user:
            return JsonResponse({'success': False, 'error': 'You do not have permission to delete this message.'}, status=403)
        message.last_deleted_time = timezone.now()
        message.is_deleted = True
        message.save() 
        return JsonResponse({'success': True})

    except Message.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message not found.'}, status=404)
    except Exception as e:
        print(f"Error during message deletion: {e}")
        return JsonResponse({'success': False, 'error': 'Internal server error.'}, status=500)


@require_POST
def update_user_activity(request):
    if request.user.is_authenticated:
        request.user.last_activity = timezone.now()
        request.user.save(update_fields=['last_activity'])
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=401)

from django.shortcuts import get_object_or_404



@login_required
def check_friend_authentication(request):
    friend_id = request.GET.get('friend_id')

    if not friend_id:
        return JsonResponse({'status': 'error', 'message': 'No friend ID provided'}, status=400)

    friend = get_object_or_404(CustomUser, pk=friend_id)

    if friend not in request.user.friends.all():
        return JsonResponse({'status': 'error', 'message': 'User is not a friend'}, status=403)

    is_authenticated = friend.is_authenticated if hasattr(friend, 'is_authenticated') else False

    return JsonResponse({'is_authenticated': is_authenticated})


##########################################################
##########################################################

import json

@login_required
def create_comment(request, post_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  
            text = data['text']
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        current_user = CustomUser.objects.get(pk=request.user.id)
        post = get_object_or_404(Post, id=post_id)

        if text:  
            comment = Comment.create_comment(user=current_user, post=post, text=text)
            comment_data = {
                'id': comment.id,
                'author_last_name': comment.author.last_name,
                'author_first_name': comment.author.first_name,
                'text': comment.text,
                'avatar_url': comment.author.avatar.url if comment.author.avatar else None,
                'timestamp': comment.created_at.isoformat(),
                'can_edit': current_user == comment.author,
                'can_delete': current_user == comment.author or current_user == post.author,
                'likes_count': 0,  
                'is_liked': False, 
                'likers_info': comment.get_likers_info(), 
            }
            return JsonResponse({'success': True, 'comment': comment_data})
        else:
            return JsonResponse({'error': 'Text is required'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def delete_comment(request, comment_id, post_id):
    current_user = CustomUser.objects.get(pk=request.user.id)
    comment = get_object_or_404(Comment, id=comment_id)
    post = get_object_or_404(Post, id=post_id)
    if current_user == comment.author or current_user == post.author:
        comment.delete_comment()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': 'Not authorized'}, status=403)

def edit_comment(request, comment_id, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    current_user = CustomUser.objects.get(pk=request.user.id)
    comment = get_object_or_404(Comment, id=comment_id)
    post = get_object_or_404(Post, id=post_id)

    if current_user != comment.author:
        return JsonResponse({'error': "You don't have permission to edit this comment"}, status=403)

    try:
        data = json.loads(request.body)
        new_text = data['text']
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    if not new_text:
        return JsonResponse({'error': 'Text is required'}, status=400)

    comment.update_comment(new_text=new_text)

    comment_data = {
        'id': comment.id,
        'author_last_name': comment.author.last_name,
        'author_first_name': comment.author.first_name,
        'text': comment.text,
        'avatar_url': comment.author.avatar.url if comment.author.avatar else None,
        'timestamp': comment.created_at.isoformat(),
        'can_edit': current_user == comment.author,
        'can_delete': current_user == comment.author or current_user == post.author,  
        'is_edited': comment.is_edited,  
        'likes_count': comment.get_likes_count(),
        'is_liked': comment.likes.filter(user=current_user).exists(),
    }

    return JsonResponse({'success': True, 'comment': comment_data})



@login_required
def load_comments(request):
    if request.method == 'GET':
        current_user = CustomUser.objects.get(pk=request.user.id)
        post_id = request.GET.get('post_id')
        if post_id:
            post = Post.objects.get(pk=post_id)
            comments = Comment.objects.filter(
                post=post,
            ).order_by('created_at')

            comments_data = [
                {
                    'id': comment.id,
                    'author_last_name': comment.author.last_name,
                    'author_first_name': comment.author.first_name,
                    'text': comment.text,
                    'avatar_url': comment.author.avatar.url if comment.author.avatar else settings.MEDIA_URL + 'avatars/default.png',
                    'timestamp': comment.created_at.isoformat(),  
                    'can_edit': current_user == comment.author,
                    'can_delete': current_user == comment.author or current_user == post.author,
                    'is_edited': comment.is_edited,  
                    'likes_count': comment.get_likes_count(),
                    'is_liked': comment.likes.filter(user=current_user).exists(),
                    'likers_info': comment.get_likers_info(),  
                    
                }
                for comment in comments
            ]
            return JsonResponse(comments_data, safe=False)
        return JsonResponse([], safe=False)

@login_required
@require_POST
def add_like(request, comment_id):
    try:
        current_user = CustomUser.objects.get(pk=request.user.id)
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({'error': 'Comment not found'}, status=404)
    
    comment.like(current_user)
    return JsonResponse({
        'status': 'success', 
        'likes_count': comment.get_likes_count(),
        'likers_info': comment.get_likers_info(),  
        'is_liked': True
    })


@login_required
@require_POST
def remove_like(request, comment_id):
    try:
        current_user = CustomUser.objects.get(pk=request.user.id)
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({'error': 'Comment not found'}, status=404)

    comment.unlike(current_user)
    return JsonResponse({
        'status': 'success', 
        'likes_count': comment.get_likes_count(),
        'likers_info': comment.get_likers_info(),  
        'is_liked': False
    })

#####################################################
@login_required
@require_POST
def add_post_like(request, post_id):
    try:
        current_user = CustomUser.objects.get(pk=request.user.id)
        post = get_object_or_404(Post, id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)
    post.like(current_user)
    return JsonResponse({
        'id': post.id,
        'status': 'success', 
        'likes_count': post.get_likes_count(),
        'likers_info': post.get_likers_info(),  
        'is_liked': True
    })


@login_required
@require_POST
def remove_post_like(request, post_id):
    try:
        current_user = CustomUser.objects.get(pk=request.user.id)
        post = get_object_or_404(Post, id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Comment not found'}, status=404)

    post.unlike(current_user)
    return JsonResponse({
        'id': post.id,
        'status': 'success', 
        'likes_count': post.get_likes_count(),
        'likers_info': post.get_likers_info(), 
        'is_liked': False
    })

@login_required
def profile_page(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(pk=request.user.id)
        hidden_posts_ids = HiddenPost.objects.filter(user=user).values_list('post_id', flat=True)
        posts_query = Post.objects.exclude(id__in=hidden_posts_ids).order_by('-time')[:20]

        posts_data = []
        for post in posts_query:
            post_data = {
                'id': post.id,
                'title': post.title,
                'body': post.body,
                'link': post.link,
                'author': post.author,
                'time': post.time,
                'image_url': post.image.url if post.image else None,
                'video_url': post.video.url if post.video else None,
                'likes_count': post.get_likes_count(),
                'likers_info': post.get_likers_info(),
            }
            posts_data.append(post_data)

        template = loader.get_template('profile.html')
        return HttpResponse(template.render(request=request, context={
            'user': user,
            'posts': posts_data,
            'current_year': datetime.now().year,
        }))
    else:
        return redirect("/user/signin")
    #####


def get_likers(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        likers = post.likes.all() 

        likers_info = [{
            'first_name': liker.user.first_name,
            'last_name': liker.user.last_name,
            'likes_count': post.get_likes_count(),
        } for liker in likers]

        return JsonResponse({'likers': likers_info})

    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)



######