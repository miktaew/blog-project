from django.db import models
from django.forms.models import model_to_dict
# everything CASCADE for now
from django.http import HttpResponse


class User(models.Model):  # users
    nick = models.TextField(unique=True)
    permissionLevel = models.TextField(default="user")
    # ^ will be something like "banned", "user" and "admin", that's all
    # password???
    # or however logging in will be done, idk


class Blog(models.Model):  # blogs
    name = models.TextField(unique=True)
    description = models.TextField(blank=True, default="Welcome to my blog")
    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    @staticmethod
    def getByName(blogname):
        try:
            b = Blog.objects.get(name=blogname)
        except Blog.DoesNotExist:
            return -1
        return model_to_dict(b)

class Picture(models.Model):
    url = models.TextField()
    # it will only store picture links (pictures stored on server) I guess,
    # might change later


class Post(models.Model):  # blog post
    title = models.TextField()
    content = models.TextField()
    postDate = models.DateTimeField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='likes_post')
    pictures = models.ForeignKey(Picture, null=True, on_delete=models.CASCADE)
    # reblogging???


class Comment(models.Model):  # comments on articles
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    commentedPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='likes_comment')