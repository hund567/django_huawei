# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Server,Array,Lun,Array_Admin
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from .array_info_collect import init_excel
from .array_info_collect import func
from .crontab import obtain_his_info
from django.http import HttpResponseRedirect
import requests
import urllib, urllib2
import cookielib
import ssl
import pymysql
import json
import datetime
import time

# Create your views here.
def index(request):
    return HttpResponse("hello world!")

def detail(request,num,num2):
    return HttpResponse("detail-%s-%s"%(num,num2))

def initdb(request):
    #首先清除所有信息
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='managedb', charset='utf8')
    cursor = conn.cursor()

    cursor.execute(
        "delete from myapp_lun")
    cursor.execute(
        "delete from myapp_server")
    cursor.execute(
        "delete from myapp_array")
    conn.commit()
    cursor.close()
    conn.close()

    Arrays_list = []
    for query in Array_Admin.objects.all():
        Arrays_list.append(query)


    # Arrays_list = [['93.1.243.31', '2102350BVB10H8000046', 'admin', 'Admin@storage'],
    #                ['93.1.243.25', '2102350HYS10H8000042', 'admin', 'Admin@storage'],
    #                ['93.1.243.63', '2102350DJX10G8000002', 'admin', 'Admin@storage'],
    #                ['93.1.243.61', '2102350BVB10F6000042', 'admin', 'Admin@storage'],
    #                ['93.225.115.54', '2102350BVB10F6000041', 'admin', 'admin@Storage']]
    Arrays_group_dict = {}
    all_info = []

    def build_uri(urlinput, endpoint):
        return '='.join([urlinput, endpoint])

    def func(array_ip, array_id, array_user, array_passwd):

        url_head = 'https://' + array_ip + ':8088/deviceManager/rest/'
        login_url = url_head + 'xxxxx/login'
        system_url = url_head + array_id + '/system/'
        fc_port_url = url_head + array_id + '/fc_initiator?PARENTID'
        lun_url = url_head + array_id + '/lun/associate?TYPE=11&ASSOCIATEOBJTYPE=21&ASSOCIATEOBJID'
        server_url = url_head + array_id + '/host?range=[0-100]'
        data = {'scope': 0, 'username': array_user, 'password': array_passwd}
        user_agent = r'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'
        context = ssl
        head = {'User-Agent': user_agent, 'Content-Type': 'application/json;charset=UTF-8',
                'Cache-Control': 'max-age=0', 'If-Modified-Since': bytes(0), 'Accept': '*/*',
                'X-Requested-With': 'XMLHttpRequest'}
        # data = {'scope': 0, 'username': 'admin', 'password': 'Admin@storage'}
        cookie = cookielib.CookieJar()
        cookie_support = urllib2.HTTPCookieProcessor(cookie)
        opener = urllib2.build_opener(cookie_support)
        urllib2.install_opener(opener)
        server_list = ['', '', '', []]



        # 登陆并获取cookie中session信息，以备后用
        # 循环开始前先置空cookie
        iBaseToken = ''
        session_info = ''

        req = requests.post(url=login_url, headers=head,
                            json={"scope": 0, "username": array_user, "password": array_passwd}, verify=False)
        print req.status_code
        session_info = requests.utils.dict_from_cookiejar(req.cookies)['session']
        iBaseToken = json.loads(req.text)['data']['iBaseToken']
        head2 = {'User-Agent': user_agent, 'Content-Type': 'application/json;charset=UTF-8',
                 'Cache-Control': 'max-age=0', 'If-Modified-Since': bytes(0), 'Accept': '*/*',
                 'X-Requested-With': 'XMLHttpRequest', 'iBaseToken': iBaseToken}
        cookies = dict(CSRF_IBASE_TOKEN=iBaseToken, DEVICE_ID=array_id, initLogin='true', session=session_info)
        # 获取盘机信息
        req_main = requests.get(url=system_url, headers=head2, verify=False, cookies=cookies)
        main_info = json.loads(req_main.text)['data']

        # 实例化盘机信息并写入数据库
        Array_in_view = Array()
        Array_in_view.array_id = array_id
        Array_in_view.array_ip = array_ip
        Array_in_view.array_name = main_info['NAME']
        Array_in_view.location = main_info['LOCATION']
        Array_in_view.PRODUCTVERSION = main_info['PRODUCTVERSION']
        Array_in_view.patchVersion = main_info['patchVersion']
        Array_in_view.TOTALCAPACITY = int(main_info['TOTALCAPACITY']) / 2097152
        Array_in_view.FREEDISKSCAPACITY = int(main_info['FREEDISKSCAPACITY']) / 2097152
        Array_in_view.STORAGEPOOLCAPACITY = int(main_info['STORAGEPOOLCAPACITY']) / 2097152
        Array_in_view.STORAGEPOOLFREECAPACITY = int(main_info['STORAGEPOOLFREECAPACITY']) / 2097152
        Array_in_view.save()
        # init_excel(main_info['ID'])
        # 获取主机信息 ID IP NAME 生成字符串

        req_server = requests.get(url=server_url, headers=head2, verify=False, cookies=cookies)
        server_info = json.loads(req_server.text)['data']
        server_group = []
        array_list = []

        for item in server_info:
            server_list = ['', '', [], []]
            server_ID = item['ID']
            server_name = item['NAME']
            server_IP = item['IP']
            server_list[0] = server_name
            server_list[1] = server_IP
            # 将提取主机ID并获取相应wwn
            req_fc_port = None
            req_fc_port = requests.get(url=build_uri(fc_port_url, server_ID), headers=head2, verify=False,
                                       cookies=cookies)
            lun_list = []
            lun_info = []
            wwn_info = []
            wwn_list = []
            if 'data' in json.loads(req_fc_port.text):

                wwn_info = json.loads(req_fc_port.text)['data']
                wwn_list = []
                for eachwwn in wwn_info:
                    wwn = eachwwn['ID']
                    wwn_list.append(wwn)

                server_list[2] = wwn_list


            #主机信息入库
            server_in_view = Server()
            server_in_view.array_id = Array_in_view
            server_in_view.server_ID = server_ID
            server_in_view.server_IP = server_IP
            server_in_view.server_name = server_name
            server_in_view.server_wwn = wwn_list
            server_in_view.save()




            # print server_list

            # 根据主机ID获取lun信息

            req_lun = None
            req_lun = requests.get(url=build_uri(lun_url, server_ID), headers=head2, verify=False, cookies=cookies)

            if 'data' in json.loads(req_lun.text):
                lun_info = json.loads(req_lun.text)['data']
                single_lun_list = []

            for each in lun_info:
                single_lun_list = []
                single_lun_list.append(each['ID'])
                single_lun_list.append(each['NAME'])
                single_lun_list.append(each['CAPACITY'])
                single_lun_list.append(each['WWN'])
                lun_list.append(single_lun_list)

                #lun信息入库

                lun_in_view = Lun()
                lun_in_view.server_ID = server_in_view
                lun_in_view.lun_ID = each['ID']
                lun_in_view.lun_NAME = each['NAME']
                lun_in_view.lun_CAPACITY = each['CAPACITY']
                lun_in_view.lun_WWN = each['WWN']
                lun_in_view.save()




            server_list[3] = lun_list
            server_group.append(server_list)
            # print server_group
        # 将盘机ID与上面的server_group做成一个字典
        array_list.append(main_info['NAME'])
        array_list.append(main_info['LOCATION'])
        array_list.append(array_ip)
        array_list.append(main_info['PRODUCTVERSION'])
        array_list.append(main_info['patchVersion'])
        array_list.append(int(main_info['TOTALCAPACITY']) / 2097152)
        array_list.append(int(main_info['FREEDISKSCAPACITY']) / 2097152)
        array_list.append(int(main_info['STORAGEPOOLCAPACITY']) / 2097152)
        array_list.append(int(main_info['STORAGEPOOLFREECAPACITY']) / 2097152)
        array_list.append(server_group)
        Arrays_group_dict[array_id] = array_list

        return Arrays_group_dict


    for each_array in Arrays_list:
        #array_ip, array_id, array_user, array_passwd
        func(each_array.array_ip,each_array.array_id,each_array.array_user,each_array.array_password)

    return HttpResponseRedirect("../array")




