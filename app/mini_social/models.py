from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django import forms
from django.utils import timezone
from datetime import timedelta

#######################################################################################
class CustomUser(User):
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    avatar = models.CharField(max_length=60, default='')
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')  # Указываем папку загрузки относительно MEDIA_ROOT
    birth_date = models.DateField(null=True, blank=True)
    RELATIONSHIP_STATUSES = (
        ('single', 'Single'),
        ('relationship', 'In a Relationship'),
        ('married', 'Married'),
        ('complicated', 'It\'s Complicated'),
        ('open', 'Open Relationship'),
        ('separated', 'Separated'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    )
    current_city = models.CharField(max_length=100, blank=True)
    work = models.CharField(max_length=150, blank=True)
    educations = models.TextField(blank=True)
    relationship_status = models.CharField(
        max_length=20, choices=RELATIONSHIP_STATUSES, default='single', blank=True
    )
    last_activity = models.DateTimeField(null=True, blank=True)
    time_of_logout = models.DateTimeField(null=True, blank=True)

#######################################################################################
class Post(models.Model):
    title = models.CharField(max_length=150, blank=True)
    body = models.TextField(blank=True)
    link = models.URLField(blank=True, null=True)
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='posts/images/', blank=True, null=True)
    video = models.FileField(upload_to='posts/videos/', blank=True, null=True)

    def get_comments_count(self):
        return self.comments.count()
    
    def like(self, user):
        PostLike.objects.get_or_create(post=self, user=user)

    def unlike(self, user):
        PostLike.objects.filter(post=self, user=user).delete()

    def get_likes_count(self):
        return self.likes.count()

    def get_likers_info(self):
        likers = self.likes.all().select_related('user')
        return [
            {
                'first_name': like.user.first_name,
                'last_name': like.user.last_name
            }
            for like in likers
        ]


class HiddenPost(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    hidden_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"HiddenPost by {self.user} for {self.post}"



#######################################################################################

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)  # Новое поле

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"

    @classmethod
    def create_comment(cls, user, post, text):
        comment = cls.objects.create(author=user, post=post, text=text)
        return comment

    def delete_comment(self):
        self.delete()

    def update_comment(self, new_text):
        self.text = new_text
        self.is_edited = True  # Устанавливаем флаг в True при редактировании
        self.save()

    def like(self, user):
        CommentLike.objects.get_or_create(comment=self, user=user)

    def unlike(self, user):
        CommentLike.objects.filter(comment=self, user=user).delete()

    def get_likes_count(self):
        return self.likes.count()

    def get_likers_info(self):
        likers = self.likes.all().select_related('user')
        return [
            {
                'first_name': like.user.first_name,
                'last_name': like.user.last_name
            }
            for like in likers
        ]
    
#########################################################################################
class PostLike(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"Like by {self.user} on {self.post}"


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comment', 'user')

    def __str__(self):
        return f"Like by {self.user} on {self.comment}"
#######################################################################################



class Friendship(models.Model):
    creator = models.ForeignKey(
        CustomUser,
        related_name="friendship_creator_set",
        on_delete=models.CASCADE
    )
    friend = models.ForeignKey(
        CustomUser,
        related_name="friend_set",
        on_delete=models.CASCADE
    )
    STATUS_CHOICES = (
        ('sent', 'Запрос отправлен'),
        ('accepted', 'Запрос принят'),
        ('rejected', 'Запрос отклонен'),
        ('blocked', 'Пользователь заблокирован'),
    )
    status = models.CharField(
        max_length=8,
        choices=STATUS_CHOICES,
        default='sent'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        unique_together = ('creator', 'friend')

    def __str__(self):
        return f"{self.creator} -> {self.friend} : {self.status}"

    @classmethod
    def create_friend_request(cls, from_user, to_user):
        friendship, created = cls.objects.get_or_create(
            creator=from_user,
            friend=to_user,
            defaults={'status': 'sent'},
        )
        return friendship, created
    
    @classmethod
    def cancel_friend_request(cls, from_user, to_user):
        try:
            friendship = cls.objects.get(creator=from_user, friend=to_user, status='sent')
            friendship.delete()
            return True
        except cls.DoesNotExist:
            return False

    @classmethod
    def accept_friend_request(cls, from_user, to_user):
        try:
            friendship = cls.objects.get(creator=from_user, friend=to_user, status='sent')
            friendship.status = 'accepted'
            friendship.save()
            return True
        except cls.DoesNotExist:
            return False

    @classmethod
    def reject_friend_request(cls, from_user, to_user):
        try:
            friendship = cls.objects.get(creator=from_user, friend=to_user)
            friendship.status = 'rejected'
            friendship.save()
            return True
        except cls.DoesNotExist:
            return False
        
    @classmethod
    def has_sent_request(cls, from_user, to_user):
        return cls.objects.filter(creator=from_user, friend=to_user, status='sent').exists()
        

    @classmethod
    def remove_friend(cls, from_user, to_user):
        cls.objects.filter(
            (models.Q(creator=from_user) & models.Q(friend=to_user)) |
            (models.Q(creator=to_user) & models.Q(friend=from_user))
        ).delete()

    @classmethod
    def get_friends(cls, user):
        created_by_user = cls.objects.filter(creator=user, status='accepted').values_list('friend', flat=True)
        friend_of_user = cls.objects.filter(friend=user, status='accepted').values_list('creator', flat=True)
        friends_ids = list(created_by_user) + list(friend_of_user)
        return CustomUser.objects.filter(id__in=friends_ids)

    @classmethod
    def get_friends_with_messages(cls, user):
        # Получаем ID друзей, с которыми у пользователя есть сообщения
        friends_with_messages_ids = Message.objects.filter(
            models.Q(sender=user) | models.Q(recipient=user)
        ).values_list('sender', 'recipient')

        # Преобразуем QuerySet в список ID
        friends_ids = set()
        for sender_id, recipient_id in friends_with_messages_ids:
            if sender_id != user.id:
                friends_ids.add(sender_id)
            if recipient_id != user.id:
                friends_ids.add(recipient_id)

        # Получаем друзей пользователя, которые есть в списке friends_ids
        created_by_user = cls.objects.filter(creator=user, status='accepted', friend__id__in=friends_ids).values_list('friend', flat=True)
        friend_of_user = cls.objects.filter(friend=user, status='accepted', creator__id__in=friends_ids).values_list('creator', flat=True)

        # Объединяем ID и возвращаем пользователей
        friends_ids = list(created_by_user) + list(friend_of_user)
        return CustomUser.objects.filter(id__in=friends_ids)


#######################################################################################

    @classmethod
    def get_mutual_friends(cls, user_one, user_two):
        user_one_friends = set(cls.get_friends(user_one).values_list('friend', flat=True))
        user_two_friends = set(cls.get_friends(user_two).values_list('friend', flat=True))
        mutual_friends = user_one_friends.intersection(user_two_friends)
        return CustomUser.objects.filter(id__in=mutual_friends)

#######################################################################################
#######################################################################################
#######################################################################################
#######################################################################################


class Message(models.Model):
    is_deleted = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"From {self.sender} to {self.recipient} at {self.timestamp}"

    def get_sender_avatar_url(self):
        return self.sender.profile.avatar.url  # предполагая, что у модели пользователя есть связанный профиль с аватаром
    


#######################################################################################






