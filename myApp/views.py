# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Server,Array,Lun
from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def index(request):
    return HttpResponse("hello world!")

def detail(request,num,num2):
    return HttpResponse("detail-%s-%s"%(num,num2))
def server(request):
    #去models里取数据
    serverlist = Server.objects.all()
    #将数据传递給模板，模板渲染页面，然后将渲染好的页面传递给浏览器
    return render(request,'myApp/server.html',{"serer_in_tem":serverlist})
    #传递给模板的是一个字典，字典的key就是html中的输入值，value就是上面我们从model中取回的数据
    pass