def array(request):
    #去models里取数据
    # inirdb()
    serverlist = Server.objects.all()
    lunlist = Lun.objects.all()
    arraylist = Array.objects.all()
    #将数据传递給模板，模板渲染页面，然后将渲染好的页面传递给浏览器
    return render(request,'myApp/array.html',{"server_in_tem":serverlist,"lun_in_tem":lunlist,"array_in_tem":arraylist})
    #传递给模板的是一个字典，字典的key就是html中的输入值，value就是上面我们从model中取回的数据
    pass

def searcharray(request):
    #去models里取数据
    # inirdb()
    #将数据传递給模板，模板渲染页面，然后将渲染好的页面传递给浏览器

    # 传递给模板的是一个字典，字典的key就是html中的输入值，value就是上面我们从model中取回的数据
    return render(request,'myApp/searcharray.html')
    pass

def getjson(request):


    # 处理收集的数据信息　编辑成一条数据
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='managedb', charset='utf8')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT t1.lun_id,t1.lun_NAME,t1.lun_CAPACITY,t1.lun_WWN,t2.server_ID,t2.server_name,t2.server_IP,t2.server_wwn,t3.array_name,t3.location,t3.array_ip,t3.array_id FROM myapp_lun t1,myapp_server t2,myapp_array t3 WHERE t1.server_ID_id = t2.id AND t2.array_id_id = t3.id ")
    effect_lun_row = cursor.fetchall()
    conn.close()
    resdict = {}
    rowlist = []
    for row in effect_lun_row:
        rowdict = {}
        rowdict['id'] = row[0]
        rowdict['lun_NAME'] = row[1]
        rowdict['lun_CAPACITY'] = row[2]/1024/1024/2
        rowdict['lun_WWN'] = row[3]
        rowdict['server_ID'] = row[4]
        rowdict['server_name'] = row[5]
        rowdict['server_IP'] = row[6]
        aa = row[7]
        bb=aa.replace('[u\'','')
        cc=bb.replace('\']','')
        dd=cc.replace("\',",'')
        ee = dd.replace("u\'", '\n')
        rowdict['server_wwn'] = ee
        rowdict['array_name'] = row[8]
        rowdict['location'] = row[9]
        rowdict['array_ip'] = row[10]
        rowdict['array_id'] = row[11]
        rowlist.append(rowdict)
    resdict['total'] = len(rowlist)
    resdict['data'] = rowlist

    # return HttpResponse(resdict.get('total', 'failure'))
    # return HttpResponse(resdict.get('data', 'failure'))

    from django.http import JsonResponse
    return JsonResponse(resdict)

