from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, MultiField, Div, Fieldset
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from blog.models import Blog, Post, Comment, Image, PrivateMessage, Topic


class BlogForm(forms.ModelForm):
    TOPIC_CHOICES = [[topic.id, topic.name] for topic in Topic.objects.all()]

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
    display_name = forms.CharField(
        required=True,
        help_text="Name of your blog",
        max_length=120
    )
    topics = forms.MultipleChoiceField(
        choices=TOPIC_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label='Select topics of your blog',
        help_text='You can change them at any time',
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
            'display_name',
            'owner',
            'topics',
        ]
        widgets = {
            'owner': forms.HiddenInput(),
            'topics': forms.CheckboxSelectMultiple(),
        }

    def clean_name(self):
        return self.cleaned_data.get('name', '').strip()

    def clean_display_name(self):
        return self.cleaned_data.get('display_name', '').strip()


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
    display_name = forms.CharField(
        required=True,
        initial="My Blog",
        help_text="Name of your blog",
        max_length=120
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

    def clean_name(self):
        return self.cleaned_data.get('name', '').strip()

    def clean_display_name(self):
        return self.cleaned_data.get('display_name', '').strip()


class BlogDeactivationForm(forms.Form):
    confirm_name = forms.CharField(max_length=120,
                                   required=True,
                                   help_text="Enter displayed blog name for confirmation",)
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
        valid = confirm_name == self.user.blog.display_name
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

    def clean_title(self):
        return self.cleaned_data.get('title', '').strip()


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

    def clean_title(self):
        return self.cleaned_data.get('title', '').strip()


class DeletePostForm(forms.ModelForm):
    pass


class BlogUpdateForm(forms.ModelForm):
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"rows":4},
        ),
        max_length=600,
    )
    display_name = forms.CharField(
        required=True,
        initial="My Blog",
        help_text="Name of your blog",
        max_length=120
    )

    class Meta:
        model = Blog
        fields = [
            'description',
            'display_name',
        ]
        widgets = {'description': forms.Textarea()}

    def clean_display_name(self):
        return self.cleaned_data.get('display_name', '').strip()


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

    def clean_content(self):
        return self.cleaned_data.get('content', '').strip()

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


class ParentlessPrivateMessageForm(forms.ModelForm):
    sender = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.HiddenInput(),
    )

    receiver = forms.CharField(

    )

    title = forms.CharField(

    )

    content = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 3},
        )
    )

    class Meta:
        model = PrivateMessage
        fields = [
            'sender',
            'receiver',
            'title',
            'content',
        ]
        widgets = {
            'sender': forms.HiddenInput(),
        }

    def clean_content(self):
        return self.cleaned_data.get('content', '').strip()

    def clean_title(self):
        return self.cleaned_data.get('title', '').strip()

    def clean_receiver(self):
        receiver = self.cleaned_data['receiver']

        if User.objects.filter(username__iexact=receiver):
            receiver = User.objects.filter(username__iexact=receiver)[0]
            valid = True
        else:
            valid = False

        if not valid:
            raise forms.ValidationError('Invalid receiver name')

        return receiver


class PrivateMessageForm(forms.ModelForm):
    sender = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.HiddenInput(),
    )

    receiver = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.HiddenInput(),
    )

    title = forms.CharField(

    )

    content = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 3},
        )
    )

    parent = forms.ModelChoiceField(
        queryset=PrivateMessage.objects.filter(parent=None),
        widget=forms.HiddenInput()
    )

    class Meta:
        model = PrivateMessage
        fields = [
            'sender',
            'receiver',
            'title',
            'content',
            'parent',
        ]
        widgets = {
            'sender': forms.HiddenInput(),
            'receiver': forms.HiddenInput(),
            'parent': forms.HiddenInput(),
        }

    def clean_content(self):
        return self.cleaned_data.get('content', '').strip()

    def clean_title(self):
        return self.cleaned_data.get('title', '').strip()


class BlogUpdateTopicsForm(forms.ModelForm):
    TOPIC_CHOICES = [[topic.id, topic.name] for topic in Topic.objects.all()]

    topics = forms.MultipleChoiceField(choices=TOPIC_CHOICES, widget=forms.CheckboxSelectMultiple(),
                                       required=True, label='')

    class Meta:
        model = Blog
        fields = [
            'topics',
        ]
        widgets = {'topics': forms.CheckboxSelectMultiple()}

    def clean(self):
        cleaned_data = self.cleaned_data
        if len(cleaned_data['topics']) > 3:
            raise forms.ValidationError('You cannot select more than 3 topics!')
        return cleaned_data


class CaseInsensitiveUserCreationForm(UserCreationForm):
    def clean(self):
        cleaned_data = super(CaseInsensitiveUserCreationForm, self).clean()
        username = cleaned_data.get('username')
        if username and User.objects.filter(username__iexact=username).exists():
            self.add_error('username', 'A user with that username already exists.')
        return cleaned_data


class SearchForm(forms.Form):
    TOPIC_CHOICES = [[topic.id, topic.name] for topic in Topic.objects.all().order_by('name')]

    topics = forms.MultipleChoiceField(choices=TOPIC_CHOICES, widget=forms.CheckboxSelectMultiple(),
                                       required=False)

    ORDER = [['ascending', 'ascending'], ['descending', 'descending']]

    order = forms.ChoiceField(choices=ORDER, required=True, widget=forms.Select())

    BY = [['creation_date', 'creation_date'], ['favourites', 'favourites'], ['name', 'name']]

    by = forms.ChoiceField(choices=BY, required=True, widget=forms.Select(), label='Sort by')

    class Meta:
        fields = [
            'topics',
            'by',
            'order',
        ]
        widgets = {
            'topics': forms.CheckboxSelectMultiple(),
            'order': forms.Select(),
            'by': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
                Div(
                    Div(
                        'topics',
                        css_class='col-6',
                    ),
                    Div(
                        'by',
                        'order',
                        css_class='col-6',
                    ),
                    css_class='row'
                )
        )
        super(SearchForm, self).__init__(*args, **kwargs)
        self.initial['order'] = 'ascending'
        self.initial['by'] = 'creation_date'

