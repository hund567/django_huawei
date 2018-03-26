# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import time
import requests
import urllib, urllib2, json
import cookielib
import ssl
import pymysql
import json


# Arrays_list = [['93.1.243.31', '2102350BVB10H8000046', 'admin', 'Admin@storage'],
#                ['93.1.243.25', '2102350HYS10H8000042', 'admin', 'Admin@storage'],
#                ['93.1.243.63', '2102350DJX10G8000002', 'admin', 'Admin@storage'],
#                ['93.1.243.61', '2102350BVB10F6000042', 'admin', 'Admin@storage'],
#                ['93.225.115.54', '2102350BVB10F6000041', 'admin', 'admin@Storage']]

def obtain_his_info():
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='managedb', charset='utf8')
        cursor = conn.cursor()
        cursor.execute(
            "select array_ip,array_id,array_user,array_password from myapp_array_admin")
        arrayinfos = cursor.fetchall()
        cursor.close()
        conn.close()
        Arrays_list = []
        for query in arrayinfos:
            Arrays_list.append(query)
        #
        # Arrays_list = [['93.1.243.31', '2102350BVB10H8000046', 'admin', 'Admin@storage'],
        #                ['93.1.243.25', '2102350HYS10H8000042', 'admin', 'Admin@storage'],
        #                ['93.1.243.63', '2102350DJX10G8000002', 'admin', 'Admin@storage'],
        #                ['93.1.243.61', '2102350BVB10F6000042', 'admin', 'Admin@storage'],
        #                ['93.225.115.54', '2102350BVB10F6000041', 'admin', 'admin@Storage']]
        Arrays_group_dict = {}
        all_info = []
        return Arrays_list

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

        # 将盘机信息并写入数据库
        Array_in_view = {}
        Array_in_view['array_id'] = array_id
        Array_in_view['array_ip'] = array_ip
        Array_in_view['array_name'] = main_info['NAME']
        Array_in_view['location'] = main_info['LOCATION']
        Array_in_view['patchVersion'] = main_info['patchVersion']
        Array_in_view['TOTALCAPACITY'] = int(int(main_info['TOTALCAPACITY']) / 2097152)
        Array_in_view['FREEDISKSCAPACITY'] = int(int(main_info['FREEDISKSCAPACITY']) / 2097152)
        Array_in_view['STORAGEPOOLCAPACITY'] = int(int(main_info['STORAGEPOOLCAPACITY']) / 2097152)
        Array_in_view['STORAGEPOOLFREECAPACITY'] = int(int(main_info['STORAGEPOOLFREECAPACITY']) / 2097152)
        #获取时间戳
        timenow = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())

        conn2 = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='managedb', charset='utf8')
        cursor2 = conn2.cursor()

        cursor2.execute(
            "insert into myapp_array_history(array_id,array_ip,array_name,location,TOTALCAPACITY,FREEDISKSCAPACITY,STORAGEPOOLCAPACITY,STORAGEPOOLFREECAPACITY,DATE) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(Array_in_view['array_id'],Array_in_view['array_ip'],Array_in_view['array_name'],Array_in_view['location'],Array_in_view['TOTALCAPACITY'],Array_in_view['FREEDISKSCAPACITY'],Array_in_view['STORAGEPOOLCAPACITY'],Array_in_view['STORAGEPOOLFREECAPACITY'],timenow))
        conn2.commit()
        cursor2.close()
        conn2.close()

if __name__ == '__main__':
    Arrays_lists=obtain_his_info()
    for each_array in Arrays_lists:
        func(each_array[0], each_array[1], each_array[2], each_array[3])








