from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from blog.models import Blog, Post, Comment, Image


class BlogForm(forms.ModelForm):
    name = forms.CharField(
        max_length=60,
        required=True,
        help_text='Select the name of your blog. Be careful though, as it cannot be changed later'
    )
    description = forms.CharField(
        required=False,
        initial="Welcome to my blog!",
        help_text='Blog description can be changed at any time. You can also leave it default or empty',
        widget=forms.Textarea(
            attrs={
                "rows": 4
            }
        )
    )
    owner = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Blog
        fields = [
            'name',
            'description',
            'owner',
        ]
        widgets = {'owner': forms.HiddenInput()}


class RawBlogForm(forms.Form):
    name = forms.CharField(
        max_length=60,
        required=True,
        help_text='Select the name of your blog. Be careful though, as it cannot be changed later'
    )
    description = forms.CharField(
        required=False,
        initial="Welcome to my blog!",
        help_text='Description can be changed at any time in blog settings. You can also leave it default or empty',
        widget=forms.Textarea(
            attrs={
                "rows": 4
            }
        )
    )
    owner = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.HiddenInput(),
    )

    def __init__(self, *args, **kwargs):
        super(RawBlogForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_id = 'id-blogForm' # or whatever
        # self.helper.form_class = 'formsClass' # or whatever
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save blog'))


class BlogDeactivationForm(forms.Form):
    confirm_name = forms.CharField(max_length=60,
                                   required=True,
                                   help_text="Confirm name of your blog",)
    # No, blog for deletion is not taken from this field, it's just for confirmation
    deactivation_password = forms.CharField(label="Password",
                                            help_text="Confirm password for deactivation",
                                            widget=forms.PasswordInput)

    class Meta:
        fields = [
            'confirm_name',
            'deactivation_password',
        ]

    def __init__(self, *args, **kwargs):
        # print("kwargs:"+str(kwargs["user"]))
        self.user = kwargs.pop('user')
        super(BlogDeactivationForm, self).__init__(*args, **kwargs)

    def clean_deactivation_password(self):
        deactivation_password = self.cleaned_data['deactivation_password']
        valid = check_password(deactivation_password, self.user.password)
        if not valid:
            raise forms.ValidationError('Invalid password')
        return deactivation_password

    def clean_confirm_name(self):
        confirm_name = self.cleaned_data['confirm_name']
        valid = confirm_name == self.user.blog.name
        if not valid:
            raise forms.ValidationError('Invalid blog name')
        return confirm_name


class BlogReactivationForm(forms.Form):
    reactivation_password = forms.CharField(label="Password",
                                            help_text="Confirm password for reactivation",
                                            widget=forms.PasswordInput)

    class Meta:

        fields = [
            'reactivation_password',
        ]

    def __init__(self, *args, **kwargs):
        # print("kwargs:"+str(kwargs["user"]))
        self.user = kwargs.pop('user')
        super(BlogReactivationForm, self).__init__(*args, **kwargs)

    def clean_reactivation_password(self):
        reactivation_password = self.cleaned_data['reactivation_password']
        valid = check_password(reactivation_password, self.user.password)
        if not valid:
            raise forms.ValidationError('Invalid password')
        return reactivation_password


class BlogNewPostForm(forms.ModelForm):
    title = forms.CharField(
        help_text="Title of new post",
        required=True,
        max_length=600,
    )
    content = forms.CharField(
        required=True,
        widget=forms.Textarea()
    )
    blog = forms.ModelChoiceField(
        queryset=Blog.objects.all(),
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'blog',
        ]
        widgets = {'blog': forms.HiddenInput(), 'content': forms.Textarea()}


class ImageForm(forms.ModelForm):
    image = forms.ImageField(label='Image', required=False)

    class Meta:
        model = Image
        fields = [
            'image',
        ]


class PostUpdateForm(forms.ModelForm):
    title = forms.CharField(
        required=True,
        max_length=600,
    )
    content = forms.CharField(
        required=True,
        widget=forms.Textarea()
    )

    class Meta:
        model = Post
        fields = [
            'title',
            'content',
        ]
        widgets = {"content": forms.Textarea()}


class DeletePostForm(forms.ModelForm):
    pass


class BlogUpdateForm(forms.ModelForm):
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(),
        max_length=600,
    )

    class Meta:
        model = Blog
        fields = [
            'description',
        ]
        widgets = {'description': forms.Textarea()}


class BlogPostCommentForm(forms.ModelForm):
    content = forms.CharField(
        required=True,
        max_length=600,
        label='',
        widget=forms.Textarea(
            attrs={"rows":5},
        ),
    )

    author = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.HiddenInput(),
    )

    commented_post = forms.ModelChoiceField(
        queryset=Post.objects.all(),
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Comment
        fields = [
            'content',
            'author',
            'commented_post',
        ]
        widgets = {
            'author': forms.HiddenInput(),
            'commented_post': forms.HiddenInput(),
            'content': forms.Textarea(),
        }


class CaseInsensitiveUserCreationForm(UserCreationForm):
    def clean(self):
        cleaned_data = super(CaseInsensitiveUserCreationForm, self).clean()
        username = cleaned_data.get('username')
        if username and User.objects.filter(username__iexact=username).exists():
            self.add_error('username', 'A user with that username already exists.')
        return cleaned_data
