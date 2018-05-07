import base64
import hashlib
import time
from django.utils import timezone
from django import forms


class NewLinkForm(forms.Form):
    CHOICES = [('plink', 'Permanent link'),
               ('tlink', '24-hour link'),
               ('olink', 'One-shot link')]

    link = forms.URLField(widget=forms.URLInput(attrs={'class': 'form form-control',
                                                       'placeholder': 'http://'}), label='URL to convert')
    linktype = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(attrs={'class': 'form form-control'}, choices=CHOICES), label='Link type')
    custom_text = forms.CharField(widget=forms.Textarea(attrs={'rows': 1, 'cols': '50', 'maxlength': '50',
                                                                'data-emojiable': 'true', 'name': 'clink',
                                                                'data-emoji-input': 'unicode',
                                                               'class': 'form form-control',
                                                               'placeholder': 'push blue button to the right'}),
                                  label='Custom link emojis', required=False)
