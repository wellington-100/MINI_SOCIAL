# Generated by Django 4.2.6 on 2023-11-03 00:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mini_social', '0004_friendship_blocked_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='friendship',
            name='blocked_by',
        ),
    ]
