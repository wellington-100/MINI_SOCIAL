# Generated by Django 4.2.6 on 2023-11-02 23:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mini_social', '0003_remove_friendship_creator_block_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendship',
            name='blocked_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='blocker_set', to='mini_social.customuser'),
        ),
    ]
