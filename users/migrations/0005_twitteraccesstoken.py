# Generated by Django 2.2.9 on 2020-01-06 13:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20191230_0957'),
    ]

    operations = [
        migrations.CreateModel(
            name='TwitterAccessToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.CharField(max_length=254)),
                ('token_secret', models.CharField(max_length=254)),
                ('twitter_user_id', models.CharField(max_length=64)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='twitter_access_token', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
