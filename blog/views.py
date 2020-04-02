from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.db.models import Count, Q
from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader, RequestContext
from django.urls import reverse_lazy
from django.views import generic
from django.utils import timezone

from blog import misc
from blog.forms import BlogForm, RawBlogForm, BlogDeactivationForm, BlogReactivationForm, BlogNewPostForm, \
    PostUpdateForm, BlogUpdateForm, BlogPostCommentForm, ImageForm, CaseInsensitiveUserCreationForm, PrivateMessageForm, \
    ParentlessPrivateMessageForm
from blog.models import Blog, Post, Comment, Image, LastVisit, FavouriteBlogs, PrivateMessage, LikedPosts


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
    context = {}

    if requested_blog:

        if request.user.is_authenticated:
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

            context['is_faved'] = is_faved

        posts_list = Blog.get_blog_posts(blog_name)
        content = []
        for post in posts_list:
            try:
                try:
                    post_count = post.comments.all().count()
                except IndexError:
                    post_count = 0

                try:
                    image = post.images.all()[0]
                    image_count = post.images.all().count()
                except IndexError:
                    image = None
                    image_count = 0

                try:
                    like_count = post.post_likes.all().count()
                except IndexError:
                    like_count = 0

                if request.user.is_authenticated:
                    is_liked = LikedPosts.objects.filter(post=Post.objects.get(id=post.id), user=request.user).exists()
                else:
                    is_liked = False

                content.append({'post': post, 'image': image, 'image_count': image_count, 'post_count': post_count, 'like_count': like_count, 'is_liked': is_liked})
            except Exception as e:
                print(e)
                continue

        favcount = Blog.get_blog_favcount(blog_name)

        ordering = request.GET.get('sorting_order')
        # print("ordering: " + ordering)

        if ordering == 'newest' or ordering is None:
            content.sort(key=lambda post: post['post'].creation_date, reverse=True)

        elif ordering == 'oldest':
            content.sort(key=lambda post: post['post'].creation_date)

        elif ordering == 'best':
            content.sort(key=lambda post: post['like_count'], reverse=True)

        page = request.GET.get('page', 1)
        paginator = Paginator(content, 10)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context.update({"blog": requested_blog, "posts": posts, 'favcount': favcount, 'sorting_order': ordering})
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
    except Exception as e:
        print(e)
        return redirect('/')


@login_required
def add_to_favs(request, blog_name):
    try:
        if request.method == "POST":
            faved_blog = Blog.get_blog_by_name(blog_name)
            if not FavouriteBlogs.objects.filter(user=request.user, blog=faved_blog).exists():
                fave = FavouriteBlogs(user=request.user, blog=faved_blog)
                fave.save()
    except Exception as e:
        print(e)
        return redirect(f"/blogs/{blog_name}/")
    return redirect(f"/blogs/{blog_name}/")


@login_required
def remove_from_favs(request, blog_name):
    try:
        faved_blog = Blog.get_blog_by_name(blog_name)
        fave = FavouriteBlogs.objects.get(user=request.user, blog=faved_blog)
        if request.method == "POST":
            fave.delete()
    except Exception as e:
        print(e)
        return redirect(f"/blogs/{blog_name}/")
    return redirect(f"/blogs/{blog_name}/")


@login_required
def like_post(request, blog_name, post_id):
    try:
        if request.method == "POST":
            post = Post.objects.get(id=post_id)
            if not LikedPosts.objects.filter(user=request.user, post=post).exists():
                like = LikedPosts(user=request.user, post=post)
                like.save()

            if request.GET.get("main") == 'true':
                return redirect(f"/blogs/{blog_name}?page={request.get.GET('page')}/")
            else:
                return redirect(f"/blogs/{blog_name}/post/{post_id}/")
    except Exception as e:
        print(e)
        return redirect(f"/blogs/{blog_name}/")


@login_required
def remove_from_likes(request, blog_name, post_id):
    try:
        if request.method == "POST":
            post = Post.objects.get(id=post_id)
            like = LikedPosts.objects.get(user=request.user, post=post)
            like.delete()

        if request.GET.get("main") == 'true':
            return redirect(f"/blogs/{blog_name}?page={request.get.GET('page')}/")
        else:
            return redirect(f"/blogs/{blog_name}/post/{post_id}/")
    except Exception as e:
        print(e)
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

                            except Exception as e:
                                print(e)

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

    context = {'post': post, 'images': images}

    try:
        LikedPosts.objects.get(user=request.user, post=Post.objects.get(id=post_id))
        is_liked = True
    except LikedPosts.DoesNotExist:
        is_liked = False
    except TypeError:
        is_liked = False

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
        context['post_comment_form'] = post_comment_form
        context['images'] = images

    page = request.GET.get('page', 1)
    paginator = Paginator(comments, 20)

    try:
        comment_list = paginator.page(page)
    except PageNotAnInteger:
        comment_list = paginator.page(1)
    except EmptyPage:
        comment_list = paginator.page(paginator.num_pages)

    context['like_count'] = LikedPosts.objects.filter(post=post).count()
    context['comments'] = comment_list
    context['is_liked'] = is_liked

    return render(request, 'blog/blog_view_post.html', context)


