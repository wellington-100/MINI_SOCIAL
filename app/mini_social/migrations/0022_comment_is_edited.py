# Generated by Django 4.2.6 on 2023-11-30 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mini_social', '0021_hiddenpost'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='is_edited',
            field=models.BooleanField(default=False),
        ),
    ]
