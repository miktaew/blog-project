from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.models import User

from blog.models import Blog


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

    def __init__(self, *args, **kwargs):
        super(RawBlogForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        # self.helper.form_id = 'id-blogForm' # or whatever
        # self.helper.form_class = 'formsClass' # or whatever
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save blog'))
