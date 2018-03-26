# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext

from django.http import HttpResponseRedirect
import requests
import urllib, urllib2
import cookielib
import ssl
import pymysql
import json
import datetime
import time

def getpolicy_from_db():
    data = {"time_to_search": "01:50:00", "storage_unit": 1}
    # 先将时间化为时间戳
    a = data['time_to_search']
    a = str(a)
    b = a.split(':')
    s = int(b[0]) * 3600 + int(b[1]) * 60 + int(b[2])
    time_begin = datetime.date.today()
    time_stamp = time.mktime(time_begin.timetuple()) - 86400 + s
    c = int(time_stamp)
    time_to_insert = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(c))
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='managedb', charset='utf8')
    cursor = conn.cursor()
    cursor.execute("select policy  from myapp_nbu_time where time=%s", (time_to_insert))
    policy_dict = cursor.fetchall()
    conn.close()
    print policy_dict

try:
    getpolicy_from_db()
finally:
    print 'aa'