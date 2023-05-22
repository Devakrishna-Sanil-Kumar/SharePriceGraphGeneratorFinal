from django.shortcuts import render, redirect
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io
import urllib, base64
from django.contrib import messages
from fsdprojapp.models import User

# Create your views here.

user = ''
password = ''

def index(request):
    response = render(request, 'index.html')
    return response

def signin(request):
    global user, password
    user = request.POST.get('username')
    password = request.POST.get('password')
    if user == '' or password == '':
        messages.error(request, 'Please enter username and password.')
        return render(request, 'index.html')
    if User.objects.filter(user=user, password=password).exists():
        response = redirect('/home')
        return response
    else:
        messages.error(request, 'Invalid username or password.')
        return render(request, 'index.html')

def gotosignup(request):
    response = render(request, 'signup.html')
    return response

def logout(request):
    response = render(request, 'index.html')
    return response

def deleteaccount(request):
    global user, password
    if User.objects.filter(user=user, password=password).exists():
        user = User.objects.filter(user=user, password=password)
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return render(request, 'index.html')
    else:
        messages.error(request, 'Invalid username or password.')
        return redirect(request.META['HTTP_REFERER'])

def signup(request):
    global user, password
    user = request.POST.get('username')
    password = request.POST.get('password')
    if user == '' or password == '':
        messages.error(request, 'Please enter username and password.')
        return render(request, 'signup.html')
    if User.objects.filter(user=user).exists():
        messages.error(request, 'Username already exists.')
        return render(request, 'signup.html')
    else:
        user = User(user=user, password=password)
        user.save()
        messages.success(request, 'User created successfully.')
        return render(request, 'index.html')

def home(request):
    response = render(request, 'home.html')
    return response

def getgraph(request):
    share = request.POST.get('share_name')
    numofdays = int(request.POST.get('numberofdays'))
    if numofdays < 2:
        messages.error(request, 'Number of days should be greater than 1')
        return render(request, 'index.html')
    end_date = datetime.today()
    start_date = end_date - timedelta(days=numofdays)
    data = yf.download(share, start_date , end_date)
    if data.empty:
        messages.error(request, 'Please enter a valid ticker.')
        return render(request, 'index.html')
    plt.plot(data['Close'], color = "black", label=f"Share Price")
    plt.title(f"{share} Share Price")
    plt.xlabel("Time")
    plt.ylabel(f"{share} Share Price")
    plt.legend()
    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    html = '<img src = "{}" style = "width: 40%; height: auto;"/>'.format(uri)
    content = {'graph': html}
    plt.close()
    return render(request, 'displayplot.html', content)