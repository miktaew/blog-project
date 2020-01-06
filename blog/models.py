from django.contrib.auth.models import User
from django.db import models
from django.forms.models import model_to_dict, ModelForm
# everything CASCADE for now
from django.http import HttpResponse
from django.utils import timezone


class Blog(models.Model):  # blogs
    name = models.CharField(unique=True, max_length=60)
    description = models.TextField(blank=True, default="Welcome to my blog", max_length=600)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="blog")
    creation_date = models.DateTimeField(editable=False)
    active = models.BooleanField(default=True, blank=False)

    @staticmethod
    def get_blog_by_name(blog_name):
        try:
            b = Blog.objects.get(name=blog_name)
        except Blog.DoesNotExist:
            return -1
        return b
    # this seems really stupid

    @staticmethod
    def get_blog_posts(blog_name):
        b = Post.objects.filter(blog__name=blog_name).order_by('-creation_date')
        return list(b)

    @staticmethod
    def get_blogs():
        b = Blog.objects.filter(active=True)
        return list(b)

    @staticmethod
    def get_blogs_newest():
        b = Blog.objects.filter(active=True).order_by('-creation_date')[:10]
        return list(b)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.creation_date = timezone.now()
        return super(Blog, self).save(*args, **kwargs)


class Picture(models.Model):
    url = models.TextField()
    # it will only store picture links (pictures stored on server) I guess,
    # not sure though


class Post(models.Model):  # blog post
    title = models.CharField(max_length=360)
    content = models.TextField()
    creation_date = models.DateTimeField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='likes_post', default=0)
    pictures = models.ForeignKey(Picture, null=True, blank=True, on_delete=models.CASCADE)
    # reblogging???

    def save(self, *args, **kwargs):
        if not self.id:
            self.creation_date = timezone.now()
        return super(Post, self).save(*args, **kwargs)


class Comment(models.Model):  # comments on articles
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    commented_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    likes = models.ManyToManyField(User, related_name='likes_comment', default=0)
    def __str__(self):
        return f'{self.author}: {self.content}'
