from django.shortcuts import render
from django.http import HttpResponse,request

def home(request):
    return render(request,'home/home.html')