def inputarrayinfo(request):
    return render(request, 'myApp/inputarrayinfo.html')

def submit_array_info(request):

    array_auth_info=json.load(request)

    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='managedb', charset='utf8')
    cursor = conn.cursor()

    cursor.execute(
        "select * from myapp_array_admin where array_ip = %s",(array_auth_info['array_ip']))

    if cursor.rowcount == 0:
        cursor.execute("insert into myapp_array_admin(array_ip,array_user,array_password,array_id) values(%s,%s,%s,%s)",(array_auth_info['array_ip'],array_auth_info['array_user'],array_auth_info['array_password'],array_auth_info['array_id']))
        resp="新增数据成功"
    else:
        cursor.execute("update myapp_array_admin set array_user=%s,array_password = %s ,array_id = %s where array_ip =%s",(array_auth_info['array_user'],array_auth_info['array_password'],array_auth_info['array_id'],array_auth_info['array_ip']))
        resp="更新数据成功"
    conn.commit()
    conn.close()
    return HttpResponse(resp)


#表单导出
def exportexcel(request):
    Arrays_list = obtain_his_info()
    for each_array in Arrays_list:
        Arrays_group_dict = func(each_array[0],each_array[1],each_array[2],each_array[3])
    init_excel(Arrays_group_dict)
    return HttpResponseRedirect("../array")


def nbuview(request):
   conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='managedb', charset='utf8')
   cursor = conn.cursor()
   #日表生成
   cursor.execute("select distinct storage_unit from myapp_nbu_jobinfo")
   tuple_of_storage_unit = cursor.fetchall()
   datedict = {}
   valuedict = {}
   datedict_weekly = {}
   valuedict_weekly = {}
   datedict_monthly = {}
   valuedict_monthly = {}

   for each_unit in tuple_of_storage_unit:
       if each_unit[0] != ' ':
           cursor.execute("select * from myapp_nbu_daily where storage_unit = %s",(each_unit[0]))
           count_today = cursor.fetchall()
           list_daily = []
           dateList = []
           valueList = []
           for each in count_today:
               list = []
               a = each[0].strftime("%H:%M:%S")
               list.append(a)
               list.append(each[1])
               list_daily.append(list)
               dateList.append(a)
               valueList.append(each[1])
               b=each_unit[0].encode('utf-8')
           datedict[b] = dateList
           valuedict[b] = valueList
        #获取磁带库与storage_unit关系

   cursor.execute("select * from myapp_nbu_library")
   library_dict={}
   L = cursor.fetchall()
   for each in L:
       m = each[1].encode('utf-8')
       library_dict[m] = each[0].encode('utf-8')

   return render(request, 'myApp/nbuview.html',{"dateList":datedict,"valueList":valuedict,"dateList_weekly":datedict_weekly,"valueList_weekly":valuedict_weekly,"dateList_monthly":datedict_monthly,"valueList_monthly":valuedict_monthly,"library_dict":library_dict})





