from os import error
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from urllib.parse import urlparse
import requests
from rest_framework_simplejwt.tokens import RefreshToken

def get_url(base_url):
    parsed_url = urlparse(base_url)

    url = parsed_url.scheme + '://' + parsed_url.netloc

    return url

def verify_jwt(base_url,token):
    context={}
    url = get_url(base_url) + '/auth/jwt/verify/'
    response = requests.post(url,data={'token' : token})
    if response.status_code == status.HTTP_200_OK:
        context['login'] = 'login'
    else:
        return redirect('login')
    return context

# def logout(request):
#     if request.method == 'POST':
#         refresh_token = request.POST.get('refresh_token')

#         if not refresh_token:
#             return render(request, 'logout.html', {'message': 'Refresh token not provided'})

#         try:
#             token = RefreshToken(refresh_token)
#             token.blacklist()
#             return render(request, 'logout.html', {'message': 'Logout successful'})
#         except Exception as e:
#             return render(request, 'logout.html', {'message': str(e)})

#     return render(request, 'logout.html')

def login(request):

    base_url = request.build_absolute_uri()

    url = get_url(base_url) + '/auth/jwt/create/'

    context = {}

    if request.method =="POST":

        data = {
            'username' : request.POST['username'],
            'password' : request.POST['password']
        }

        if not data['username'] or not data['password']:
            return render(request,'index.html',{'error':'Username and password required'})

        user = authenticate(username=data['username'], password=data['password'])
        if user is not None:
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)
            return render(request, 'index.html', {'logged':'valid credentials'})
        else:
            return render(request, 'index.html', {'error': 'Invalid credentials'})

        # response = requests.post(url, data=data)
        # if response.status_code == status.HTTP_200_OK:
        #     context = verify_jwt(base_url,response.json()['access'])
        #     if not context:
        #         return redirect('login')
        #     elif context['login'] == 'login':
        #         settings.CONTEXT_DICT['login'] = 'login'
        #         return redirect('home')
        #     else:
        #         return redirect('login')
        # else :
        #     return redirect('login')
    
    return render(request, 'index.html')

def user_register(request):
    base_url = request.build_absolute_uri()

    url_user = get_url(base_url) + '/auth/users/'
    url_customer = get_url(base_url) + '/store/customers/'

    if request.method == "POST":

        data = {
            'username' : request.POST['username'],
            'password' : request.POST['password'],
            'email' : request.POST['email'],
            'first_name' : request.POST['first_name'],
            'last_name' : request.POST['last_name'],
        }

        data_cust = {
            'phone' : request.POST['phone'],
            'birth_date' : request.POST['birth_date']
        }

        headers = {'Content-Type': 'application/json'}

        response = requests.post(url_user ,data=data,headers=headers)

        if response.status_code == status.HTTP_201_CREATED:
            try:
                user_data = response.json()
                print(user_data)
            except error:
                print(error)
            data_customer = {
                'user' : user_data.get('id'),
                'phone' : data_cust['phone'],
                'birth_date' : data_cust['birth_date']
            }

            response = requests.post(url_customer ,data=data_customer,headers=headers)

            return redirect('login')
    
    return render(request, 'register.html')

