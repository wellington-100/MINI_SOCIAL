from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.template import loader
from datetime import datetime
from random import randint
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from .models import Post, CustomUser, Friendship 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from time import time
from .forms import *
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import  require_POST
from django.http import JsonResponse





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

def profile_page(request):
    if request.user.is_authenticated:
        user = CustomUser.objects.get(pk=request.user.id)
        posts = Post.objects.all().order_by('-time')[:10]
        template = loader.get_template('profile.html')
        return HttpResponse(template.render(request=request, context={
            'user': user,
            'posts': posts,
            'current_year': datetime.now().year,
        }))
    else:
        return redirect ("/user/signin")
    
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
        return redirect("/user/profile")
    else:
        messages.error(request, "Invalid email or password")
        return HttpResponseRedirect('/user/signin')

@require_POST
def signup_action(request):
    # Теперь мы обрабатываем данные из POST запроса
    input_first_name = request.POST['first_name']
    input_last_name = request.POST['last_name']
    input_email = request.POST['email']
    input_password = request.POST['password']
    input_confirm_password = request.POST['confirm_password']
    if input_confirm_password == input_password:
        c_user = CustomUser.objects.create_user(
            first_name=input_first_name,
            last_name=input_last_name,
            username=input_email,  # Используем email в качестве username
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
        avatar_des_name = f"avatars/avatar{randint(1000000, 9000000)}-{time()}.png"
        with open(f"app/static/{avatar_des_name}", "wb+") as destination:
            for chunk in input_file_avatar.chunks():
                destination.write(chunk)
        user.avatar = avatar_des_name
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
    return redirect ('/user/profile')
    
def signup(request):
    template = loader.get_template('signup.html')
    return HttpResponse(template.render(base_context(request), request))

def logout_view(request):
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
        posts = Post.objects.filter(author=user).order_by('-time')[:10]
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
    
    # Находим запись о запросе в дружбу
    friendship_request = Friendship.objects.filter(creator=request.user, friend=to_user, status='sent').first()
    
    if friendship_request:
        friendship_request.delete()  # Удаление записи
        return JsonResponse({'message': 'Request cancelled successfully.'})
    else:
        return JsonResponse({'message': 'Friend request not found or already processed.'}, status=404)

@login_required
def accept_friend_request(request, friendship_id):
    friendship = get_object_or_404(Friendship, id=friendship_id)
    if friendship.friend.email == request.user.email:
        Friendship.accept_friend_request(friendship.creator, request.user)
        return JsonResponse({'status': 'success', 'message': 'Friend request accepted.'})
    return JsonResponse({'status': 'error', 'message': 'Unable to accept friend request.'}, status=400)

@login_required
def reject_friend_request(request, friendship_id):
    friendship = get_object_or_404(Friendship, id=friendship_id)
    if friendship.friend.email == request.user.email:
        friendship.delete()  # Удаление записи
        return JsonResponse({'status': 'success', 'message': 'Friend request rejected.'})
    return JsonResponse({'status': 'error', 'message': 'Unable to reject friend request.'}, status=400)



@login_required
def friends_page(request):
    user = CustomUser.objects.get(pk=request.user.id)
    template = loader.get_template('friends_list.html')
    received_requests = Friendship.objects.filter(friend=request.user, status='sent')
    friends = Friendship.get_friends(request.user)
    return HttpResponse(template.render(request=request, context={
        'user': user,
        'requests': received_requests,
        'friends': friends,
   
        'current_year': datetime.now().year,
    }))

@login_required
def sent_friend_requests(request):
    sent_requests = Friendship.objects.filter(creator=request.user, status='sent')
    return render(request, 'friends_app/sent_requests.html', {'requests': sent_requests})


@login_required
def block_friend(request, friendship_id):
    friendship = get_object_or_404(Friendship, id=friendship_id)
    if friendship.friend == request.user or friendship.creator == request.user:
        friendship.status = 'blocked'
        friendship.save()
    return redirect('list_friends')

@login_required
def list_blocked_friends(request):
    blocked_friends = Friendship.objects.filter(
        Q(creator=request.user, status='blocked') |
        Q(friend=request.user, status='blocked')
    )
    return render(request, 'friends_app/blocked_friends.html', {'blocked_friends': blocked_friends})

@login_required
def mutual_friends(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)
    mutuals = Friendship.get_mutual_friends(request.user, other_user)
    return render(request, 'friends_app/mutual_friends.html', {'mutuals': mutuals})


