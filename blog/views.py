from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from blog.models import Blog


def index(request):
    template = loader.get_template('blog/index.html')
    return HttpResponse(template.render())


def blog(request, blog_name):

    requested_blog = Blog.getByName(blog_name)
    # maybe somehow check if blog with given name exists and if not, return some custom error site?
    if type(requested_blog) is dict:
        template = loader.get_template('blog/blog.html')
        return HttpResponse(template.render(requested_blog))
    else:
        template = loader.get_template('blog/notFound.html')
        return HttpResponse(template.render())
    # just use blog_name to get blog data as dictionary and put it as template.render() argument, should work
