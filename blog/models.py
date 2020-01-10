from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.db.models import Count
from django.forms.models import model_to_dict, ModelForm
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from django.utils import timezone


class Blog(models.Model):  # blogs
    name = models.CharField(unique=True, max_length=60)
    description = models.TextField(blank=True, default="Welcome to my blog", max_length=600)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="blog")
    creation_date = models.DateTimeField(editable=False)
    latest_post_date = models.DateTimeField(default=timezone.now())
    active = models.BooleanField(default=True, blank=False)

    @staticmethod
    def get_blog_by_name(blog_name):
        try:
            b = Blog.objects.get(name=blog_name)
        except Blog.DoesNotExist:
            return
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
        b = Blog.objects.filter(active=True).order_by('-creation_date')[:5]
        return list(b)

    @staticmethod
    def get_blogs_top():
        b = Blog.objects.annotate(faves=Count('blog_favs')).order_by('-faves')[:5]
        return list(b)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.creation_date = timezone.now()
            self.latest_post_date = self.creation_date
        return super(Blog, self).save(*args, **kwargs)


class Post(models.Model):  # blog post
    title = models.CharField(max_length=360)
    content = models.TextField()
    creation_date = models.DateTimeField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='post_blog')
    likes = models.ManyToManyField(User, related_name='likes_post', default=0)
    # reblogging???

    def save(self, *args, **kwargs):
        if not self.id:
            self.creation_date = timezone.now()
            Blog.objects.filter(pk=self.blog.id).update(latest_post_date=self.creation_date)
        return super(Post, self).save(*args, **kwargs)

    def get_image_filename(self, filename):
        title = self.post.title
        slug = slugify(title)
        return "media/post_images/%s-%s" % (slug, filename)


class Image(models.Model):
    post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=Post.get_image_filename, verbose_name='Image')


class Comment(models.Model):  # comments on articles
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    commented_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    likes = models.ManyToManyField(User, related_name='likes_comment', default=0)

    def __str__(self):
        return f'{self.author}: {self.content}'


class LastVisit(models.Model):
    date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visits')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='visits')


class FavouriteBlogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_favs')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='blog_favs')
