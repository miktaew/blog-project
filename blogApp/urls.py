from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.views.generic import RedirectView

from blog import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blogs/<blog_name>/', views.blog),
    path('', views.index, name='main_page'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('blogs/', RedirectView.as_view(pattern_name="main_page", permanent=False)),
    path('create/', views.create_blog_view, name='blog_create'),

    #path(r'^(?P<url>./)$', lambda request: redirect('', permanent=False)),
]