def nbuview_weekly(request):
   conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='managedb', charset='utf8')
   cursor = conn.cursor()
   cursor.execute("select distinct storage_unit from myapp_nbu_jobinfo")
   tuple_of_storage_unit = cursor.fetchall()
   datedict_weekly = {}
   valuedict_weekly = {}
   for each_unit in tuple_of_storage_unit:
       if each_unit[0] != ' ':
        #周报生成
           time_begin = datetime.date.today()
           time_stamp = time.mktime(time_begin.timetuple()) - 604800
           time_to_insert = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time_stamp))
           cursor.execute("select * from myapp_nbu_week_all WHERE  time >= %s and storage_unit = %s",(time_to_insert,each_unit[0]))
           count_week = cursor.fetchall()
           list_weekly = []
           dateList_weekly = []
           valueList_weekly = []
           for each in count_week:
               list = []
               a = each[0].strftime("%Y/%m/%d \n %H:%M:%S")
               list.append(a)
               list.append(each[1])
               list_weekly.append(list)
               dateList_weekly.append(a)
               valueList_weekly.append(each[1])
               b = each_unit[0].encode('utf-8')

           datedict_weekly[b] = dateList_weekly
           valuedict_weekly[b] = valueList_weekly

        #获取磁带库与storage_unit关系

   cursor.execute("select * from myapp_nbu_library")
   library_dict={}
   L = cursor.fetchall()
   for each in L:
       m = each[1].encode('utf-8')
       library_dict[m] = each[0].encode('utf-8')

   return render(request, 'myApp/nbuview_weekly.html',{"dateList_weekly":datedict_weekly,"valueList_weekly":valuedict_weekly,"library_dict":library_dict})


def nbuview_monthly(request):
   conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='managedb', charset='utf8')
   cursor = conn.cursor()
   cursor.execute("select distinct storage_unit from myapp_nbu_jobinfo")
   tuple_of_storage_unit = cursor.fetchall()
   datedict_monthly = {}
   valuedict_monthly = {}

   for each_unit in tuple_of_storage_unit:
       if each_unit[0] != ' ':
        #月表生成
           time_begin = datetime.date.today()
           time_stamp = time.mktime(time_begin.timetuple()) - 259200
           time_to_insert = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time_stamp))
           cursor.execute("select * from myapp_nbu_monthly where time > %s and storage_unit = %s",(time_to_insert,each_unit[0]))
           count_today = cursor.fetchall()
           list_monthly = []
           dateList_monthly = []
           valueList_monthly = []
           for each in count_today:
               list = []
               a = each[0].strftime("%Y/%m/%d")
               list.append(a)
               list.append(each[1])
               list_monthly.append(list)
               dateList_monthly.append(a)
               valueList_monthly.append(each[1])
               b = each_unit[0].encode('utf-8')
           datedict_monthly[b] = dateList_monthly
           valuedict_monthly[b] = valueList_monthly


        #获取磁带库与storage_unit关系

   cursor.execute("select * from myapp_nbu_library")
   library_dict={}
   L = cursor.fetchall()
   for each in L:
       m = each[1].encode('utf-8')
       library_dict[m] = each[0].encode('utf-8')

   return render(request, 'myApp/nbuview_monthly.html',{"dateList_monthly":datedict_monthly,"valueList_monthly":valuedict_monthly,"library_dict":library_dict})
def getecharts(request,postinfo):
    #先拼接时间
    time_begin = datetime.date.today()
    time_stamp = time.mktime(time_begin.timetuple()) - 86400 + time.mktime(postinfo[0].timetuple())
    time_to_insert = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time_stamp))
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='managedb', charset='utf8')
    cursor = conn.cursor()
    # 查询数据
    cursor.execute("select policy from myapp_nbu_jobinfo WHERE storage_unit=%s and start_time <= %s and end_time >= %s",(postinfo[1],time_to_insert,time_to_insert))
    lists_of_policys = cursor.fetchall()

    return render(request, 'myApp/nbuview.html',{"lists_of_policys":lists_of_policys})

def getpolicy_from_db(request):
    #先把时间串拼起来
    data = json.load(request)
    #先将时间化为时间戳
    a= data['time_to_search']
    a= str(a)
    b = a.split(':')
    s = int(b[0])*3600 + int(b[1])*60 + int(b[2])
    time_begin = datetime.date.today()
    time_stamp = time.mktime(time_begin.timetuple()) - 86400*3 + s #这里别忘了后期改一下
    c = int(time_stamp)
    time_to_insert = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(c))
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='managedb', charset='utf8')
    cursor = conn.cursor()
    cursor.execute("select policy  from myapp_nbu_time where time=%s and storage_unit=%s",(time_to_insert,data['storage_unit']))
    policy_dict = cursor.fetchall()
    conn.close()

    from django.http import JsonResponse
    return JsonResponse(policy_dict,safe=False)