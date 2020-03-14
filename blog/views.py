from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.db.models import Count
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader, RequestContext
from django.urls import reverse_lazy
from django.views import generic
from django.utils import timezone

from blog import misc
from blog.forms import BlogForm, RawBlogForm, BlogDeactivationForm, BlogReactivationForm, BlogNewPostForm, \
    PostUpdateForm, BlogUpdateForm, BlogPostCommentForm, ImageForm, CaseInsensitiveUserCreationForm
from blog.models import Blog, Post, Comment, Image, LastVisit, FavouriteBlogs


def index(request):
    newest_blogs = Blog.get_blogs_newest()
    top_blogs = Blog.get_blogs_top()
    context = {"new_blogs": newest_blogs, "top_blogs": top_blogs}
    return render(request, 'index.html', context)


@login_required
def create_blog_view(request):
    form = BlogForm(request.POST or None, initial={'owner': request.user})
    if request.method == "POST":
        if form.is_valid():
            form.save()
    context = {'form': form}
    return render(request, 'blog/blog_create.html', context)


def blog(request, blog_name):
    requested_blog = Blog.get_blog_by_name(blog_name)
    if requested_blog:

        try:
            last_visit = LastVisit.objects.get(user=request.user, blog=requested_blog)
            last_visit.date = timezone.now()
            last_visit.save()
        except LastVisit.DoesNotExist:
            last_visit = LastVisit(user=request.user, blog=requested_blog, date=timezone.now())
            last_visit.save()
        except TypeError:
            pass

        try:
            FavouriteBlogs.objects.get(user=request.user, blog=requested_blog)
            is_faved = True
        except FavouriteBlogs.DoesNotExist:
            is_faved = False
        except TypeError:
            is_faved = False

        posts_list = Blog.get_blog_posts(blog_name)
        content = []
        for post in posts_list:
            try:
                try:
                    post_count = post.comments.all().count()
                except IndexError:
                    post_count = 0
                image = post.images.all()[0]
                image_count = post.images.all().count()
                content.append({'post': post, 'image': image, 'image_count': image_count, 'post_count': post_count})
            except IndexError:
                content.append({'post': post, 'image': None, 'image_count': 0, 'post_count': post_count})
            except Exception:
                continue

        favcount = Blog.get_blog_favcount(blog_name)
        print(favcount)
        page = request.GET.get('page', 1)
        paginator = Paginator(content, 10)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context = {"blog": requested_blog, "posts": posts, 'is_faved': is_faved, 'favcount': favcount}
        return render(request, 'blog/blog.html', context)
    else:
        return redirect('/')


@login_required
def manage_blog_view(request):
    blog = Blog.get_blog_by_name(request.user.blog.name)
    print(request.POST)
    if request.method == 'POST':
        if any(['deactivate-deactivation_password' in request.POST,
                'reactivate-reactivation_password' in request.POST]):
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


@login_required
def blog_new_post(request):
    blog = request.user.blog
    ImageFormSet = modelformset_factory(Image, form=ImageForm, extra=3)
    if request.method == 'POST':
        create_post_form = BlogNewPostForm(request.POST)
        image_formset = ImageFormSet(request.POST, request.FILES, queryset=Image.objects.none())

        if create_post_form.is_valid() and image_formset.is_valid():
            post_form = create_post_form.save(commit=False)
            post_form.blog = request.user.blog
            post_form.save()
            for form in image_formset.cleaned_data:
                if form:
                    image = form['image']
                    photo = Image(post=post_form, image=image)
                    photo.save()

            return redirect(f"/blogs/{blog.name}/")
        else:
            print(create_post_form.errors, image_formset.errors)
    else:
        create_post_form = BlogNewPostForm(initial={"blog": request.user.blog.id})
        image_formset = ImageFormSet(queryset=Image.objects.none())
    context = {"blog": blog, "create_post_form": create_post_form, 'image_formset': image_formset}
    return render(request, 'blog/blog_create_post.html', context)


