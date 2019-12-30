from django.contrib.auth.models import User
from django.db import models
from django.forms.models import model_to_dict, ModelForm
# everything CASCADE for now
from django.http import HttpResponse


class Blog(models.Model):  # blogs
    name = models.TextField(unique=True)
    description = models.TextField(blank=True, default="Welcome to my blog")
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="blog")

    @staticmethod
    def getByName(blog_name):
        try:
            b = Blog.objects.get(name=blog_name)
        except Blog.DoesNotExist:
            return -1
        return model_to_dict(b)

    @staticmethod
    def getBlogPosts(blog_name):  # NOT TESTED YET
        b = Post.objects.filter(blog__name=blog_name)
        return list(b)

    def __str__(self):
        return self.name


class Picture(models.Model):
    url = models.TextField()
    # it will only store picture links (pictures stored on server) I guess,
    # might change later


class Post(models.Model):  # blog post
    title = models.TextField()
    content = models.TextField()
    postDate = models.DateTimeField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='likes_post', blank=True)
    pictures = models.ForeignKey(Picture, null=True, blank=True, on_delete=models.CASCADE)
    # reblogging???


class Comment(models.Model):  # comments on articles
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    commentedPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='likes_comment')


class BlogForm(ModelForm):
    class Meta:
        model = Blog
        fields = ['name', 'description', 'owner']