@login_required
def private_messages_view(request):
    # all messages from/to current user
    all_messages = PrivateMessage.objects.filter(Q(receiver=request.user) | Q(sender=request.user))

    # takes parent id from messages with parent
    parents = all_messages.exclude(parent=None).values('parent__id').distinct()
    # removes parents from queryset, only non-parents remain
    nonparent_messages = all_messages.exclude(id__in=parents)

    # first group - have no parent AND are not a parent
    solo_messages = nonparent_messages.filter(parent=None)

    # second group - newest from each conversation
    nonsolo_list = []
    for parent in parents:
        newest = all_messages.filter(parent=parent['parent__id']).order_by('-creation_date')[0]  # powinno dzialac?
        count = all_messages.filter(parent=parent['parent__id']).count()
        nonsolo_list.append({'message': newest, 'count': count})

    solo_list = []
    for message in solo_messages:
        solo_list.append({'message': message})

    message_list = solo_list + nonsolo_list

    ordering = request.GET.get('sorting_order')
    # print("ordering: " + ordering)

    if ordering == 'newest' or ordering is None:
        message_list.sort(key=misc.private_message_date, reverse=True)

    elif ordering == 'oldest':
        message_list.sort(key=misc.private_message_date)

    elif ordering == 'new_unread':
        message_list = misc.private_message_unread_new_sort(request, message_list)

    elif ordering == 'old_unread':
        message_list = misc.private_message_unread_old_sort(request, message_list)

    page = request.GET.get('page', 1)
    paginator = Paginator(message_list, 20)

    try:
        messages = paginator.page(page)
    except PageNotAnInteger:
        messages = paginator.page(1)
    except EmptyPage:
        messages = paginator.page(paginator.num_pages)

    context = {"messages": messages, 'sorting_order': ordering}

    return render(request, 'messaging/messages.html', context)


@login_required
def private_message_view(request, message_id):
    try:
        PrivateMessage.objects.filter(pk=message_id, receiver=request.user).update(read=True)
        if PrivateMessage.objects.get(pk=message_id).parent:
            parent = PrivateMessage.objects.get(pk=message_id).parent
            title = PrivateMessage.objects.get(pk=parent.id).title
            messages = PrivateMessage.objects.filter(parent=parent) | PrivateMessage.objects.filter(pk=parent.id)
            messages.filter(read=False, receiver=request.user).update(read=True)
            messages = messages.order_by('-creation_date')

        else:
            parent = PrivateMessage.objects.get(pk=message_id)
            messages = PrivateMessage.objects.filter(pk=message_id) | PrivateMessage.objects.filter(parent=message_id)
            title = PrivateMessage.objects.get(pk=message_id).title

        if PrivateMessage.objects.get(pk=message_id).receiver == request.user:
            receiver = PrivateMessage.objects.get(pk=message_id).sender
        else:
            receiver = PrivateMessage.objects.get(pk=message_id).receiver

        if request.method == 'POST':

            private_message_form = PrivateMessageForm(request.POST,
                                                      initial={"sender": request.user.id, "receiver": receiver.id,
                                                               "title": f"Re: {title}", "parent": parent.id})
            if private_message_form.is_valid():
                private_message_form.save()
                private_message_form = PrivateMessageForm()
                return redirect(f"/messages/{message_id}/")

            else:
                print(private_message_form.errors)

        else:
            private_message_form = PrivateMessageForm(initial={"sender": request.user.id, "receiver": receiver.id, "title": f"Re: {title}", "parent": parent.id})

        messages = messages.order_by('-creation_date')

        # print(messages)

        page = request.GET.get('page', 1)
        paginator = Paginator(messages, 10)

        try:
            message_list = paginator.page(page)
        except PageNotAnInteger:
            message_list = paginator.page(1)
        except EmptyPage:
            message_list = paginator.page(paginator.num_pages)

        context = {'messages': message_list, 'private_message_form': private_message_form}
        return render(request, 'messaging/message.html', context)

    except PrivateMessage.DoesNotExist:
        return redirect("/messages/")


@login_required
def new_private_message_view(request):
    if request.method == 'POST':
        private_message_form = ParentlessPrivateMessageForm(request.POST,initial={"sender": request.user.id})
        if private_message_form.is_valid():
            private_message_form.save()
            private_message_form = PrivateMessageForm()
            return redirect(f"/messages/")

        else:
            print(private_message_form.errors)

    else:
        private_message_form = ParentlessPrivateMessageForm(initial={"sender": request.user.id})

    context = {"private_message_form": private_message_form}
    return render(request, 'messaging/message_create.html', context)


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
    paginator = Paginator(res, 5)

    try:
        fav_blogs = paginator.page(page)
    except PageNotAnInteger:
        fav_blogs = paginator.page(1)
    except EmptyPage:
        fav_blogs = paginator.page(paginator.num_pages)

    context = {'fav_blogs': fav_blogs, 'sorting_order': ordering}
    return render(request, 'favourite/favourite.html', context)


class SignUp(generic.CreateView):
    form_class = CaseInsensitiveUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'blog/signup.html'
