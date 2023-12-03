from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class User(AbstractUser):
    pass

class Category(models.Model):
    cate_name = models.CharField(max_length=50)

    def __str__(self):
        return self.cate_name

class Post(models.Model):
    cate = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    p_title = models.CharField(max_length=50)
    p_desc = models.CharField(max_length=100)
    p_contents = models.TextField()
    p_created = models.DateTimeField(auto_now_add=True, null=True)
    p_updated = models.DateTimeField(auto_now=True, null=True)
    thumbnail = models.ImageField(upload_to="post", blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.p_title

class Comments(models.Model):
    p = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    c_user_id = models.CharField(max_length=20)
    c_user_pw = models.CharField(max_length=20)
    c_contents = models.TextField()
    c_created = models.DateTimeField(auto_now_add=True)
    c_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.c_contents
    
# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, username, password=None, **extra_fields):
#         if not email:
#             raise ValueError('이메일 주소를 입력해야 합니다.')
#         email = self.normalize_email(email)
#         user = self.model(email=email, username=username, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, username, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('슈퍼유저는 is_staff=True여야 합니다.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('슈퍼유저는 is_superuser=True여야 합니다.')

#         return self.create_user(email, username, password, **extra_fields)

# class CustomUser(AbstractUser, PermissionsMixin):
#     email = models.EmailField(unique=True)
#     username = models.CharField(max_length=100, unique=True)
#     date_joined = models.DateTimeField(default=timezone.now)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']