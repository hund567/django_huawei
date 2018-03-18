# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from models import Server,Array,Lun
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext

import requests
import urllib, urllib2, json
import cookielib
import ssl
import pymysql
import sys,shelve
import json

def func():
    list1=[]
    querys = (x for x in Array.objects.all())
    for query in querys:
        print query

try:
    func()
finally:
    print "a"