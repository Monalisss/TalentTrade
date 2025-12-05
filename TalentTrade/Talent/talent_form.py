from django.forms import (
CharField, DateField,
Form, Textarea, ModelForm)

from Talent.models import TalentsPost, Categories, UserAccount


class TalentForm(ModelForm):
    class Meta:
        model = TalentsPost
        fields= '__all__'

class UserAccountForm(ModelForm):
    class Meta:
        model = UserAccount
        fields = ['bio', 'phone_number', 'photo']
        widgets = {
            'bio': Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'phone_number':Textarea(attrs={
                'placeholder': '0744 123 456'
            }),
        }