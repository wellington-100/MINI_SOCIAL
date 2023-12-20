from django.urls import path
from mini_social.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", home_page),
    path("user/signin/", signin),
    path("user/signin-action/", signin_action),
    path("user/signup-action/", signup_action),
    path("user/signup/", signup),
    path('user/logout/', logout_view, name='logout'),
    path("user/terms_and_conditions/", terms_and_conditions),
    path("user/profile/", profile_page),
    path("user/profile/edit/", profile_edit_page),
    path("user/profile/save/", profile_save_action),
    path("user/create_post/", create_post),
    path('delete-post/<int:post_id>/', delete_post, name='delete_post'),
    path('edit-post/<int:post_id>/', edit_post, name='edit_post'),
    path("user/edit_post/", edit_post),
    path("user/about/", about_page),
    path('delete-account/<int:user_id>/', delete_account, name='delete_account'),
    path("user/my-posts/", my_posts_page),
    path("user/search/", search_users, name='search_users'),
    path("user/users_list/", users_list_page),
    path("user/add_friend/<int:user_id>/", add_friend, name='add_friend'),
    path("user/remove_friend/<int:user_id>/", remove_friend, name='remove_friend'),
    path("user/friends_list/", friend_list, name='friend_list'),




] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

################

# de inlocuit GET CU POST peste tot(signin, signup)