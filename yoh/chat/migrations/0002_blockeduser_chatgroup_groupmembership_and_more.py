# Generated by Django 5.2.3 on 2025-07-12 14:26

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlockedUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blocked_at', models.DateTimeField(auto_now_add=True)),
                ('reason', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ChatGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='groups/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='GroupMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('member', 'Member')], default='member', max_length=10)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='MessageReaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reaction', models.CharField(choices=[('👍', 'Thumbs Up'), ('❤️', 'Heart'), ('😂', 'Laughing'), ('😮', 'Wow'), ('😢', 'Sad'), ('😡', 'Angry')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TypingStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_typing', models.BooleanField(default=False)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('phone_number', models.CharField(blank=True, max_length=15)),
                ('is_online', models.BooleanField(default=False)),
                ('last_seen', models.DateTimeField(blank=True, null=True)),
                ('show_last_seen', models.BooleanField(default=True)),
                ('show_online_status', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['timestamp']},
        ),
        migrations.AddField(
            model_name='friendship',
            name='blocked_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='friendship',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='delivery_status',
            field=models.CharField(choices=[('sent', 'Sent'), ('delivered', 'Delivered'), ('read', 'Read')], default='sent', max_length=10),
        ),
        migrations.AddField(
            model_name='message',
            name='edited_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='file_attachment',
            field=models.FileField(blank=True, null=True, upload_to='messages/files/'),
        ),
        migrations.AddField(
            model_name='message',
            name='image_attachment',
            field=models.ImageField(blank=True, null=True, upload_to='messages/images/'),
        ),
        migrations.AddField(
            model_name='message',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='message_type',
            field=models.CharField(choices=[('text', 'Text'), ('image', 'Image'), ('file', 'File'), ('voice', 'Voice')], default='text', max_length=10),
        ),
        migrations.AddField(
            model_name='message',
            name='read_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='reply_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='chat.message'),
        ),
        migrations.AddField(
            model_name='message',
            name='voice_attachment',
            field=models.FileField(blank=True, null=True, upload_to='messages/voice/'),
        ),
        migrations.AlterField(
            model_name='friendship',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='message',
            name='content',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='friendship',
            index=models.Index(fields=['user', 'friend'], name='chat_friend_user_id_2ec469_idx'),
        ),
        migrations.AddIndex(
            model_name='friendship',
            index=models.Index(fields=['created_at'], name='chat_friend_created_ffe502_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['sender', 'receiver', 'timestamp'], name='chat_messag_sender__53da58_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['timestamp'], name='chat_messag_timesta_6494d7_idx'),
        ),
        migrations.AddIndex(
            model_name='message',
            index=models.Index(fields=['is_read'], name='chat_messag_is_read_872c73_idx'),
        ),
        migrations.AddField(
            model_name='blockeduser',
            name='blocked',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocked_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blockeduser',
            name='blocker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocked_users', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatgroup',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_groups', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='groupmembership',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.chatgroup'),
        ),
        migrations.AddField(
            model_name='groupmembership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatgroup',
            name='members',
            field=models.ManyToManyField(through='chat.GroupMembership', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='messagereaction',
            name='message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reactions', to='chat.message'),
        ),
        migrations.AddField(
            model_name='messagereaction',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='typingstatus',
            name='typing_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='being_typed_to', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='typingstatus',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='typing_to', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='blockeduser',
            unique_together={('blocker', 'blocked')},
        ),
        migrations.AlterUniqueTogether(
            name='groupmembership',
            unique_together={('group', 'user')},
        ),
        migrations.AddIndex(
            model_name='messagereaction',
            index=models.Index(fields=['message', 'user'], name='chat_messag_message_511fb7_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='messagereaction',
            unique_together={('message', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='typingstatus',
            unique_together={('user', 'typing_to')},
        ),
    ]
