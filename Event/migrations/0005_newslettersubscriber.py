# Generated by Django 5.2 on 2025-07-14 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Event', '0004_alter_blogpost_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsletterSubscriber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]
