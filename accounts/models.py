from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        if not username:
            raise ValueError('The Username must be set')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, username, password, **extra_fields)

    def active_users(self):
        return self.get_queryset().filter(is_active=True)

    def get_followers(self, user):
        return user.followers.all()

    def get_following(self, user):
        return user.following.all()


class FollowRequestManager(models.Manager):
    def pending_requests(self, user):
        return self.filter(receiver=user, status='pending')

    def exists_pending_request(self, sender, receiver):
        return self.filter(
            requester=sender,
            receiver=receiver,
            status='pending'
        ).exists()

    def accept_request(self, request):
        request.status = 'accepted'
        request.save()
        request.requester.following.add(request.receiver)
        request.receiver.followers.add(request.requester)

    def reject_request(self, request):
        request.status = 'rejected'
        request.save()


class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    ]

    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    website = models.URLField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    is_private = models.BooleanField(default=True)
    verified = models.BooleanField(default=False)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    def __str__(self):
        return self.username


class FollowRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = FollowRequestManager()

    class Meta:
        unique_together = ('requester', 'receiver')

    def __str__(self):
        return f"{self.requester} -> {self.receiver} ({self.status})"
