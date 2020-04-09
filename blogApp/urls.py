from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include, re_path
from django.views.generic import RedirectView

from blog import views
from blogApp import settings

urlpatterns = [
    path('', views.index, name='main_page'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls, name='admin_page'),

    path('blogs/<blog_name>/', views.blog, name='blog_page'),
    path('blogs/<blog_name>/add_to_favourites/', views.add_to_favs, name='blog_fave'),
    path('blogs/<blog_name>/remove_from_favourites/', views.remove_from_favs, name='blog_unfave'),
    path('blogs/<blog_name>/post/<post_id>/like/', views.like_post, name='post_like'),
    path('blogs/<blog_name>/post/<post_id>/unlike/', views.remove_from_likes, name='post_unlike'),
    path('blogs/<blog_name>/post/<post_id>/', views.blog_view_post, name='post_page'),

    path('blog/post/create/', views.blog_new_post, name='blog_new_post'),
    path('blog/post/delete/<post_id>/', views.delete_post_view, name='delete_post'),
    path('blog/post/like/<post_id>/', views.like_post, name='like_post'),
    path('blog/post/update/<post_id>/', views.update_post_view, name='update_post'),
    path('blog/settings/', views.manage_blog_view, name='blog_settings'),

    path('create/', views.create_blog_view, name='blog_create'),
    path('favourite/', views.favs_list_view, name='favourite'),

    path('messages/', views.private_messages_view, name='private_messages'),
    path('messages/create/', views.new_private_message_view, name='new_message'),
    path('messages/<message_id>/', views.private_message_view, name='private_message'),

    path('search/', views.search_blogs_view, name='search'),
    path('signup/', views.SignUp.as_view(), name='signup'),


    re_path(r'^.*/$', RedirectView.as_view(pattern_name="main_page", permanent=False)),
    # redirects everything else to the main page
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
