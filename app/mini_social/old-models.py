from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.backends import ModelBackend

#######################################################################################
class CustomUser(User):

    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    avatar = models.CharField(max_length=60, default='')
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


####################################################

        
    @classmethod
    def block_friend(cls, from_user, to_user):
        try:
            # Обновляем статус для обоих направлений дружбы
            friendship = cls.objects.filter(
                (models.Q(creator=from_user) & models.Q(friend=to_user)) |
                (models.Q(creator=to_user) & models.Q(friend=from_user))
            ).first() # использование first() предполагает, что может быть только одна запись
            if friendship:
                friendship.status = 'blocked'
                friendship.save()
                return True
        except cls.DoesNotExist:
            pass
        return False






    @classmethod
    def get_friends(cls, user):
        created_by_user = cls.objects.filter(creator=user, status='accepted').values_list('friend', flat=True)
        friend_of_user = cls.objects.filter(friend=user, status='accepted').values_list('creator', flat=True)
        friends_ids = list(created_by_user) + list(friend_of_user)
        return CustomUser.objects.filter(id__in=friends_ids)
    
    @classmethod
    def get_blocked_users(cls, user):
        blocked_by_user = cls.objects.filter(creator=user, status='blocked').values_list('friend', flat=True)
        blocked_of_user = cls.objects.filter(friend=user, status='blocked').values_list('creator', flat=True)
        blocked_users_ids = set(list(blocked_by_user) + list(blocked_of_user))  # Используем set для удаления возможных дубликатов
        return blocked_users_ids





####################################


    
   
    @classmethod
    def unblock_user(cls, from_user, to_user):
        try:
            friendship = cls.objects.get(
                (models.Q(creator=from_user) & models.Q(friend=to_user)) |
                (models.Q(creator=to_user) & models.Q(friend=from_user))
            )
            friendship.status = 'accepted'  # или 'rejected' в зависимости от того, что подразумевается под разблокировкой
            friendship.save()
            return True
        except cls.DoesNotExist:
            return False



    @classmethod
    def get_mutual_friends(cls, user_one, user_two):
        user_one_friends = set(cls.get_friends(user_one).values_list('friend', flat=True))
        user_two_friends = set(cls.get_friends(user_two).values_list('friend', flat=True))
        mutual_friends = user_one_friends.intersection(user_two_friends)
        return CustomUser.objects.filter(id__in=mutual_friends)

#######################################################################################