@login_required
def delete_post_view(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        images = Image.objects.filter(post=post)
        if request.method == "POST":
            post.delete()
            images.delete()
        return redirect(f"/blogs/{request.user.blog.name}/")
    except Exception:
        return redirect('/')


@login_required
def add_to_favs(request, blog_name):
    try:
        if request.method == "POST":
            faved_blog = Blog.get_blog_by_name(blog_name)
            if not FavouriteBlogs.objects.filter(user=request.user, blog=faved_blog).exists():
                fave = FavouriteBlogs(user=request.user, blog=faved_blog)
                fave.save()
    except Exception:
        return redirect(f"/blogs/{blog_name}/")
    return redirect(f"/blogs/{blog_name}/")


@login_required
def remove_from_favs(request, blog_name):
    try:
        faved_blog = Blog.get_blog_by_name(blog_name)
        fave = FavouriteBlogs.objects.get(user=request.user, blog=faved_blog)
        if request.method == "POST":
            fave.delete()
    except Exception:
        return redirect(f"/blogs/{blog_name}/")
    return redirect(f"/blogs/{blog_name}/")


@login_required
def update_post_view(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        blog = request.user.blog

        image_count = Image.objects.filter(post=post_id).count()
        ImageFormSet = modelformset_factory(Image, form=ImageForm, can_delete=True, extra=3-image_count)

        image_formset = ImageFormSet(queryset=Image.objects.filter(post=post_id))
        update_post_form = PostUpdateForm(request.POST or None, instance=post)

        if request.method == "POST":
            image_formset = ImageFormSet(request.POST, request.FILES, queryset=Image.objects.filter(post=post_id))

            if update_post_form.is_valid() and image_formset.is_valid():
                update_post_form.save()

                for form in image_formset.cleaned_data:
                    if form:
                        image = form['image']

                        if form['DELETE']:
                            try:
                                photo = Image.objects.get(id=form['id'].id)
                                photo.delete()

                            except Exception:
                                pass

                        elif form['id'] is not None:
                            try:
                                photo = Image.objects.get(id=form['id'].id)
                                photo.delete()
                                photo = Image(post=post, image=image)
                                photo.save()

                            except Exception:
                                pass

                        else:
                            photo = Image(post=post, image=image)
                            photo.save()

                return redirect(f'/blog/post/update/{post_id}/')

            else:
                print('Error: ', end='')
                print(update_post_form.errors, image_formset.errors)

        context = {"blog": blog, "post": post, "update_post_form": update_post_form, 'image_formset': image_formset}
        return render(request, 'blog/blog_update_post.html', context)

    except Exception:
        return redirect('/')


def blog_view_post(request, post_id, blog_name):
    post = Post.objects.get(id=post_id)
    comments = post.comments.all().order_by('-id')
    images = post.images.all()
    if request.user:
        if request.method == 'POST':
            post_comment_form = BlogPostCommentForm(request.POST,
                                                    initial={"commented_post": post.id, "author": request.user.id},
                                                    prefix='comment')
            if post_comment_form.is_valid():
                post_comment_form.save()
                post_comment_form = BlogPostCommentForm()

                return redirect(f'/blogs/{blog_name}/post/{post.id}/')
            else:
                print(post_comment_form.errors)

        else:
            post_comment_form = BlogPostCommentForm(initial={"commented_post": post.id, "author": request.user.id},
                                                    prefix='comment')
        context = {'post_comment_form': post_comment_form, 'post': post, 'comments': comments, 'images': images}
    else:
        context = {'post': post, 'comments': comments, 'images': images}
    return render(request, 'blog/blog_view_post.html', context)


@login_required
def favs_list_view(request):
    favs = FavouriteBlogs.objects.filter(user=request.user)
    res = []
    for fav in favs:
        tmp = LastVisit.objects.get(user=request.user, blog=fav.blog)
        # print(tmp)
        count = Post.objects.filter(blog=fav.blog, creation_date__gte=tmp.date).count()
        # print(count)
        res.append({"blog": fav.blog, "count": count})

    ordering = request.GET.get('sorting_order')
    if ordering == 'new_count':
        res.sort(key=misc.fav_key_favs, reverse=True)

    elif ordering == 'alphabetical':
        res = misc.favs_adv_sort(res)

    page = request.GET.get('page', 1)
    paginator = Paginator(res, 20)


    try:
        fav_blogs = paginator.page(page)
    except PageNotAnInteger:
        fav_blogs = paginator.page(1)
    except EmptyPage:
        fav_blogs = paginator.page(paginator.num_pages)

    context = {'fav_blogs': fav_blogs, 'sorting_order': ordering,}
    return render(request, 'favourite/favourite.html', context)


class SignUp(generic.CreateView):
    form_class = CaseInsensitiveUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'blog/signup.html'
