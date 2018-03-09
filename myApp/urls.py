# -*- coding: utf-8 -*-
from django.conf.urls import url,include
from . import views

# '^$' 表示以什么都没有开头，以什么都没有结束 ^x 表示以x开头 y$表示以y结尾
urlpatterns = [
    url(r'^$',views.index),

#这里加小括号的的意思是接受小括号里面的值  表示的是以数字开头 以/结尾的一段字符串 如果没有小括号，参数就无法传递到detail这个函数当中
#小括号是正则当中组的概念
    url(r'^(\d+)/(\d+)/$',views.detail),
    url(r'^server/$',views.server)
]