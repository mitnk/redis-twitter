import string
from django import forms

class TweetForm(forms.Form):
    text = forms.CharField(label="What Happened", widget=forms.Textarea)

    def clean_text(self):
        text = self.cleaned_data['text'].strip().replace('\n', ' ')
        if not text:
            raise forms.ValidationError("Invalid text")
        elif len(text) > 140:
            raise forms.ValidationError("text too long")
        return text

class RegisterForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if not username:
            raise forms.ValidationError("Invalid username")
        elif len(username) > 16:
            raise forms.ValidationError("User name too long")
        elif not all([x in "%s_%s" % (string.ascii_letters, string.digits) for x in username]):
            raise forms.ValidationError("Only Letters, Numbers and _ are valid")
        return username

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
