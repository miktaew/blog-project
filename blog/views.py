from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader, RequestContext
from django.urls import reverse_lazy
from django.views import generic

from blog.forms import BlogForm, RawBlogForm
from blog.models import Blog


def index(request):
    template = loader.get_template('blog/index.html')
    return HttpResponse(template.render({"request": request}))


# def create_blog_view(request):
#     form = RawBlogForm(initial={'owner': request.user})
#     if request.method == "POST":
#         form = RawBlogForm(request.POST)
#         if form.is_valid():
#             print(form.cleaned_data)
#             #  Blog.objects.create(**form.cleaned_data)
#         else:
#             print(form.errors)
#     context = {'form': form}
#     return render(request, 'blog/blog_create.html', context)

def create_blog_view(request):
    form = BlogForm(request.POST or None, initial={'owner': request.user})
    if form.is_valid():
        form.save()
    context = {'form': form}
    return render(request, 'blog/blog_create.html', context)


def blog(request, blog_name):
    requested_blog = Blog.getByName(blog_name)
    if type(requested_blog) is dict:
        request = {"request": request, "blog": requested_blog, "posts": Blog.getBlogPosts(blog_name)}
        template = loader.get_template('blog/blog.html')

        return HttpResponse(template.render(request))  # this is not the same "request" as
        #                                                in functions above, don't be mistaken
    else:
        # template = loader.get_template('blog/notFound.html')
        # return HttpResponse(template.render())
        response = redirect('/')
        return response


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'blog/signup.html'


class BlogListView(generic.ListView):
    model = Blog
    context_object_name = 'blogs'

