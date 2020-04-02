from django.contrib import admin
from .models import *

admin.site.register(Blog)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Image)
admin.site.register(LastVisit)
admin.site.register(FavouriteBlogs)
admin.site.register(PrivateMessage)
admin.site.register(Topic)