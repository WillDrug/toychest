from django.db.utils import IntegrityError
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from emojiurl.forms import NewLinkForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.forms import inlineformset_factory, modelformset_factory
from annoying.decorators import ajax_request
from datetime import datetime, timedelta
from django.utils import timezone
from barnum import gen_data

from emojiurl.forms import NewLinkForm
from emojiurl.codec import to_emoji, from_emoji
from emojiurl.models import Link
from time import time
# Create your views here.
def permanent_link(request, emojis):
    URL = from_emoji(emojis)
    return redirect(URL)

def temp_link(request,emojis):
    link = Link.objects.filter(emoji=emojis).first()
    if link is None:
        return redirect(reverse('emoji_index'))
    to_direct = link.link
    if int(time()) > link.keep_alive:
        link.delete()
    return redirect(to_direct)

def see_help(request):
    return render(request, 'emojiurl/help.html')

def emoji_index(request):
    form = NewLinkForm()
    return render(request, 'emojiurl/index.html', dict(form=form))

def make_link(request):
    form = NewLinkForm(request.POST)
    if form.is_valid():
        if form.cleaned_data['linktype']=='plink':
            link = 'https://' if request.is_secure() else 'http://' + request.get_host() + '/emojiurl/p/' + to_emoji(form.cleaned_data['link'])  # todo except Exception from codec
            return HttpResponse(f'Your link: <a href="{link}">{link}</a>')
        else:
            if form.cleaned_data['custom_text'] == '':
                link = 'https://' if request.is_secure() else 'http://' + request.get_host() + '/emojiurl/' + to_emoji(form.cleaned_data['link'])  # todo except Exception from codec
            else:
                link = 'https://' if request.is_secure() else 'http://' + request.get_host() + '/emojiurl/' +form.cleaned_data['custom_text']
            if form.cleaned_data['linktype'] == 'olink':
                lifetime = int(time() - 1)
            elif form.cleaned_data['linktype'] == 'tlink':
                lifetime = int(time()) + 86400
            else:
                return 'No way, Jose'

            try:
                print(link)
                link_obj = Link.objects.create(link=form.cleaned_data['link'], emoji=form.cleaned_data['custom_text'] if form.cleaned_data['custom_text']!='' else to_emoji(form.cleaned_data['link']), keep_alive=lifetime)
            except IntegrityError as e:
                return HttpResponse(f'<p>That link is already taken, try something else</p>')
            link_obj.save()
            return HttpResponse(f'<p>Your link: <a href="{link}">{link}</a></p>')
    else:
        return HttpResponse(f'<ul>'+['<li>' + q +'</li>' for q in form.errors]+'</ul>')
