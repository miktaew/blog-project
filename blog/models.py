from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.db.models import Count
from django.template.defaultfilters import slugify
from django.utils import timezone


class Topic(models.Model):
    name = models.TextField()

    def __str__(self):
        return f'{self.name} {self.id}'


class Blog(models.Model):  # blogs
    name = models.CharField(unique=True, max_length=60)  # this is actually blog URL, not the displayed name
    display_name = models.CharField(max_length=120, default="My Blog")
    description = models.TextField(blank=True, default="Welcome to my blog", max_length=600)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="blog")
    creation_date = models.DateTimeField(editable=False)
    latest_post_date = models.DateTimeField(default=timezone.now())
    active = models.BooleanField(default=True, blank=False)
    topics = models.ManyToManyField(Topic, blank=True)

    @staticmethod
    def get_blog_by_name(blog_name):
        try:
            b = Blog.objects.get(name=blog_name)
        except Blog.DoesNotExist:
            return
        return b
    # this seems really stupid

    @staticmethod
    def get_blog_favcount(blog_name):
        try:
            favcount = Blog.objects.annotate(faves=Count('blog_favs')).get(name=blog_name).faves  # ugly
        except Blog.DoesNotExist:
            return -1
        return favcount

    @staticmethod
    def get_blog_posts(blog_name):
        b = Post.objects.filter(blog__name=blog_name).order_by('-creation_date')
        return list(b)

    @staticmethod
    def get_blogs():
        b = Blog.objects.filter(active=True)
        return list(b)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.creation_date = timezone.now()
            self.latest_post_date = self.creation_date
        if self.name:
            self.name = self.name.strip()
        if self.display_name:
            self.display_name = self.display_name.strip()
        return super(Blog, self).save(*args, **kwargs)


class Post(models.Model):  # blog post
    title = models.CharField(max_length=360)
    content = models.TextField()
    creation_date = models.DateTimeField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='post_blog')

    def save(self, *args, **kwargs):
        if not self.id:
            self.creation_date = timezone.now()
            Blog.objects.filter(pk=self.blog.id).update(latest_post_date=self.creation_date)
        if self.title:
            self.title = self.title.strip()
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

    def save(self, *args, **kwargs):
        if self.content:
            self.content = self.content.strip()
        return super(Comment, self).save(*args, **kwargs)


class PrivateMessage(models.Model):
    creation_date = models.DateTimeField()
    read = models.BooleanField(default=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    hidden_by_sender = models.BooleanField(default=False)    # instead of deleting by users
    hidden_by_receiver = models.BooleanField(default=False)  # ^
    content = models.TextField()
    title = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    @staticmethod
    def get_unread(receiver):
        m = PrivateMessage.objects.filter(receiver=receiver, read=False, hidden_by_receiver=False)
        return list(m)

    @staticmethod
    def remove_all_from(sender):
        try:
            PrivateMessage.objects.filter(sender=sender, hidden_by_receiver=False).update(hidden_by_receiver=True)
        except Exception:
            return False
        return True

    def __str__(self):
        return f'{self.sender} to {self.receiver}: {self.title}'

    def save(self, *args, **kwargs):

        if self.parent:
            while self.parent.parent:
                self.parent = self.parent.parent

        if not self.id:
            self.creation_date = timezone.now()
        if self.title:
            self.title = self.title.strip()
        if self.content:
            self.content = self.content.strip()
        return super(PrivateMessage, self).save(*args, **kwargs)


class LastVisit(models.Model):
    date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visits')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='visits')


class FavouriteBlogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_favs')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='blog_favs')


class LikedPosts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')