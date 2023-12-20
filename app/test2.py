import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mini_social.settings')
django.setup()

# Теперь вы можете использовать функции Django, такие как resolve
from django.urls import resolve
resolve('/get_friend_data/2/')
