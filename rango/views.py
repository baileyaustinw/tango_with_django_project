from django.shortcuts import render
from django.http import HttpResponse
from tango_with_django_project.settings import MEDIA_URL

def index(request):
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!',
                    'MEDIA_URL': MEDIA_URL}

    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    context_dict = {
        'boldmessage': 'This tutorial has been put together by Austin Bailey',
        'MEDIA_URL': MEDIA_URL
    }

    return render(request, 'rango/about.html', context=context_dict)