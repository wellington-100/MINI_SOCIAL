# Generated by Django 4.2.6 on 2023-11-02 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mini_social', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendship',
            name='creator_block',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='friendship',
            name='receiver_block',
            field=models.BooleanField(default=False),
        ),
    ]