from django.urls import path
from mini_social.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", home_page),
    path("user/signin/", signin),
    path("user/signin-action/", signin_action),
    path("user/signup-action/", signup_action, name='signup_action'),
    path("user/signup/", signup),
    path('user/logout/', logout_view, name='logout'),
    path("user/terms_and_conditions/", terms_and_conditions),
    path("user/profile/", profile_page),
    path("user/profile/edit/", profile_edit_page),
    path("user/profile/save/", profile_save_action),
    path("user/create_post/", create_post),
    path('delete-post/<int:post_id>/', delete_post, name='delete_post'),
    path('edit-post/<int:post_id>/', edit_post, name='edit_post'),
    path('hide-post/<int:post_id>/', hide_post, name='hide_post'),

    path("user/edit_post/", edit_post),
    path("user/about/", about_page),
    path('delete-account/<int:user_id>/', delete_account, name='delete_account'),
    path("user/my-posts/", my_posts_page),
    path("user/search/", search_users, name='search_users'),
    path("user/users_list/", users_list_page),

    path("user/friends_list/", friends_page, name='friends_page'),
    path('send-request/<int:user_id>/', send_friend_request, name='send_friend_request'),
    path('cancel-request/<int:user_id>/', cancel_friend_request, name='cancel_friend_request'),
    path('accept-request/<int:friendship_id>/', accept_friend_request, name='accept_friend_request'),
    path('reject-request/<int:friendship_id>/', reject_friend_request, name='reject_friend_request'),


    path('remove-friend/<int:user_id>/', remove_friend, name='remove_friend'),
    path('sent-requests/', sent_friend_requests, name='sent_friend_requests'),
    path("user/user-profile/<int:user_id>/", user_posts_page, name='user_profile'),

    # path('user/send_message/', friends_and_messages, name='friends_and_messages'),
    # path('user/send_message/', friends_and_messages, name='friends_and_messages'),
    path('user/message_list/', message_list, name='inbox'),

    path('user/friends/', friends_and_chat, name='friends_page'),
    path('chat/<int:friend_id>/', friends_and_chat, name='chat_view'),
    path('load_messages/', load_messages, name='load_messages'),
    path('send_message/<int:friend_id>/', send_message, name='send_message'),
    path('check_messages_updates/', check_messages_updates, name='check_new_messages'),
    path('get_friend_data/<int:friend_id>/', get_friend_data, name='get_friend_data'),


    path('message_edit/<int:message_id>/', edit_message, name='edit_message'),
    path('message_delete/<int:message_id>/', delete_message, name='delete_message'),

    path('update_activity/', update_user_activity, name='update_activity'),
    # path('get_friends_activity/', get_friends_activity, name='get_friends_activity'),

    path('create-comment/<int:post_id>/', create_comment, name='create_comment'),
    path('delete-comment/<int:comment_id>/<int:post_id>/', delete_comment, name='delete_comment'),
    path('edit-comment/<int:comment_id>/<int:post_id>/', edit_comment, name='edit_comment'),
    path('load-comments/', load_comments, name='load_comments'),
    path('add-like/<int:comment_id>/', add_like, name='add_like'),
    path('remove-like/<int:comment_id>/', remove_like, name='remove_like'),
    path('add-post-like/<int:post_id>/', add_post_like, name='add_post_like'),
    path('remove-post-like/<int:post_id>/', remove_post_like, name='remove_post_like'),
    path('get-likers/<int:post_id>/', get_likers, name='get_likers'),











] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


###################

# de inlocuit GET CU POST peste tot(signin, signup)