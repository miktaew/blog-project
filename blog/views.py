from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader, RequestContext
from django.urls import reverse_lazy
from django.views import generic

from blog.forms import BlogForm, RawBlogForm, BlogDeactivationForm, BlogReactivationForm, BlogNewPostForm, PostUpdateForm, BlogUpdateForm, BlogPostCommentForm
from blog.models import Blog, Post, Comment


def index(request):
    context = {"blogs": Blog.get_blogs_newest()}
    return render(request, 'index.html', context)

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
    requested_blog = Blog.get_blog_by_name(blog_name)
    if requested_blog is not -1:
        posts_list = Blog.get_blog_posts(blog_name)
        page = request.GET.get('page', 1)
        paginator = Paginator(posts_list, 10)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context = {"blog": requested_blog, "posts": posts}
        return render(request, 'blog/blog.html', context)
    else:
        return redirect('/')


def manage_blog_view(request):
    blog = Blog.get_blog_by_name(request.user.blog.name)
    print(request.POST)
    if request.method == 'POST':
        if any(['deactivate-deactivation_password' in request.POST, 'reactivate-reactivation_password' in request.POST]):
            deactivation_form = BlogDeactivationForm(request.POST, user=request.user, prefix='deactivate')
            reactivation_form = BlogReactivationForm(request.POST, user=request.user, prefix='reactivate')
            update_blog_form = BlogUpdateForm(prefix='update')

            if deactivation_form.is_valid():
                Blog.objects.filter(pk=blog.id).update(active=False)
                Post.objects.filter(blog__id=blog.id).delete()
                return redirect("/")

            if reactivation_form.is_valid():
                Blog.objects.filter(pk=blog.id).update(active=True)
                return redirect(f"/blogs/{blog.name}/")

        elif 'update-description' in request.POST:
            update_blog_form = BlogUpdateForm(request.POST, instance=blog, prefix='update')
            deactivation_form = BlogDeactivationForm(user=request.user, prefix='deactivate')
            reactivation_form = BlogReactivationForm(user=request.user, prefix='reactivate')

            if update_blog_form.is_valid():
                update_blog_form.save()

    else:
        deactivation_form = BlogDeactivationForm(user=request.user, prefix='deactivate')
        reactivation_form = BlogReactivationForm(user=request.user, prefix='reactivate')
        update_blog_form = BlogUpdateForm(instance=blog, prefix='update')

    context = {"blog": blog, "deactivation_form": deactivation_form, "reactivation_form": reactivation_form,
               'update_blog_form': update_blog_form}
    return render(request, 'blog/blog_manage.html', context)
# it's terrible, but it seems to work properly


def blog_new_post(request):
    blog = request.user.blog
    create_post_form = BlogNewPostForm(request.POST or None, initial={"blog": request.user.blog.id})
    if create_post_form.is_valid():
        create_post_form.save()
        return redirect(f"/blogs/{blog.name}/")
    context = {"blog": blog, "create_post_form": create_post_form }
    return render(request, 'blog/blog_create_post.html', context)


def delete_post_view(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        if request.method == "POST":
            post.delete()
        return redirect(f"/blogs/{request.user.blog.name}/")
    except Exception:
        return redirect('/')


def update_post_view(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        blog = request.user.blog
        update_post_form = PostUpdateForm(request.POST or None, instance = post)
        context = {"blog": blog, "post": post, "update_post_form": update_post_form}

        if request.method == "POST" and update_post_form.is_valid():
            update_post_form.save()
            return redirect(f"/blogs/{blog.name}/")
        return render(request, 'blog/blog_update_post.html', context)
    except Exception:
        return redirect('/')


def blog_view_post(request, post_id, blog_name):
    post = Post.objects.get(id=post_id)
    comments = post.comments.all().order_by('-id')
    if request.user:
        if request.method == 'POST':
            post_comment_form = BlogPostCommentForm(request.POST, initial={"commented_post": post.id, "author": request.user.id}, prefix='comment')
            if post_comment_form.is_valid():
                post_comment_form.save()
                post_comment_form = BlogPostCommentForm()
                print('commented')
                return redirect(f'/blogs/{blog_name}/post/{post.id}/')
            else:
                print(post_comment_form.errors)

        else:
            post_comment_form = BlogPostCommentForm(initial={"commented_post": post.id, "author": request.user.id}, prefix='comment')
        context = {'post_comment_form': post_comment_form, 'post': post, 'comments': comments}
    else:
        context = {'post': post, 'comments': comments}
    return render(request, 'blog/blog_view_post.html', context)


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'blog/signup.html'