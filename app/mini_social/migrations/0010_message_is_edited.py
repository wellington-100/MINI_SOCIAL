# Generated by Django 4.2.6 on 2023-11-19 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mini_social', '0009_message_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_edited',
            field=models.BooleanField(default=False),
        ),
    ]