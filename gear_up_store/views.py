from urllib.parse import urlparse
from django.shortcuts import render
from core.views import verify_jwt
from django.conf import settings

def home(request):
    # base_url = request.build_absolute_uri()
    settings.CONTEXT_DICT['Home'] = 'Home'

    return render(request,'index.html',settings.CONTEXT_DICT)