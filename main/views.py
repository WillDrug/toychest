from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
# Create your views here.


def index_view(request):
    return render(request, 'main/index.html')
