# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Server,Array,Lun
from django.shortcuts import render
from django.http import HttpResponse

import requests
import urllib, urllib2, json
import cookielib
import ssl

# Create your views here.
def index(request):
    return HttpResponse("hello world!")

def detail(request,num,num2):
    return HttpResponse("detail-%s-%s"%(num,num2))

def inirdb():
    Arrays_list = [['93.1.243.31', '2102350BVB10H8000046', 'admin', 'Admin@storage'],
                   ['93.1.243.25', '2102350HYS10H8000042', 'admin', 'Admin@storage'],
                   ['93.1.243.63', '2102350DJX10G8000002', 'admin', 'Admin@storage'],
                   ['93.1.243.63', '2102350DJX10G8000002', 'admin', 'Admin@storage'],
                   ['93.1.243.61', '2102350BVB10F6000042', 'admin', 'Admin@storage'],
                   ['93.225.115.54', '2102350BVB10F6000041', 'admin', 'admin@Storage']]
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
            server_in_view.array_id = array_id
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
                lun_in_view.server_ID = server_ID
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
        func(each_array[0],each_array[1],each_array[2],each_array[3])
    return






def server(request):
    #去models里取数据
    inirdb()
    serverlist = Server.objects.all()
    lunlist = Lun.objects.all()
    #将数据传递給模板，模板渲染页面，然后将渲染好的页面传递给浏览器
    return render(request,'myApp/server.html',{"serer_in_tem":serverlist},{"lun_in_tem":lunlist})
    #传递给模板的是一个字典，字典的key就是html中的输入值，value就是上面我们从model中取回的数据
    pass
